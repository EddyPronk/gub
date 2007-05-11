from gub import targetpackage
sf = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'
sf_gphoto = 'http://surfnet.dl.sourceforge.net/sourceforge/gphoto/%(name)s-%(ball_version)s.tar.%(format)s'

class Libgphoto2 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='2.1.6', mirror=sf_gphoto)
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
    def patch (self):
        self.wrap_pkg_config ()
    def configure_command (self):
        return ('PATH=%(srcdir)s:$PATH '
                + targetpackage.TargetBuildSpec.configure_command (self))
    def get_build_dependencies (self):
        return ['libexif', 'libjpeg', 'libusb']
    
