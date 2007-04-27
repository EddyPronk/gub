def change_target_package (package):
    import cross
    import gub
    import targetpackage
    cross.change_target_package (package)
    if isinstance (package, targetpackage.TargetBuildSpec):
        gub.change_target_dict (package,
                                {'LD': '%(target_architecture)s-ld --as-needed, ',})
        gub.append_target_dict (package,
                                {'LDFLAGS': ' -Wl,--as-needed ' })
    return package

def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']
    
