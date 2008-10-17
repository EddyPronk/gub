from gub import misc

def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['cross/gcc']
    
def change_target_package (package):
    from gub import cross
    from gub import build
    from gub import targetbuild
    cross.change_target_package (package)
    targetbuild.change_target_dict (package,
                    {
            'DLLTOOL': '%(toolchain_prefix)sdlltool',
            'DLLWRAP': '%(toolchain_prefix)sdllwrap',
            })
    return
    def install (whatsthis):
        package.post_install_smurf_exe ()

    package.install = misc.MethodOverrider (package.install, install)
