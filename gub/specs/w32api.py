from gub import build
from gub import mirrors

class W32api (build.BinaryBuild, build.SdkBuild):
    source = mirrors.with_template (name='w32api', version='3.6', strip_components=0, mirror=mirrors.mingw)
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        print 'FIXME: serialization:', __file__, ': strip-components'
        source.strip_components = 0
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
cd  %(srcdir)s/ && mkdir usr && mv include lib usr/
''')

