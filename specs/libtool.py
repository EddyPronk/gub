import targetpackage
from toolpackage import ToolBuildSpec
import gub

# FIXME, need for WITH settings when building dependency 'libtool'
# This works without libtool.py:
#    ./gub-builder.py -p mingw build http://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.20.tar.gz

class Libtool (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='1.5.20')
        self.so_version = '3'

    def get_subpackage_names (self):
        return ['devel', 'doc', 'runtime', '']

    def get_dependency_dict (self):
        return { '': ['libltdl3'],
                 'devel' : ['libtool'],
                 'doc' : [],
                 'runtime': [],}

    def get_subpackage_definitions (self):
        d = targetpackage.TargetBuildSpec.get_subpackage_definitions (self)
        #d['devel'].append (['/usr/bin', '/usr/share/libltdl'])
        d['devel'].append ('/usr/bin/libtool*')
        d['devel'].append ('/usr/share/libltdl')
        return d

class Libtool__darwin (Libtool):
    def install (self):
        Libtool.install (self)

        ## necessary for programs that load dynamic modules.
        self.dump ("prependdir DYLD_LIBRARY_PATH=$INSTALLER_PREFIX/lib",
                   '%(install_root)s/usr/etc/relocate/libtool.reloc')

class Libtool__cygwin (Libtool):
    def __init__ (self, settings):
        Libtool.__init__ (self, settings)
        self.with (version='1.5.22')
        #self.with (version='1.5.22-1',
        #          mirror='http://mirrors.kernel.org/sourceware/cygwin/release/libtool/libtool1.5/libtool1.5-%(version)s-1-src.tar.bz2',)
        # FIXME: build lib package naming: lib<NAME><MAJOR-SO-VERSION> into gub

    def only_for_cygwin_untar (self):
        self.untar_cygwin_src_package_variant2 (self.file_name ())

    def get_dependency_dict (self):
        d = Libtool.get_dependency_dict (self)
        d[''].append ('cygwin')
        return d

    def get_subpackage_definitions (self):
        d = Libtool.get_subpackage_definitions (self)
        d['runtime'].append ('/usr/bin/cyg*dll')
        return d

    def install (self):
        Libtool.install (self)
        self.install_readmes ()

    def get_distro_dependency_dict (self):
        return {
            '': ['cygwin'],
            'libltdl3': ['cygwin'],
        }

class Libtool__local (ToolBuildSpec):
    """

Libtool as a local package is rather painful, as Darwin has its own
libtool which is unrelated to GNU libtool, but necessary for linking
dylibs.

    """
    
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version='1.5.20')

    def configure (self):
        gub.BuildSpec.configure (self)

