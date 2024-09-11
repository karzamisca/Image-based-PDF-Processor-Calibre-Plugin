from calibre.gui2.actions import InterfaceAction #Built-in for Calibre 7.17
from PIL import Image #v10.4.0 
import os #Built-in for Python 3.12.6
import zipfile #Built-in for Python 3.12.6
import tempfile #Built-in for Python 3.12.6
import shutil #Built-in for Python 3.12.6
import re #Built-in for Python 3.12.6

class InterfacePlugin(InterfaceAction):
    name = 'Image-based PDF Processor Calibre Plugin'

    action_spec = ('Image-based PDF Processor Calibre Plugin', None, 'Convert PDF to images and text', 'Ctrl+Shift+I')

    def genesis(self):
        '''Initial setup for the plugin.'''
        icon = get_icons('images/icon.png', 'Image-based PDF Processor Calibre Plugin')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        '''Show the main UI dialog for PDF conversion.'''
        from calibre_plugins.image_based_pdf_processor.ui import PDFConverterDialog
        d = PDFConverterDialog(self.gui, self.qaction.icon(), self)
        d.show()

    def extract_tesseract(self):
        '''Extract Tesseract from the plugin zip file to a temporary directory.'''
        try:
            # Create a temporary directory to extract Tesseract
            temp_dir = tempfile.mkdtemp()

            # Get the path of the plugin zip file
            plugin_zip_path = os.path.join(os.path.dirname(__file__))

            # Extract the Tesseract folder from the zip file
            with zipfile.ZipFile(plugin_zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.startswith('Tesseract-OCR/'):
                        zip_ref.extract(file, temp_dir)

            # Return the path to the extracted Tesseract directory
            tesseract_dir = os.path.join(temp_dir, 'Tesseract-OCR')
            return tesseract_dir
        except Exception as e:
            return f'Error during Tesseract extraction: {e}'

    def convert_pdf_to_images(self, pdf_path, output_folder):
        '''Convert PDF to images, split double-page images, and save them in a structured folder.'''
        try:
           with self.interface_action_base_plugin: 
            from pdf2image import convert_from_path #v1.17.0
            # Poppler path configuration
            poppler_path = get_resources('poppler-24.07.0/Library/bin')

            # Create the output folder named after the input file (without extension)
            input_file_name = os.path.splitext(os.path.basename(pdf_path))[0]
            image_output_folder = os.path.join(output_folder, input_file_name, 'img')

            os.makedirs(image_output_folder, exist_ok=True)

            images = convert_from_path(pdf_path, poppler_path=poppler_path)

            # Keep only even pages and the first and last pages
            total_pages = len(images)
            filtered_images = [images[0]]  # Always keep the first page

            for i in range(1, total_pages - 1):
                if i % 2 == 0:  # Keep only even pages
                    filtered_images.append(images[i])

            if total_pages > 1:
                filtered_images.append(images[-1])  # Always keep the last page

            # Split the double-page images and save the individual pages
            page_counter = 1
            for image in filtered_images:
                # Get image size (width, height)
                width, height = image.size

                # Split the image vertically into two parts
                left_page = image.crop((0, 0, width // 2, height))  # Left half of the image
                right_page = image.crop((width // 2, 0, width, height))  # Right half of the image

                # Save the left page
                left_image_path = os.path.join(image_output_folder, f'page_{page_counter}.png')
                left_page.save(left_image_path, 'PNG')
                page_counter += 1

                # Save the right page
                right_image_path = os.path.join(image_output_folder, f'page_{page_counter}.png')
                right_page.save(right_image_path, 'PNG')
                page_counter += 1

            # Extract Tesseract and perform OCR on the images
            tesseract_dir = self.extract_tesseract()
            ocr_result = self.perform_ocr_on_images(image_output_folder, tesseract_dir)

            # Clean up temporary Tesseract directory
            shutil.rmtree(tesseract_dir)

            # Divide text into chapters after all OCR text files are created
            chapter_result = self.divide_text_into_chapters(os.path.join(output_folder, input_file_name, '_ocr'))

            return f'Conversion successful! {page_counter - 1} images saved in: {image_output_folder}. {ocr_result}. {chapter_result}'
        except Exception as e:
            return f'Error during conversion: {e}'

    def perform_ocr_on_images(self, image_output_folder, tesseract_dir):
        '''Perform OCR on images in the folder and save the text results.'''
        try:
           with self.interface_action_base_plugin: 
            import pytesseract #v0.3.13
            # Specify the path to tesseract executable inside the extracted folder
            pytesseract.pytesseract.tesseract_cmd = os.path.join(tesseract_dir, 'tesseract.exe')

            # Set the OCR text output folder next to the image folder
            ocr_output_folder = os.path.join(os.path.dirname(image_output_folder), '_ocr')
            os.makedirs(ocr_output_folder, exist_ok=True)

            # Iterate over the images in the folder
            for image_file in os.listdir(image_output_folder):
                if image_file.endswith('.png'):
                    image_path = os.path.join(image_output_folder, image_file)

                    # Perform OCR on the image
                    ocr_text = pytesseract.image_to_string(Image.open(image_path))

                    # Save the OCR text to a file
                    text_file_path = os.path.join(ocr_output_folder, f'{os.path.splitext(image_file)[0]}.txt')
                    with open(text_file_path, 'w', encoding='utf-8') as text_file:
                        text_file.write(ocr_text)

            return f'OCR completed! Text saved in: {ocr_output_folder}'
        except Exception as e:
            return f'Error during OCR: {e}'

    def divide_text_into_chapters(self, ocr_output_folder):
        '''Find chapter headings in OCR text files and divide the text into chapters.'''
        try:
            # Define a pattern for identifying chapter headings
            chapter_heading_pattern = re.compile(r'^\bChapter\b\s+\d+', re.IGNORECASE)

            # Collect headings and their corresponding text files
            chapter_headings = []

            for text_file in sorted(os.listdir(ocr_output_folder)):
                if text_file.endswith('.txt'):
                    file_path = os.path.join(ocr_output_folder, text_file)
                    
                    # Read the content of the OCR text file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()

                    # Split content into lines and consider only the first 5 lines for heading detection
                    lines = content.split('\n')
                    heading_lines = lines[:5]

                    # Find all chapter headings and their positions
                    for i, line in enumerate(heading_lines):
                        match = chapter_heading_pattern.match(line.strip())
                        if match:
                            chapter_number = re.search(r'\d+', match.group()).group()
                            chapter_headings.append((file_path, i, chapter_number))

            if chapter_headings:
                # Create chapters based on detected headings
                chapters_folder = os.path.join(os.path.dirname(ocr_output_folder), 'chapters')
                os.makedirs(chapters_folder, exist_ok=True)

                for i, (start_file_path, start_line, chapter_number) in enumerate(chapter_headings):
                    start_page = start_file_path
                    if i + 1 < len(chapter_headings):
                        end_file_path = chapter_headings[i + 1][0]
                    else:
                        end_file_path = None
                    
                    chapter_text = self.extract_chapter_text(start_file_path, start_line, end_file_path)
                    
                    # Save the chapter text to a new file
                    chapter_file_path = os.path.join(chapters_folder, f'Chapter_{chapter_number}.txt')
                    with open(chapter_file_path, 'w', encoding='utf-8') as chapter_file:
                        chapter_file.write(chapter_text)

                return f'Chapters divided and saved in: {chapters_folder}'
            return 'No chapter headings found in the OCR text files.'
        except Exception as e:
            return f'Error during chapter division: {e}'

    def extract_chapter_text(self, start_file_path, start_line, end_file_path):
        '''Extract text for a chapter from start to end file.'''
        chapter_text = []
        
        # Extract text from the start file
        with open(start_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            chapter_text.extend(lines[start_line:])

        # Extract text from the intermediate files if any
        current_file_path = start_file_path
        while current_file_path != end_file_path:
            next_file_path = self.get_next_file_path(current_file_path)
            if next_file_path is None:
                break
            with open(next_file_path, 'r', encoding='utf-8') as file:
                chapter_text.extend(file.readlines())
            current_file_path = next_file_path

        # Extract text from the end file, if exists
        if end_file_path:
            with open(end_file_path, 'r', encoding='utf-8') as file:
                chapter_text.extend(file.readlines())

        return ''.join(chapter_text)

    def get_next_file_path(self, current_file_path):
        '''Get the next text file path in the directory.'''
        files = sorted([f for f in os.listdir(os.path.dirname(current_file_path)) if f.endswith('.txt')])
        current_index = files.index(os.path.basename(current_file_path))
        if current_index + 1 < len(files):
            return os.path.join(os.path.dirname(current_file_path), files[current_index + 1])
        return None
