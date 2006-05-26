from toolpackage import ToolBuildSpecification
import re

class Fontforge (ToolBuildSpecification):
    def srcdir (self):
        return re.sub ('_full', '', ToolBuildSpecification.srcdir(self))

    def install_command (self):
        return self.broken_install_command ()

    def configure_command (self):
        return ToolBuildSpecification.configure_command (self) + " --without-freetype-src "
    def patch (self):
        ToolBuildSpecification.patch (self)
        self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/fontforge-20060501-srcdir.patch")
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/fontforge-20060501-execprefix.patch")
		
    def __init__ (self, settings):
        ToolBuildSpecification.__init__ (self, settings)
        self.with (mirror="http://fontforge.sourceforge.net/fontforge_full-%(version)s.tar.bz2",
                   version="20060501"),
