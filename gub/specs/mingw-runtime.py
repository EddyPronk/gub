from gub import gubb
from gub import mirrors

class Mingw_runtime (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with (version='3.9', strip_components=0, mirror=mirrors.mingw)
    def install (self):
        self.system ('''
mkdir -p %(install_root)s/usr/share
tar -C %(srcdir)s/ -cf - . | tar -C %(install_root)s/usr -xf -
mv %(install_root)s/usr/doc %(install_root)s/share
''', locals ())

