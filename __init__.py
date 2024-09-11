from calibre.customize import InterfaceActionBase #Built-in for Calibre 7.17

class InterfacePluginDemo(InterfaceActionBase):
    '''
    The actual interface plugin class is defined in main.py.
    '''
    name = 'Image-based PDF Processor Calibre Plugin'
    description = 'Convert PDF pages to images and text with poppler and Tesseract-OCR'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Hoàng Minh Quân'
    version = (1, 0, 0)
    minimum_calibre_version = (0, 7, 53)

    # Point to the actual plugin class
    actual_plugin = 'calibre_plugins.image_based_pdf_processor.main:InterfacePlugin'

    def is_customizable(self):
        '''Enable customization via Preferences -> Plugins'''
        return True

    def config_widget(self):
        '''Returns the configuration dialog widget.'''
        from calibre_plugins.image_based_pdf_processor.ui import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        '''Save settings specified by the user in the config widget.'''
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
