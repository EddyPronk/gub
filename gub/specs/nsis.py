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
        
    #FIXME: should be automatic for scons build
    def stages (self):
        return misc.list_remove (build.SdkBuild.stages (self), ['configure'])

    def compile_command (self):
        # SCons barfs on trailing / on directory names
        return ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s'
                ' DEBUG=yes'
                ' NSIS_CONFIG_LOG=yes'
                ' SKIPPLUGINS=System')
    
    def get_compile_env (self):
        # Do not use 'root', 'usr', 'cross', rather use from settings,
        # that enables changing system root, prefix, etc.
        mingw_dir = (self.settings.alltargetdir + '/mingw'
                     + self.settings.root_dir)
        mingw_bin = (mingw_dir
                     + self.settings.prefix_dir
                     + self.settings.cross_dir
                     + '/bin')
        env = {'PATH': mingw_bin + ':' + os.environ['PATH'] }
        if 'x86_64-linux' in self.settings.build_architecture:
            from gub import cross
            return cross.setup_linux_x86 (self, env)
        return env

    def compile (self): 
        self.system ('cd %(builddir)s/ && %(compile_command)s',
                     self.get_compile_env ())

    def install (self):
        self.system ('cd %(builddir)s/ && %(compile_command)s install ',
                     self.get_compile_env ())

    def install_command (self):
        return self.compile_command () + ' install'

