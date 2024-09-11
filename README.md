### Image-based PDF Processor Calibre Plugin

### 1. **__init__.py**

#### **Class: InterfacePluginDemo**
- **Purpose:** This is the interface plugin class that interacts with Calibre. It specifies the plugin's name, description, version, and which platforms it supports. It also points to the actual plugin class in `main.py` and provides customization features.

#### **Functions:**
- **`is_customizable(self):`** 
  - Returns `True` to enable customization via Calibre’s Preferences -> Plugins menu.
  
- **`config_widget(self):`** 
  - Returns the configuration widget used for customization.
  
- **`save_settings(self, config_widget):`** 
  - Saves settings specified by the user in the configuration widget.

### 2. **main.py**

#### **Class: InterfacePlugin**
- **Purpose:** This is the core class that handles the conversion of PDF files into images and text using poppler and Tesseract-OCR. It also manages the extraction of Tesseract, splitting double-page images, performing OCR, and dividing text into chapters.

#### **Functions:**
- **`genesis(self):`** 
  - Initializes the plugin by setting up the action icon and connecting the action to the UI dialog.

- **`show_dialog(self):`** 
  - Displays the main UI dialog for PDF conversion.

- **`extract_tesseract(self):`** 
  - Extracts Tesseract-OCR from the plugin zip file into a temporary directory and returns the path to the extracted Tesseract directory.

- **`convert_pdf_to_images(self, pdf_path, output_folder):`** 
  - Converts the given PDF to images, splits double-page images, performs OCR, and divides text into chapters. It saves the images and text in a structured output folder.

- **`perform_ocr_on_images(self, image_output_folder, tesseract_dir):`** 
  - Uses Tesseract-OCR to perform OCR on the images in the specified folder and saves the extracted text to text files.

- **`divide_text_into_chapters(self, ocr_output_folder):`** 
  - Identifies chapter headings in the OCR text files and divides the text into chapters based on those headings.

- **`extract_chapter_text(self, start_file_path, start_line, end_file_path):`** 
  - Extracts text for a chapter starting from the given file and line until the next chapter heading (or the end of the file).

- **`get_next_file_path(self, current_file_path):`** 
  - Returns the next text file path in the directory, allowing for sequential processing of text files when dividing chapters.

### 3. **ui.py**

#### **Class: PDFConverterDialog**
- **Purpose:** This class creates the user interface for selecting the input PDF file and output folder, and it allows the user to initiate the PDF conversion process.

#### **Functions:**
- **`__init__(self, gui, icon, plugin):`** 
  - Initializes the dialog, sets up the layout, and creates the input/output file selection and conversion buttons.

- **`select_pdf_file(self):`** 
  - Opens a file dialog for selecting the input PDF file and updates the corresponding text field.

- **`select_output_folder(self):`** 
  - Opens a folder selection dialog for selecting the output folder and updates the corresponding text field.

- **`convert_pdf_to_images(self):`** 
  - Calls the `convert_pdf_to_images` method from the `InterfacePlugin` class to start the PDF conversion process. It displays the result message in the status label.

---

### Summary of Components:

- **InterfacePluginDemo (in `__init__.py`):**
  - Handles plugin configuration and customization in Calibre.
  
- **InterfacePlugin (in `main.py`):**
  - Main plugin logic for converting PDFs to images, performing OCR, and dividing text into chapters.
  
- **PDFConverterDialog (in `ui.py`):**
  - Provides the graphical user interface (GUI) for the plugin, allowing users to select files, start the conversion, and display status messages.
