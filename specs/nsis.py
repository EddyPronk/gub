from toolpackage import ToolBuildSpecification
import os

## 2.06 and earlier.
class Nsis__old (ToolBuildSpecification):
    def compile (self): 
        env = {}
        env['PATH'] = '%(topdir)s/target/mingw/system/usr/cross/bin:' + os.environ['PATH']
        self.system ('cd %(builddir)s/ && make -C Source POSSIBLE_CROSS_PREFIXES=i686-mingw32- ', env)
              
    def patch (self):
        ## Can't use symlinks for files, since we get broken symlinks in .gub
        self.system ('mkdir -p %(allbuilddir)s', ignore_error=True)
        self.system ('ln -s %(srcdir)s %(builddir)s') 
        
    def srcdir (self):
        d = ToolBuildSpecification.srcdir (self).replace ('_','-')
        return d

    def configure (self):
        pass
    
    def install (self):
        ## this is oddball, the installation ends up in system/usr/usr/
        ## but it works ...
        self.system('''
cd %(builddir)s && ./install.sh %(system_root)s/usr/ %(install_root)s 
''')
# cd %(install_root)s/usr/ && mkdir bin && cd bin && ln -s ../share/NSIS/makensis .

    def package (self):
        self.system ('tar -C %(install_root)s/%(system_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .')


class Nsis (ToolBuildSpecification):
    def __init__ (self, settings):
        ToolBuildSpecification.__init__(self, settings)
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

    def package (self):
        self.system ('tar -C %(install_root)s/%(system_root)s/ -zcf %(gub_uploads)s/%(gub_name)s .')

        
    def srcdir (self):
        d = ToolBuildSpecification.srcdir (self).replace ('_','-') + '-src'
        return d
          


