from gub import targetbuild
from gub import mirrors

class Libusb (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_template (version="0.1.12", mirror=mirrors.sf)
    def configure (self):
        targetbuild.TargetBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
