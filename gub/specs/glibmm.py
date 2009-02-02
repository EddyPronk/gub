from gub import target

class Glibmm (target.AutoBuild):
#    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.12/glibmm-2.12.10.tar.gz'
    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.18/glibmm-2.18.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glib', 'libsig++']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': self._get_build_dependencies ()}
    ## FIXME: tools.configure () always updates libtool
    ## why no in target.py // 18 packages do this??
    def configure (self):
        target.AutoBuild.configure (self)
        self.update_libtool ()
