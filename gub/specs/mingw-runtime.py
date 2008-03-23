from gub import build
from gub import mirrors

class Mingw_runtime (build.BinaryBuild, build.SdkBuild):
    source = mirrors.with_template (name='mingw-runtime', version='3.14', strip_components=0, mirror=mirrors.mingw)
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        print 'FIXME: serialization:', __file__, ': strip-components'
        source.strip_components = 0
    def install (self):
        self.system ('''
mkdir -p %(install_prefix)s/share
tar -C %(srcdir)s/ -cf - . | tar -C %(install_prefix)s -xf -
mv %(install_prefix)s/doc %(install_root)s/share
''', locals ())
