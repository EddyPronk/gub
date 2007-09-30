from gub import toolsbuild

class Texinfo (toolsbuild.ToolsBuild):
    def patch (self):
        toolsbuild.ToolsBuild.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/texinfo-4.8.patch')
