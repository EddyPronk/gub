import toolpackage

class Git (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (mirror="http://kernel.org/pub/software/scm/git/git-1.4.3.tar.bz2",
                   version="1.4.3")

        
    def patch (self):
        self.shadow_tree ("%(srcdir)s", '%(builddir)s')
        self.system ('cd %(srcdir)s && autoconf')
    
