from gub import build

class Urw_fonts (build.BinaryBuild):
    source = 'ftp://ftp.gnome.ru/fonts/urw/release/urw-fonts-1.0.7pre41.tar.bz2&strip=0'
    def compile (self):
        self.system ('cd %(srcdir)s && rm README* COPYING ChangeLog TODO')
    def install (self):
        self.system ('mkdir -p %(install_prefix)s/share/fonts/default/Type1')
        self.system ('cp %(srcdir)s/* %(install_prefix)s/share/fonts/default/Type1/')
    def package (self):
        build.AutoBuild.package (self)
    def get_subpackage_names (self):
        return ['']
