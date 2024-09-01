from calibre.gui2.actions import InterfaceAction
from PIL import Image
import os
import zipfile
import tempfile
import shutil

class InterfacePlugin(InterfaceAction):
    name = 'PDF to Image Converter'

    action_spec = ('PDF to Image Converter', None, 'Convert PDF to images', 'Ctrl+Shift+I')

    def genesis(self):
        '''Initial setup for the plugin.'''
        icon = get_icons('images/icon.png', 'PDF to Image Converter Plugin')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        '''Show the main UI dialog for PDF conversion.'''
        from calibre_plugins.pdf_to_image.ui import PDFConverterDialog
        d = PDFConverterDialog(self.gui, self.qaction.icon(), self)
        d.show()

    def extract_tesseract(self):
        '''Extract Tesseract from the plugin zip file to a temporary directory.'''
        try:
            # Create a temporary directory to extract Tesseract
            temp_dir = tempfile.mkdtemp()

            # Get the path of the plugin zip file
            plugin_zip_path = os.path.join(os.path.dirname(__file__), 'PDF to Image Converter Plugin.zip')

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
       with self.interface_action_base_plugin: 
        from pdf2image import convert_from_path
        '''Convert PDF to images, split double-page images, and save them in a structured folder.'''
        try:
            poppler_path = get_resources('poppler-24.07.0/Library/bin')

            # Create the output folder named after the input file (without extension)
            input_file_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_folder = os.path.join(output_folder, input_file_name, 'img')

            os.makedirs(output_folder, exist_ok=True)

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
                left_image_path = os.path.join(output_folder, f'page_{page_counter}.png')
                left_page.save(left_image_path, 'PNG')
                page_counter += 1

                # Save the right page
                right_image_path = os.path.join(output_folder, f'page_{page_counter}.png')
                right_page.save(right_image_path, 'PNG')
                page_counter += 1

            # Extract Tesseract and perform OCR on the images
            tesseract_dir = self.extract_tesseract()
            ocr_result = self.perform_ocr_on_images(output_folder, tesseract_dir)

            # Clean up temporary Tesseract directory
            shutil.rmtree(tesseract_dir)

            return f'Conversion successful! {page_counter - 1} images saved in: {output_folder}. {ocr_result}'
        except Exception as e:
            return f'Error during conversion: {e}'

    def perform_ocr_on_images(self, image_folder, tesseract_dir):
       with self.interface_action_base_plugin: 
        import pytesseract
        '''Perform OCR on images in the folder and save the text results.'''
        try:
            # Specify the path to tesseract executable inside the extracted folder
            pytesseract.pytesseract.tesseract_cmd = os.path.join(tesseract_dir, 'tesseract.exe')

            text_output_folder = os.path.join(image_folder, 'ocr_text')
            os.makedirs(text_output_folder, exist_ok=True)

            # Iterate over the images in the folder
            for image_file in os.listdir(image_folder):
                if image_file.endswith('.png'):
                    image_path = os.path.join(image_folder, image_file)

                    # Perform OCR on the image
                    ocr_text = pytesseract.image_to_string(Image.open(image_path))

                    # Save the OCR text to a file
                    text_file_path = os.path.join(text_output_folder, f'{os.path.splitext(image_file)[0]}.txt')
                    with open(text_file_path, 'w', encoding='utf-8') as text_file:
                        text_file.write(ocr_text)

            return f'OCR completed! Text saved in: {text_output_folder}'
        except Exception as e:
            return f'Error during OCR: {e}'
