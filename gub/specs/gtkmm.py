from gub import target

class Gtkmm (target.AutoBuild):
#    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.12/glibmm-2.12.10.tar.gz'
    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtkmm/2.14/gtkmm-2.14.3.tar.gz'
    def _get_build_dependencies (self):
        return ['cairomm-devel', 'gtk+-devel', 'pangomm-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
