from gub import targetbuild
from gub import build
from gub import mirrors
from gub import toolsbuild


# FIXME, need for WITH settings when building dependency 'libtool'
# This works without libtool.py:
#    ./gub-builder.py -p mingw build http://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.20.tar.gz

class Libtool (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        # KUGH
        self.so_version = '3'
    def get_subpackage_names (self):
        return ['devel', 'doc', 'runtime', '']
    def get_dependency_dict (self):
        return { '': ['libtool-runtime'],
                 'devel' : ['libtool'],
                 'doc' : [],
                 'runtime': [],}
    def get_subpackage_definitions (self):
        d = targetbuild.TargetBuild.get_subpackage_definitions (self)
        d['devel'].append (self.settings.prefix_dir + '/bin/libtool*')
        d['devel'].append (self.settings.prefix_dir + '/share/libltdl')
        return d

class Libtool__darwin (Libtool):
    def install (self):
        Libtool.install (self)
        ## necessary for programs that load dynamic modules.
        self.dump ("prependdir DYLD_LIBRARY_PATH=$INSTALLER_PREFIX/lib",
                   '%(install_prefix)s/etc/relocate/libtool.reloc')

class Libtool__cygwin (Libtool):
    def __init__ (self, settings):
        Libtool.__init__ (self, settings)
        self.with_template (version='1.5.22')
    def only_for_cygwin_untar (self):
        cygwin.untar_cygwin_src_package_variant2 (self, self.file_name ())
    # FIXME: we do most of this for all cygwin packages
    def get_dependency_dict (self):
        d = Libtool.get_dependency_dict (self)
        d[''].append ('cygwin')
        return d
    def category_dict (self):
        return {'': 'Devel'}

class Libtool__tools (toolsbuild.ToolsBuild):
    def __init__ (self, settings, source):
        toolsbuild.ToolsBuild.__init__ (self, settings, source)
    def configure (self):
        build.UnixBuild.configure (self)
    def wrap_executables (self):
        # The libtool script calls the cross compilers, and moreover,
        # it is copied.  Two reasons why it cannot be wrapped.
        pass
