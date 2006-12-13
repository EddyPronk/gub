import toolpackage

class Imagemagick (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (mirror='ftp://ftp.nluug.nl/pub/ImageMagick/ImageMagick-%(version)s-1.tar.bz2',
                   version='6.3.1')
    def license_file (self):
        return '%(srcdir)s/LICENSE'
