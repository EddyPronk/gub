from gub import build

'''
Make import lib

wget 'http://ftp.debian.org/debian/pool/main/w/wine/wine_0.9.25-2.1_i386.deb'
mkdir bin lib
cp /usr/share/wine/skel/c/windows/system32/wsock32.dll bin/libwsock32.dll
echo EXPORTS > lib/libwsock32.a.def
target/mingw/root/usr/cross/bin/i686-mingw32-nm target/mingw/usr/libwsock32.a | grep ' T _' | sed -e 's/.* T _//' -e 's/@.*//' >> lib/libwsock32.a.def
target/mingw/root/usr/cross/bin/i686-mingw32-dlltool --def lib/libwsock32.a.def --dllname bin/libwsock32.dll --output-lib lib/libwsock32.dll.a
# manually create lib/libwsock32.la
'''

class Libwsock32 (build.BinaryBuild):
# newer WINEs come with a dll.so that's not usable in Windows :-(
#    source = 'http://ftp.debian.org/debian/pool/main/w/wine/wine_0.9.25-2.1_i386.deb'
# ugh, turns out this libwsock32.dll from wine is empty
# which somehow means that linking works until you create an executable
    source = 'http://lilypond.org/download/gub-sources/libwsock32-0.9.25.tar.gz'
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        source._version = '0.9.25'
        source.strip_components = 0
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
cd  %(srcdir)s && mkdir usr && mv bin lib usr
''')
