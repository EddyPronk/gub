
## untested.
if 0:
        Alien (settings).with_template (version="8.60",
                   mirror="http://www.kitenet.net/programs/alien/alien_8.60.tar.gz",
                   format="gz"),


class Alien (ToolBuildSpec):
    def srcdir (self):
        return '%(allsrcdir)s/alien'
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def configure (self):
        ToolBuildSpec.configure (self)
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/alien.patch')
    def configure_command (self):
        return 'perl Makefile.PL'

