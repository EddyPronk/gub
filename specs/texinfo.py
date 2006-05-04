import toolpackage
import download

class Texinfo(toolpackage.Tool_package):
    def __init__ (self, settings):
        toolpackage.Tool_package.__init__ (self, settings)
        self.with (version="4.8",
                   mirror=download.gnu, format="bz2")
    def patch (self):
        toolpackage.Tool_package.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 <  %(patchdir)s/texinfo-4.8.patch')
