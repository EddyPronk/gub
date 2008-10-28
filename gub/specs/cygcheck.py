from gub import build

class Cygcheck (build.BinaryBuild):
    "Only need the cygcheck.exe binary."
    source = 'http://mirrors.kernel.org/sourceware/cygwin/release/cygcheck-1.5.18-1.tar.bz2'
    def untar (self):
        build.BinaryBuild.untar (self)
        file = self.expand ('%(srcdir)s/usr/bin/cygcheck.exe')
        cygcheck = open (file).read ()
        self.system ('rm -rf %(srcdir)s/')
        self.system ('mkdir -p %(srcdir)s/usr/bin/')
        open (file, 'w').write (cygcheck)
    def basename (self):
        import re
        f = build.BinaryBuild.basename (self)
        f = re.sub ('-1$', '', f)
        return f
