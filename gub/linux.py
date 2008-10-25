def change_target_package (package):
    from gub import cross
    from gub import build
    from gub import targetbuild
    cross.change_target_package (package)
    if isinstance (package, targetbuild.TargetBuild):
        targetbuild.change_target_dict (package,
                                 {'LD': '%(target_architecture)s-ld --as-needed ',})
        targetbuild.append_target_dict (package,
                                 {'LDFLAGS': ' -Wl,--as-needed ' })
    return package

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']
    
