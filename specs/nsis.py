from toolpackage import ToolBuildSpec
import os

class Nsis (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__(self, settings)
        self.with (version='2.20',
                   
                   mirror="http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s-src.tar.%(format)s",
                   
                   format="bz2")

    def get_build_dependencies (self):
        return ["scons"]

    def patch (self):
        self.system ('mkdir -p %(allbuilddir)s', ignore_error=True)
        self.system ('ln -s %(srcdir)s %(builddir)s')

    def configure (self):
        pass

    def compile_command (self):
        ## no trailing / in paths!
        return (' scons PREFIX=%(system_root)s/usr PREFIX_DEST=%(install_root)s '
                ' DEBUG=yes '
                ' NSIS_CONFIG_LOG=yes '
                ' SKIPPLUGINS=System')
    
    def compile (self): 
        env = {'PATH': '%(topdir)s/target/mingw/system/usr/cross/bin:' + os.environ['PATH']}
        self.system ('cd %(builddir)s/ && %(compile_command)s',
                     env)

    def install (self):
        env = {'PATH': '%(topdir)s/target/mingw/system/usr/cross/bin:' + os.environ['PATH']}
        self.system ('cd %(builddir)s/ && %(compile_command)s install ', env)
        
    def srcdir (self):
        d = ToolBuildSpec.srcdir (self).replace ('_','-') + '-src'
        return d
          



