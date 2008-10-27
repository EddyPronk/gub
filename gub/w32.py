from gub import build
from gub import cross
from gub import loggedos
from gub import misc
from gub import targetbuild

def change_target_package (package):

    def configure (whatsthis):
        def libtool_fix_allow_undefined (logger, file):
            '''libtool: link: warning: undefined symbols not allowed in i686-pc-mingw32 shared  libraries'''
            loggedos.file_sub (logger, [('^(allow_undefined_flag=.*)unsupported', r'\1')], file)
        package.map_locate (libtool_fix_allow_undefined, '%(builddir)s', 'libtool')
        # already in build.py
        # package.map_locate (build.AutoBuild.libtool_disable_install_not_into_dot_libs_test, '%(builddir)s', 'libtool')

    package.configure = misc.MethodOverrider (package.configure, configure)

    def install (whatsthis):
        package.post_install_smurf_exe ()

    package.install = misc.MethodOverrider (package.install, install)

    # FIXME (cygwin): [why] do cross packages get here too?
    if isinstance (package, cross.CrossAutoBuild):
        return

    targetbuild.change_target_dict (package, {
            'DLLTOOL': '%(toolchain_prefix)sdlltool',
            'DLLWRAP': '%(toolchain_prefix)sdllwrap',
            # note: this was cygwin only: ...
            'LDFLAGS': '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api',
            })
