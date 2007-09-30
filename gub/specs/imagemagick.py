from gub import toolsbuild

class Imagemagick (toolsbuild.ToolsBuild):
    def __init__ (self, settings):
        toolsbuild.ToolsBuild.__init__ (self, settings)
        self.with_template (mirror='ftp://ftp.nluug.nl/pub/ImageMagick/ImageMagick-%(version)s-1.tar.bz2',
                   version='6.3.1')
    def license_file (self):
        return '%(srcdir)s/LICENSE'
