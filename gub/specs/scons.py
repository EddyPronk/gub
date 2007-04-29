from gub import toolpackage
from gub import mirrors

class Scons (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version='0.96.93',
                   format='gz',
                   mirror=mirrors.sf),

    def compile (self):
        pass

    def patch (self):
        pass
    
    def configure (self):
        self.system ('mkdir %(builddir)s')
    
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(local_prefix)s --root=%(install_root)s'

    def license_file (self):
        return '%(srcdir)s/LICENSE.txt' 
