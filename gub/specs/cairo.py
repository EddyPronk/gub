from gub import target

class Cairo (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairo-1.8.8.tar.gz'
    def patch (self):
        target.AutoBuild.patch (self)
        self.system ('rm -f %(srcdir)s/src/cairo-features.h')
    def _get_build_dependencies (self):
        return ['tools::libtool', 'fontconfig-devel', 'libpng-devel', 'libx11-devel', 'libxrender-devel', 'pixman-devel']

class Cairo__mingw (Cairo):
    def configure_command (self):
        return (Cairo.configure_command (self)
                + ' --enable-win32=yes'
                + ' --enable-win32-font=yes'
                + ' --enable-ft'
                + ' --disable-xlib'
                + ' --disable-xlib-xrender'
                + ' --disable-xcb'
                + ' LDFLAGS=-lpthread'
                )
    def _get_build_dependencies (self):
        return ([x for x in Cairo._get_build_dependencies (self)
                 if 'libx' not in x]
                + ['pthreads-w32-devel'])
