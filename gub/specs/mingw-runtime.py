from gub import build
from gub import mirrors

class Mingw_runtime (build.BinaryBuild, build.SdkBuild):
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        self.with_template (version='3.9', strip_components=0, mirror=mirrors.mingw)
    def install (self):
        self.system ('''
mkdir -p %(install_prefix)s/share
tar -C %(srcdir)s/ -cf - . | tar -C %(install_prefix)s -xf -
mv %(install_prefix)s/doc %(install_root)s/share
''', locals ())

