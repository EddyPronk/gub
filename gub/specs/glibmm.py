from gub import target

class Glibmm (target.AutoBuild):
#    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.12/glibmm-2.12.10.tar.gz'
    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.18/glibmm-2.18.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glib-devel', 'libsig++-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
    ## FIXME: tools.configure () always updates libtool
    ## why no in target.py // 18 packages do this??
    def configure (self):
        target.AutoBuild.configure (self)
        self.update_libtool ()
