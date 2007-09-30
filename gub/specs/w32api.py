from gub import build
from gub import mirrors

class W32api (build.BinaryBuild, build.SdkBuild):
    def __init__ (self, settings):
        build.BinaryBuild.__init__ (self, settings)
        self.with_template (version='3.6', strip_components=0, mirror=mirrors.mingw)
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
cd  %(srcdir)s/ && mkdir usr && mv include lib usr/
''')

