import toolpackage
import download

class Texinfo(toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version="4.8",
                   mirror=download.gnu, format="bz2")
    def patch (self):
        toolpackage.ToolBuildSpec.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 <  %(patchdir)s/texinfo-4.8.patch')

    ## TODO: should patch out info reader completely.
