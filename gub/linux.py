from gub import build
from gub import cross
from gub import target

def change_target_package (package):
    cross.change_target_package (package)
    return package

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']
    
