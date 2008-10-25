from gub import toolsbuild
from gub import build

class Librestrict__tools (toolsbuild.ToolsBuild, build.SdkBuild):
    source = 'http://lily/librestrict-1.0.tar.gz'
    def stages (self):
        return [x for x in toolsbuild.ToolsBuild.stages (self)
                if x not in ['download', 'patch', 'autoupdate', 'configure']]
    # ugh, download is not a true stage [yet]
    def download (self):
        pass
    def untar (self):
        self.system ('rm -rf %(builddir)s')
        self.shadow_tree ('%(gubdir)s/librestrict', '%(builddir)s')
    def makeflags (self):
        return 'prefix=%(system_prefix)s'
    def LD_PRELOAD (self):
        return ''
