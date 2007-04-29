from gub import toolpackage
from gub import mirrors

class Flex (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version="2.5.4a",
                   mirror=mirrors.nongnu, format='gz'),
    def srcdir (self):
        return '%(allsrcdir)s/flex-2.5.4'
    def install_command (self):
        return self.broken_install_command ()
    def packaging_suffix_dir (self):
        return ''
    def patch (self):
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/flex-2.5.4a-FC4.patch")
