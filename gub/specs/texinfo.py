from gub import toolsbuild
from gub import mirrors

class Texinfo(toolsbuild.ToolsBuild):
    def __init__ (self, settings):
        toolsbuild.ToolsBuild.__init__ (self, settings)
        self.with_template (version="4.8",
                   mirror=mirrors.gnu, format="bz2")
    def patch (self):
        toolsbuild.ToolsBuild.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 <  %(patchdir)s/texinfo-4.8.patch')

    ## TODO: should patch out info reader completely.
