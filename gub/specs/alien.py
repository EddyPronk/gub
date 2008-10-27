
## untested.
if 0:
    Alien (settings).with_template (version="8.60",
           mirror="http://www.kitenet.net/programs/alien/alien_8.60.tar.gz",
           format="gz"),


class Alien (ToolsBuild):
    def srcdir (self):
        return '%(allsrcdir)s/alien'
    def configure (self):
        self.shadow ()
        ToolsBuild.configure (self)
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/alien.patch')
    def configure_command (self):
        return 'perl Makefile.PL'

