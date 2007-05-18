from gub import gubb
from gub import mirrors

class W32api (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with_template (version='3.6', strip_components=0, mirror=mirrors.mingw)
    def untar (self):
        gubb.BinarySpec.untar (self)
        self.system ('''
cd  %(srcdir)s/ && mkdir usr && mv include lib usr/
''')

