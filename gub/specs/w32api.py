from gub import build

class W32api (build.BinaryBuild, build.SdkBuild):
    #source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/mingw-3.11.tar.gz'
    #source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/mingw-3.12.tar.gz'
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/w32api-3.12-mingw32-dev.tar.gz'
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        source.strip_components = 0
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
cd  %(srcdir)s/ && mkdir usr && mv include lib usr/
''')
