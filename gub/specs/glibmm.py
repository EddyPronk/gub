from gub import target

class Glibmm (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.18/glibmm-2.18.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glib-devel', 'libsig++-devel']
