from toolpackage import ToolBuildSpec
import re

class Fontforge (ToolBuildSpec):
    def srcdir (self):
        return re.sub ('_full', '', ToolBuildSpec.srcdir(self))

    def license_file (self):
        return '%(srcdir)s/LICENSE' 
        
    def install_command (self):
        return self.broken_install_command ()

    def packaging_suffix_dir (self):
        return ''
    
    def configure_command (self):
        return ToolBuildSpec.configure_command (self) + " --without-freetype-src "
    def patch (self):
        ToolBuildSpec.patch (self)
        self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/fontforge-20060501-srcdir.patch")
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/fontforge-20060501-execprefix.patch")
		
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (mirror="http://lilypond.org/~hanwen/gub-sources/fontforge_full-%(version)s.tar.bz2",
                   version="20060501")
