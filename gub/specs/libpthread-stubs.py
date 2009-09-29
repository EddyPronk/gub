from gub import target

class Libpthread_stubs (target.AutoBuild):
    source = 'http://xcb.freedesktop.org/dist/libpthread-stubs-0.1.tar.gz'
    dependencies = ['tools::libtool']

class Libpthread_stubs__freebsd__x86 (Libpthread_stubs):
    configure_variables = (Libpthread_stubs.configure_variables
                           + ' CFLAGS=-pthread')
    
class Libpthread_stubs__mingw (Libpthread_stubs):
    dependencies = (Libpthread_stubs.dependencies
                + ['pthreads-w32-devel'])
