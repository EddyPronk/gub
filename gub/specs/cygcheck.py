from gub import build
from gub import mirrors

class Cygcheck (build.BinaryBuild):
    "Only need the cygcheck.exe binary."
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
    source = mirrors.with_template (name='cygcheck', version='1.5.18-1', mirror=mirrors.cygwin_bin, format='bz2')
        
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
