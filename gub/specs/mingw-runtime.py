from gub import gubb
from gub import mirrors

class Mingw_runtime (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with_template (version='3.9', strip_components=0, mirror=mirrors.mingw)
    def install (self):
        self.system ('''
mkdir -p %(install_prefix)s/share
tar -C %(srcdir)s/ -cf - . | tar -C %(install_prefix)s -xf -
mv %(install_prefix)s/doc %(install_root)s/share
''', locals ())

