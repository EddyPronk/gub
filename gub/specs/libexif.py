from gub import targetpackage
from gub import mirrors

class Libexif (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
# incompatible with gphoto?
#        self.with_template (version="0.6.9", mirror=mirrors.sf)
# does not install
#        self.with_template (version="0.6.14", mirror=mirrors.sf)
# too old for libgphoto-2.3.1
#        self.with_template (version="0.6.12", mirror=mirrors.sf)
        self.with_template (version="0.6.15", mirror=mirrors.sf)
