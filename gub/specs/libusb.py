from gub import targetbuild

class Libusb (targetbuild.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libusb-0.1.12.tar.gz'
    def configure (self):
        targetbuild.AutoBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
