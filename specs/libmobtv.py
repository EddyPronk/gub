import download
import gub

tvom = 'ftp://oe:buildme@tvom.ddns.htc.nl.philips.com/software/openembedded/src/%(name)s-%(ball_version)s.tar.%(format)s'

class Libmobtv (gub.BinarySpec):
    def __init__ (self, settings):
        gub.BinarySpec.__init__ (self, settings)
        self.with (version='2.5.4', mirror=tvom, format='gz')

    def patch (self):
        self.system ('cd %(srcdir)s && echo "Philips Research Unreleased" > LICENSE')

    def license_file (self):
        return '%(srcdir)s/LICENSE'

    def install (self):
        # FIXME: should patch libmobtv
        self.system ('''
cd %(srcdir)s && install -d -m755 %(install_root)s/usr/lib
cd %(srcdir)s && install -m755 lib/* %(install_root)s/usr/lib
cd %(srcdir)s && install -d -m755 %(install_root)s/usr/lib/pkgconfig
cd %(srcdir)s && install -m755 share/pkgconfig/* %(install_root)s/usr/lib/pkgconfig
cd %(srcdir)s && install -d %(install_root)s/usr/include/mobtv
cd %(srcdir)s && install -m 644 inc/mobtv/* %(install_root)s/usr/include/mobtv
''')

    def package (self):
        gub.BuildSpec.package (self)

    def get_subpackage_names (self):
        return ['']
