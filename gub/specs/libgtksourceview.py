from gub import target

class Libgtksourceview (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/gnome/sources/gtksourceview/2.6/gtksourceview-2.6.2.tar.gz'
    def _get_build_dependencies (self):
        return [
            'gtk+-devel',
            'libxml2-devel',
            'tools::glib',
            'tools::intltool',
            ]

