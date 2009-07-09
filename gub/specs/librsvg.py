from gub import target

class Librsvg (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/librsvg/2.26/librsvg-2.26.0.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool',
                'cairo-devel',
                'fontconfig-devel',
                'glib-devel',
                'gtk+-devel',
                'pangocairo-devel',
                'libxml2-devel']
