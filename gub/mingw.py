def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['cross/gcc']
    
def change_target_package (p):
    from gub import cross
    from gub import build
    from gub import targetbuild
    cross.change_target_package (p)
    targetbuild.change_target_dict (p,
                    {
            'DLLTOOL': '%(toolchain_prefix)sdlltool',
            'DLLWRAP': '%(toolchain_prefix)sdllwrap',
            })
