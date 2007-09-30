from gub import mirrors
from gub import targetpackage

class Libxml2 (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnome_218, version='2.6.27')
    def configure_command (self):
        return (targetpackage.TargetBuild.configure_command (self)
                + ' --without-python')
