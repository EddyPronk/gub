import os

from gub import mirrors
from gub import repository
from gub import toolsbuild

class Nsis (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='nsis', version='2.24',
                                    # wx-windows, does not compile
                                    # version='2.30',
                                    # bzip2 install problem
                                    # version='2.23',
                                    mirror='http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s-src.tar.%(format)s',
                                    format='bz2')
    FOOsource = repository.CVS ('downloads/nsis',
                             source=':pserver:anonymous@nsis.cvs.sourceforge.net:/cvsroot/nsis',
                             module='NSIS',
                             tag='HEAD')
    def __init__ (self, settings, source):
        toolsbuild.ToolsBuild.__init__ (self, settings, source)
        self.x64_hack = 'x86_64-linux' in settings.build_architecture

    def get_build_dependencies (self):
        return ['scons']

    def patch (self):
        self.system ('mkdir -p %(allbuilddir)s', ignore_errors=True)
        self.system ('ln -s %(srcdir)s %(builddir)s')
        if self.settings.build_architecture.startswith ('x86_64-linux'):
            self.file_sub ([('''^Export\('defenv'\)''', '''
import os
defenv['CC'] = os.environ['CC']
defenv['CXX'] = os.environ['CXX']
Export('defenv')
''')],
                       '%(srcdir)s/SConstruct')
        
    def configure (self):
        pass

    def compile_command (self):
        ## no trailing / in paths!
        s = ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s'
#                ' CPATH=%(CPATH)s'
                ' DEBUG=yes'
                ' NSIS_CONFIG_LOG=yes'
                ' SKIPPLUGINS=System')

        return s
    
    def get_compile_env (self):
        env = {'PATH': '%(gubdir)s/target/mingw/root/usr/cross/bin:' + os.environ['PATH'] }
#        env['CPATH'] = ''
        if self.x64_hack:
            x86_dir = package.settings.alltargetdir + '/linux-x86'
            x86_cross = (x86_dir
                         + package.settings.root_dir
                         + package.settings.prefix_dir
                         + package.settings.cross_dir)
            x86_bindir = x86_cross + '/bin'
            x86_cross_bin = x86_cross + '/i686-linux' + '/bin'

            env['LIBRESTRICT_ALLOW'] = self.settings.targetdir
            env['CC'] = x86_cross_bin + '/gcc'
            env['CXX'] = x86_cross_bin + '/g++'
            env['PATH'] = x86_cross_bin + ':' + env['PATH']
#            env['CPATH'] = x86_cross_bin + ':' + env['PATH']

        return env

    def compile (self): 
        self.system ('cd %(builddir)s/ && %(compile_command)s',
                     self.get_compile_env ())

    def install (self):
        self.system ('cd %(builddir)s/ && %(compile_command)s install ',
                     self.get_compile_env ())

    def install_command (self):
        return self.compile_command () + ' install'

