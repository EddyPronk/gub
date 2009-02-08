from gub import target

class Libiconv (target.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/libiconf/libiconv-1.11.tar.gz'
    def force_sequential_build (self):
        return True
    def _get_build_dependencies (self):
        return ['gettext-devel', 'libtool']
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias')
