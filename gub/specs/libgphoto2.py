from gub import targetpackage
sf = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'
sf_gphoto = 'http://surfnet.dl.sourceforge.net/sourceforge/gphoto/%(name)s-%(ball_version)s.tar.%(format)s'

class Libgphoto2 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
# -lltdl build problem
#        self.with_template (version='2.3.0', mirror=sf_gphoto)
# needs libexif >= 0.6.13, which we currently cannot compile/install
        self.with_template (version='2.3.1', mirror=sf_gphoto)
# Does not compile
#        self.with_template (version='2.1.6', mirror=sf_gphoto)
    def get_build_dependencies (self):
        return ['libexif', 'libjpeg', 'libusb']
    def wrap_pkg_config (self):
        self.dump ('''#! /bin/sh
/usr/bin/pkg-config\
  --define-variable prefix=%(system_root)s/usr\
  --define-variable includedir=%(system_root)s/usr/include\
  --define-variable libdir=%(system_root)s/usr/lib\
  "$@"
''',
                   '%(srcdir)s/pkg-config')
        import os
        os.chmod (self.expand ('%(srcdir)s/pkg-config'), 0755)
    def wrap_libusb_config (self):
        self.dump ('''#! /bin/sh
/usr/bin/libusb-config\
  --prefix=%(system_root)s/usr\
  "$@"
''',
                   '%(srcdir)s/libusb-config')
        import os
        os.chmod (self.expand ('%(srcdir)s/libusb-config'), 0755)
    def patch (self):
        self.wrap_pkg_config ()
        self.wrap_libusb_config ()
    def configure_command (self):
        return ('PATH=%(srcdir)s:$PATH '
                + targetpackage.TargetBuildSpec.configure_command (self))
    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
    def makeflags (self):
        return """ libgphoto2_port_la_DEPENDENCIES='$(top_srcdir)/gphoto2/gphoto2-port-version.h $(top_srcdir)/gphoto2/gphoto2-port-library.h $(srcdir)/libgphoto2_port.sym' libgphoto2_la_DEPENDENCIES='$(top_srcdir)/gphoto2/gphoto2-version.h $(srcdir)/libgphoto2.sym' LDFLAGS='-Wl,--rpath-link,%(system_root)s/usr/lib'"""

