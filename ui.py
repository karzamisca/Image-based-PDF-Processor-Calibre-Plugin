from qt.core import QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog, QLineEdit

class PDFConverterDialog(QDialog):
    '''Main dialog for the Image-based PDF Processor plugin.'''

    def __init__(self, gui, icon, plugin):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.plugin = plugin  # Store the plugin instance
        self.setWindowIcon(icon)
        self.setWindowTitle('Image-based PDF Processor')

        # Layout
        self.layout = QVBoxLayout(self)
        
        # Input file selection
        self.inputPathEdit = QLineEdit(self)
        self.inputPathEdit.setPlaceholderText('Select PDF file...')
        self.layout.addWidget(self.inputPathEdit)

        self.selectInputButton = QPushButton('Select PDF File', self)
        self.selectInputButton.clicked.connect(self.select_pdf_file)
        self.layout.addWidget(self.selectInputButton)

        # Output folder selection
        self.outputPathEdit = QLineEdit(self)
        self.outputPathEdit.setPlaceholderText('Select output folder...')
        self.layout.addWidget(self.outputPathEdit)

        self.selectOutputButton = QPushButton('Select Output Folder', self)
        self.selectOutputButton.clicked.connect(self.select_output_folder)
        self.layout.addWidget(self.selectOutputButton)

        # Convert button
        self.convertButton = QPushButton('Start Processing', self)
        self.convertButton.clicked.connect(self.convert_pdf_to_images)
        self.layout.addWidget(self.convertButton)

        # Status label
        self.statusLabel = QLabel('', self)
        self.layout.addWidget(self.statusLabel)

    def select_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select PDF File', '', 'PDF Files (*.pdf)')
        if file_path:
            self.inputPathEdit.setText(file_path)

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if folder_path:
            self.outputPathEdit.setText(folder_path)

    def convert_pdf_to_images(self):
        pdf_path = self.inputPathEdit.text()
        output_folder = self.outputPathEdit.text()

        if not pdf_path or not output_folder:
            self.statusLabel.setText('Please select both input and output paths.')
            return

        # Use the existing plugin instance to call the conversion method
        result_message = self.plugin.convert_pdf_to_images(pdf_path, output_folder)
        self.statusLabel.setText(result_message)
