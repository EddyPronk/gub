from gub import target

class Poppler (target.AutoBuild):
    #source = 'http://poppler.freedesktop.org/poppler-0.10.3.tar.gz'
    #source= 'http://poppler.freedesktop.org/poppler-0.10.7.tar.gz'
    source = 'http://poppler.freedesktop.org/poppler-0.11.2.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'tools::glib',
                'zlib-devel',
                'fontconfig-devel',
                'gtk+-devel',
                'libjpeg-devel',
                'libxml2-devel',
                ]
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --disable-poppler-qt'
                + ' --disable-poppler-qt4'
                + ' --enable-xpdf-headers'
                + ' --disable-gtk-test')
                # FIXME: poppler, librsvg, cairo, gtk dependencies?
                # gtk+ depends on pango, pango on cairo, cairo on poppler, and poppler on gtk+ and cairo
                # TRIED: removing gtk+ dependency from poppler -- no go
                # TRY: removing poppler from cairo...
                #+ ' --disable-gdk'
                #+ ' --disable-splash-output'
                #+ ' --disable-cairo' ? 

class Poppler__mingw (Poppler):
    patches = ['poppler-0.11.2-mingw.patch']

class Poppler__darwin (Poppler):
    def _get_build_dependencies (self):
        return [x for x in Poppler._get_build_dependencies (self)
                if x.replace ('-devel', '') not in [
                'libxml2', # Included in darwin-sdk, hmm?
                ]]
