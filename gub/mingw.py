from gub import cross
from gub import w32

def get_cross_build_dependencies (settings):
    return ['cross/gcc']
    
def change_target_package (package):
    cross.change_target_package (package)
    w32.change_target_package (package)

    return

    # Too crude?
    # We need pthreads-w32 with python for openoffice
    # but db breaks with threads (although uses its own
    # interesting --disable-* naming), but libicu breaks,
    # libxml2 breaks...
    package.configure_command = (package.configure_command
                                 + w32.configure_no_threads)
