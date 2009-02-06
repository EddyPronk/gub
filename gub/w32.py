from gub import build
from gub import cross
from gub import loggedos
from gub import misc
from gub import target

def libtool_fix_allow_undefined (logger, file):
    '''libtool: link: warning: undefined symbols not allowed in i686-pc-mingw32 shared  libraries'''
    loggedos.file_sub (logger, [('^(allow_undefined_flag=.*)unsupported', r'\1')], file)

def libtool_disable_relink (logger, file):
    loggedos.file_sub (logger, [('need_relink=yes', 'need_relink=no')], file)

def change_target_package (package):
    def update_libtool (self):
        package.map_locate (libtool_fix_allow_undefined, '%(builddir)s', 'libtool')
        package.map_locate (libtool_disable_relink, '%(builddir)s', 'libtool')
    package.update_libtool = misc.MethodOverrider (package.update_libtool, update_libtool)

    def install (whatsthis):
        package.post_install_smurf_exe ()
    package.install = misc.MethodOverrider (package.install, install)

    # FIXME (cygwin): [why] do cross packages get here too?
    if isinstance (package, cross.AutoBuild):
        return

    target.change_target_dict (package, {
            'DLLTOOL': '%(toolchain_prefix)sdlltool',
            'DLLWRAP': '%(toolchain_prefix)sdllwrap',
            # note: this was cygwin only: ...
            'LDFLAGS': '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api',
            })
