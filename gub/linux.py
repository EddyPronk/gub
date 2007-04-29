def change_target_package (package):
    from gub import cross
    from gub import gubb
    from gub import targetpackage
    cross.change_target_package (package)
    if isinstance (package, targetpackage.TargetBuildSpec):
        gubb.change_target_dict (package,
                                {'LD': '%(target_architecture)s-ld --as-needed, ',})
        gubb.append_target_dict (package,
                                {'LDFLAGS': ' -Wl,--as-needed ' })
    return package

def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']
    
