import os

from gub import repository
from gub import toolsbuild

class Nsis (toolsbuild.ToolsBuild):
    def __init__ (self, settings, source):
        toolsbuild.ToolsBuild.__init__ (self, settings, source)
        self.save_path = os.environ['PATH']
        mingw_dir = settings.alltargetdir + '/mingw' + settings.root_dir
        os.environ['PATH'] = (mingw_dir
                              + settings.prefix_dir + settings.cross_dir
                              + '/bin' + ':' + os.environ['PATH'])
        # nsis <= 2.30 does not build with 64 bit compiler
        self.CPATH = ''
        if settings.build_architecture.startswith ('x86_64-linux'):
            from gub import cross
            cross.setup_linux_x86 (self)
            os.environ['PATH'] = self.PATH
            os.environ['CC'] = self.CC
            os.environ['CXX'] = self.CXX
            # FIXME: need this to find windows.h on linux-64;
            # how does this ever work on linux-x86?
            self.CPATH = mingw_dir + settings.prefix_dir + '/include'

        if 1:
        source = mirrors.with_template (name='nsis', version='2.24',
                # wx-windows, does not compile
                # version='2.30',
                # bzip2 install problem
                # version='2.23',
                       mirror='http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(version)s-src.tar.%(format)s',
                       format='bz2')
        else:
            repo = repository.CVS (
                self.get_repodir (),
                source=':pserver:anonymous@nsis.cvs.sourceforge.net:/cvsroot/nsis',
                module='NSIS',
                tag='HEAD')
        source = mirrors.with_vc (repo)

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
        #self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/nsis-2.22-contrib-math.patch')
        
    def configure (self):
        pass

    def compile_command (self):
        ## no trailing / in paths!
        return ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s'
                ' CPATH=%(CPATH)s'
                ' DEBUG=yes'
                ' NSIS_CONFIG_LOG=yes'
                ' SKIPPLUGINS=System')
    
    def install_command (self):
        return self.compile_command () + ' install'

    def clean (self):
        if settings.build_architecture.startswith ('x86_64-linux'):
            os.environ['PATH'] = self.save_path
            del os.environ['CC']
            del os.environ['CXX']
        toolsbuild.ToolsBuild.clean (self)
