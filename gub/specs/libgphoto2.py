from gub import targetpackage
sf = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'
sf_gphoto = 'http://surfnet.dl.sourceforge.net/sourceforge/gphoto/%(name)s-%(ball_version)s.tar.%(format)s'

class Libgphoto2 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='2.1.6', mirror=sf_gphoto)
    def get_build_dependencies (self):
        return ['libexif', 'libjpeg', 'libusb']
    
