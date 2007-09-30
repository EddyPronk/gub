from gub import targetpackage
from gub import mirrors

class Libusb (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (version="0.1.12", mirror=mirrors.sf)
    def configure (self):
        targetpackage.TargetBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
