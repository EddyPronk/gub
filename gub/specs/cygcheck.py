from gub import gubb
from gub import mirrors

class Cygcheck (gubb.BinarySpec):
    "Only need the cygcheck.exe binary."
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with_template (version='1.5.18-1', mirror=mirrors.cygwin_bin, format='bz2')
        
    def untar (self):
        gubb.BinarySpec.untar (self)

        file = self.expand ('%(srcdir)s/usr/bin/cygcheck.exe')
        cygcheck = open (file).read ()
        self.system ('rm -rf %(srcdir)s/')
        self.system ('mkdir -p %(srcdir)s/usr/bin/')
        open (file, 'w').write (cygcheck)

    def basename (self):
        import re
        f = gubb.BinarySpec.basename (self)
        f = re.sub ('-1$', '', f)
        return f
