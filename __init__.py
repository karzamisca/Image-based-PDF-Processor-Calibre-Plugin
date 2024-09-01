from calibre.customize import InterfaceActionBase

class InterfacePluginDemo(InterfaceActionBase):
    '''
    The actual interface plugin class is defined in main.py.
    '''
    name = 'PDF to Image Converter Plugin'
    description = 'Convert PDF pages to images with poppler support'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Your Name'
    version = (1, 0, 0)
    minimum_calibre_version = (0, 7, 53)

    # Point to the actual plugin class
    actual_plugin = 'calibre_plugins.pdf_to_image.main:InterfacePlugin'

    def is_customizable(self):
        '''Enable customization via Preferences -> Plugins'''
        return True

    def config_widget(self):
        '''Returns the configuration dialog widget.'''
        from calibre_plugins.pdf_to_image.ui import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        '''Save settings specified by the user in the config widget.'''
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
