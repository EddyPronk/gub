import toolpackage

class Git (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (mirror="http://kernel.org/pub/software/scm/git/git-%(version)s.tar.bz2",
                   version="1.4.4.3")
    def patch (self):
        self.shadow_tree ("%(srcdir)s", '%(builddir)s')
    def configure (self):
        self.dump ('prefix=%(system_root)s/usr', '%(builddir)s/config.mak')
        
    def wrap_executables (self):
        # GIT executables use ancient unix style smart name-based
        # functionality switching.  Did Linus not read or understand
        # Standards.texi?
        pass
