from gub import build

class Freebsd_runtime (build.BinaryBuild, build.SdkBuild):
    source = 'http://lilypond.org/download/gub-sources/freebsd-runtime-4.11-1.%(package_arch)s.tar.gz&strip=0'
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
# blocks installing db, and runtime lacks binary libdb.*
rm -f %(srcdir)s%(prefix_dir)s/include/db.h
''')

class Freebsd_runtime__freebsd__x86 (Freebsd_runtime):
    patches = ['freebsd4-runtime.patch']
    def untar (self):
        Freebsd_runtime.untar (self)
        self.patch ()
        # FIXME: check if empty? (on freebsds4 it is...)
        # cpp -P ~/vc/gub/target/freebsd-x86/root/usr/include/wctype.h
        self.system ('''
#breaks boost#rm %(srcdir)s%(prefix_dir)s/include/wctype.h
cp %(sourcefiledir)s/stdint-32.h %(srcdir)s%(prefix_dir)s/include/stdint.h
''')

class Freebsd_runtime__freebsd__64 (Freebsd_runtime):
    source = 'http://lilypond.org/download/gub-sources/freebsd-runtime-6.2-2.%(package_arch)s.tar.gz&strip=0'
