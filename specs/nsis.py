from toolpackage import ToolBuildSpec
import os

class Nsis (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__(self, settings)
        self.with (version='2.16',
                   mirror="http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s-src.tar.%(format)s",
                   
                   format="bz2")

    def get_build_dependencies (self):
        return ["scons"]

    def patch (self):
  
        if 1: # 2.16
            self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/nsis-2.16-macos.patch")
            self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/nsis-2.16-platform-h.patch")
            self.system ('mkdir -p %(allbuilddir)s', ignore_error=True)
            self.system ('ln -s %(srcdir)s %(builddir)s') 
		
    def configure (self):
        pass

    def compile_command (self):
        ## no trailing / in paths!
        return (' scons PREFIX=%(system_root)s/usr PREFIX_DEST=%(install_root)s '
                ' DEBUG=yes '

                ## /s switch doesn't work anymore?!
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
          
    def get_packages (self):
        return self.get_broken_packages ()
    



