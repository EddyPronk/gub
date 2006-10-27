import gub

class Urw_fonts (gub.BinarySpec):
    def __init__ (self, settings):
        gub.BinarySpec.__init__ (self, settings)
        self.with(version="1.0.7pre41",
                  mirror="ftp://ftp.gnome.ru/fonts/urw/release/urw-fonts-%(version)s.tar.bz2",
                  strip_dir=False)
    def compile (self):
        self.system ('cd %(srcdir)s/ &&  rm README* COPYING ChangeLog TODO')

    def install (self):
        self.system ('mkdir -p %(install_root)s/usr/share/fonts/default/Type1')
        self.system ('cp %(srcdir)s/* %(install_root)s/usr/share/fonts/default/Type1/')
    def package (self):
        gub.BuildSpec.package (self)
    def get_subpackage_names (self):
        return ['']

