import os

from gub import mirrors
from gub import misc
from gub import repository
from gub import toolsbuild
from gub import cross

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

    def add_mingw_env (self):
        # Do not use 'root', 'usr', 'cross', rather use from settings,
        # that enables changing system root, prefix, etc.
        mingw_dir = (self.settings.alltargetdir + '/mingw'
                     + self.settings.root_dir)
        mingw_bin = (mingw_dir
                     + self.settings.prefix_dir
                     + self.settings.cross_dir
                     + '/bin')
        return {'PATH': mingw_bin + ':' + os.environ['PATH'] }
        
    def __init__ (self, settings, source):
        toolsbuild.ToolsBuild.__init__ (self, settings, source)
        if 'x86_64-linux' in self.settings.build_architecture:
            cross.setup_linux_x86 (self, self.add_mingw_env ())
        
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
        return misc.list_remove (toolsbuild.ToolsBuild.stages (self),
                                 ['configure'])
    def compile_command (self):
        # SCons barfs on trailing / on directory names
        return ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s'
                ' DEBUG=yes'
                ' NSIS_CONFIG_LOG=yes'
                ' SKIPPLUGINS=System')

    # this method is overwritten for x86-64_linux
    def build_environment (self):
        return self.add_mingw_env ()
    
    def compile (self):
        self.system ('cd %(builddir)s/ && %(compile_command)s',
                     self.build_environment ())

    def install_command (self):
        return self.compile_command () + ' install'
    
    def install (self):
        self.system ('cd %(builddir)s && %(install_command)s ',
                     self.build_environment ())

