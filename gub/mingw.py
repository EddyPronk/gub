from gub import cross
from gub import w32

def get_cross_build_dependencies (settings):
    return ['cross/gcc']
    
def change_target_package (package):
    cross.change_target_package (package)
    w32.change_target_package (package)
