from gub import target

class Libpthread_stubs (target.AutoBuild):
    source = 'http://xcb.freedesktop.org/dist/libpthread-stubs-0.1.tar.gz'
    def _get_build_dependencies (self):
        return ['libtool']

class Libpthread_stubs__freebsd__x86 (Libpthread_stubs):
    def configure_command (self):
        return (Libpthread_stubs.configure_command (self)
                + ' LDFLAGS=-lc_r')
    
class Libpthread_stubs__mingw (Libpthread_stubs):
    def _get_build_dependencies (self):
        return (Libpthread_stubs._get_build_dependencies (self)
                + ['pthreads-w32-devel'])
