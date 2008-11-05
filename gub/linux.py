from gub import build
from gub import cross
from gub import target

def change_target_package (package):
    cross.change_target_package (package)
    if isinstance (package, target.AutoBuild):
        target.change_target_dict (package,
                                 {'LD': '%(target_architecture)s-ld --as-needed ',})
        target.append_target_dict (package,
                                 {'LDFLAGS': ' -Wl,--as-needed ' })
    return package

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']
    
