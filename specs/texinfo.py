import toolpackage
import download

class Texinfo(toolpackage.ToolBuildSpecification):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpecification.__init__ (self, settings)
        self.with (version="4.8",
                   mirror=download.gnu, format="bz2")
    def patch (self):
        toolpackage.ToolBuildSpecification.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 <  %(patchdir)s/texinfo-4.8.patch')
