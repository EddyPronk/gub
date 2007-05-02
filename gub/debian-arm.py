def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    from gub import debian
    # FIXME: urg, must override in debian/cross/gcc.py
    debian.gcc_version = '3.4.3' # only change
    return debian.get_cross_build_dependencies (settings)

def change_target_package (p):
    from gub import cross
    cross.change_target_package (p)
    return p
