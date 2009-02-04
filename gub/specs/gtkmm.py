from gub import target

class Gtkmm (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtkmm/2.14/gtkmm-2.14.3.tar.gz'
    def _get_build_dependencies (self):
        return ['cairomm-devel', 'gtk+-devel', 'pangomm-devel']
