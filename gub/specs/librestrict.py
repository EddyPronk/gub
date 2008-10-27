from gub import toolsbuild

class Librestrict__tools (toolsbuild.AutoBuild):
    source = 'url://host/librestrict-1.0.tar.gz'
    # ugh, download is not a true stage [yet]
    def untar (self):
        self.system ('rm -rf %(builddir)s')
    def configure (self):
        self.shadow_tree ('%(gubdir)s/librestrict', '%(builddir)s')
    def makeflags (self):
        return 'prefix=%(system_prefix)s'
    def LD_PRELOAD (self):
        return ''
