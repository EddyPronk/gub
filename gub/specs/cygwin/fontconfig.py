#
from gub import cygwin
from gub import gup
from gub.specs import fontconfig

class Fontconfig (fontconfig.Fontconfig):
    source = 'http://www.fontconfig.org/release/fontconfig-2.4.1.tar.gz'
    configure_flags = (fontconfig.Fontconfig.configure_flags
                + ' --sysconfdir=/etc --localstatedir=/var')
    subpackage_names = ['devel', 'runtime', '']
    dependencies = gup.gub_to_distro_deps (fontconfig.Fontconfig.dependencies,
                                           cygwin.gub_to_distro_dict)
    def __init__ (self, settings, source):
        fontconfig.Fontconfig.__init__ (self, settings, source)
        self.so_version = '1'
    def category_dict (self):
        return {'': 'Libs'}
    def install (self):
        self.pre_install_smurf_exe ()
        fontconfig.Fontconfig.install (self)
        name = 'fontconfig-postinstall.sh'
        postinstall = '''#! /bin/sh
# cleanup silly symlink of previous packages
rm -f /usr/X11R6/bin/fontconfig-config
'''
        self.dump (postinstall,
                   '%(install_root)s/etc/postinstall/%(name)s',
                   env=locals ())
