from gub import build

class W32api (build.BinaryBuild, build.SdkBuild):
    #source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/mingw-3.12.tar.gz&strip=0'
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/w32api-3.12-mingw32-dev.tar.gz&strip=0'
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
cd  %(srcdir)s/ && mkdir usr && mv include lib usr/
''')
