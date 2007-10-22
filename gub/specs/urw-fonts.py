from gub import build
from gub import mirrors

class Urw_fonts (build.BinaryBuild):
    source = mirrors.with_template (name='urw-fonts', version='1.0.7pre41',
                                    mirror='ftp://ftp.gnome.ru/fonts/urw/release/urw-fonts-%(version)s.tar.bz2&strip_components=0')
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        # FIXME: TODO: find nice way to pass strip_components
        # parameter to TarBall
        print 'FIXME: serialization:', __file__, ': strip-components'
        source.strip_components = 0
    def compile (self):
        self.system ('cd %(srcdir)s && rm README* COPYING ChangeLog TODO')
    def install (self):
        self.system ('mkdir -p %(install_prefix)s/share/fonts/default/Type1')
        self.system ('cp %(srcdir)s/* %(install_prefix)s/share/fonts/default/Type1/')
    def package (self):
        build.UnixBuild.package (self)
    def get_subpackage_names (self):
        return ['']

