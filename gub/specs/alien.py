from gub import tools

class Alien (tools.AutoBuild):
    source = "http://www.kitenet.net/programs/alien/alien_8.60.tar.gz",
    srcdir_build_broken = True
    def srcdir (self):
        return '%(allsrcdir)s/alien'
    def configure (self):
        tools.AutoBuild.configure (self)
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/alien.patch')
    def configure_command (self):
        return 'perl Makefile.PL'

