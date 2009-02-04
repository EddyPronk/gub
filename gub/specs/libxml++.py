from gub import target

class Libxml_xx_ (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/libxml++/2.18/libxml++-2.18.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glibmm-devel']
