from gub import tools

class Intltool (tools.AutoBuild):
    source = 'ftp://ftp.gnome.org/pub/GNOME/sources/intltool/0.40/intltool-0.40.5.tar.gz'
    def _get_build_dependencies (self):
        return [
            'tools::perl-xml-parser',
            ]
