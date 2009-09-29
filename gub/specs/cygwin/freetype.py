#
from gub import cygwin
from gub import gup
from gub import target
from gub.specs import freetype

class XFreetype (freetype.Freetype):
    source = 'http://download.savannah.nongnu.org/releases/freetype/freetype-2.1.10.tar.gz&name=freetype'
    patches = ['freetype-libtool-no-version.patch']
    configure_flags = (freetype.Freetype.configure_flags
                + ' --sysconfdir=/etc --localstatedir=/var')
    subpackage_names = ['devel', 'runtime', '']
    dependencies = gup.gub_to_distro_deps (freetype.Freetype.dependencies,
                                           cygwin.gub_to_distro_dict)
    def __init__ (self, settings, source):
        freetype.Freetype.__init__ (self, settings, source)
        self.so_version = '6'
    def category_dict (self):
        return {'': 'Libs'}
    def install (self):
        self.pre_install_smurf_exe ()
        target.AutoBuild.install (self)
