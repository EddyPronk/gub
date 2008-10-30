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
    def no_threads (d):
        return (d
                + ' --disable-threads' # libicu
                + ' --without-threads' # libxml2
                + '--disable-posixmutexes --disable-mutexsupport --disable-pthread_api' # db
                )
    package.configure_command \
        = misc.MethodOverrider (package.configure_command, no_threads)
