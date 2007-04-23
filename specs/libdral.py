import download
import targetpackage

tvom = 'ftp://tvom/%(name)s-%(ball_version)s.tar.%(format)s'

class Libdral (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='3.2', mirror=tvom, format='gz')

    def patch (self):
        self.system ('cd %(srcdir)s && echo "Philips Research Unreleased" > LICENSE')

    def license_file (self):
        return '%(srcdir)s/LICENSE'

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        # FIXME: should patch libdral
        self.system ('''
cd %(builddir)s && install -d -m755 %(system_root)s/usr/lib
cd %(builddir)s && install -m755 .libs/libDral.so* %(system_root)s/usr/lib
cd %(builddir)s && install libDral.la %(system_root)s/usr/lib
cd %(srcdir)s && install -d %(system_root)s/usr/include/dral
cd %(srcdir)s && install -m 644 inc/*.h %(system_root)s/usr/include/dral
cd %(srcdir)s && install -m 644 dral/inc/*.h %(system_root)s/usr/include/dral
cd %(srcdir)s && install -m 644 dral_osal/inc/*.h %(system_root)s/usr/include/dral
cd %(srcdir)s && install -m 644 dral/Configuration/inc/*.h %(system_root)s/usr/include/dral
cd %(srcdir)s && install -m 644 log/inc/*.h %(system_root)s/usr/include/dral
cd %(srcdir)s && install -m 644 support/inc/*.h %(system_root)s/usr/include/dral
''')
