import gub

class Urw_fonts (gub.Binary_package):
    def __init__ (self, settings):
        gub.Binary_package.__init__ (self, settings)
        self.with(version="1.0.7pre41",
                  mirror="ftp://ftp.gnome.ru/fonts/urw/release/urw-fonts-%(version)s.tar.bz2")
    def install (self):
        self.system ('mkdir -p %(install_root)s/usr/share/fonts/default/Type1')
        self.system ('cp %(srcdir)s/root/* %(install_root)s/usr/share/fonts/default/Type1/')
    def package (self):
        gub.Package.package (self)
    

