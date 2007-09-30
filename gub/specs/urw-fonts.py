from gub import build

class Urw_fonts (build.BinaryBuild):
    def __init__ (self, settings):
        build.BinaryBuild.__init__ (self, settings)

        self.with_template (version='1.0.7pre41',
                   mirror='ftp://ftp.gnome.ru/fonts/urw/release/urw-fonts-%(version)s.tar.bz2')
        self.source.strip_components = 0
    def compile (self):
        self.system ('cd %(srcdir)s && rm README* COPYING ChangeLog TODO')
    def install (self):
        self.system ('mkdir -p %(install_prefix)s/share/fonts/default/Type1')
        self.system ('cp %(srcdir)s/* %(install_prefix)s/share/fonts/default/Type1/')
    def package (self):
        build.UnixBuild.package (self)
    def get_subpackage_names (self):
        return ['']

