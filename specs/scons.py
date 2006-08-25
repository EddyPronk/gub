from toolpackage import ToolBuildSpec
import download

class Scons (ToolBuildSpec):
    def compile (self):
        pass

    def patch (self):
        pass
    
    def configure (self):
        self.system ('mkdir %(builddir)s')
    
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(buildtools)s --root=%(install_root)s'

    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version='0.96.91',
                   format='gz',
                   mirror=download.sf),
        
