from gub import targetbuild

class Libiconv (targetbuild.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/libiconf/libiconv-1.11.tar.gz'
    def force_sequential_build (self):
        return True
    def get_build_dependencies (self):
        return ['gettext-devel', 'libtool']
    def configure (self):
        targetbuild.AutoBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
    def install (self):
        targetbuild.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias')
