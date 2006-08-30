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


class Libtool__darwin (Libtool):
    def install (self):
        Libtool.install (self)

        ## necessary for programs that load dynamic modules.
        self.dump ("prependdir DYLD_LIBRARY_PATH=$INSTALLER_PREFIX/lib",
                   '%(install_root)s/usr/etc/relocate/libtool.reloc')

class Libtool__cygwin (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        #self.with (version='1.5.22')
        self.with (version='1.5.22-1',
                   mirror='http://mirrors.kernel.org/sourceware/cygwin/release/libtool/libtool1.5/libtool1.5-%(version)s-1-src.tar.bz2',)

    def untar (self):
        self.untar_cygwin_src_package_variant2 (self.file_name ())

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

