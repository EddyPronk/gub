from gub import toolsbuild

class Librestrict__tools (toolsbuild.MakeBuild):
    source = 'url://host/librestrict-1.0.tar.gz'
    def untar (self):
        self.system ('rm -rf %(builddir)s')
    def shadow (self):
        self.shadow_tree ('%(gubdir)s/librestrict', '%(builddir)s')
    def makeflags (self):
        return 'prefix=%(system_prefix)s'
    def LD_PRELOAD (self):
        return ''
