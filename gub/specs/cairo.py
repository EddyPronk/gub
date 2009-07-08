from gub import target

class Cairo (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairo-1.8.8.tar.gz'
    def patch (self):
        target.AutoBuild.patch (self)
        self.system ('rm -f %(srcdir)s/src/cairo-features.h')
    def _get_build_dependencies (self):
        return ['tools::libtool',
                'fontconfig-devel',
                'ghostscript-devel',
                'libpng-devel',
                'libx11-devel',
                'libxrender-devel',
                'pixman-devel',
                # FIXME: poppler, librsvg, cairo, gtk dependencies?
                # gtk+ depends on pango, pango on cairo, cairo on poppler, and poppler on gtk+?
                # TRIED: removing gtk+ dependency from poppler -- no go
                # TRY: removing poppler from cairo...
#                'poppler-devel',
                'zlib-devel']

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
                 if 'libx' not in x
                 and 'poppler' not in x] # poppler does not build for mingw
                + ['pthreads-w32-devel'])
