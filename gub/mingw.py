def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['cross/gcc']
    
def change_target_package (p):
    from gub import cross
    from gub import gubb
    cross.change_target_package (p)
    gubb.change_target_dict (p,
                    {
            'DLLTOOL': '%(tool_prefix)sdlltool',
            'DLLWRAP': '%(tool_prefix)sdllwrap',
            })
