import targetpackage

class Libiconv (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='1.9.2', builddeps=['gettext', 'libtool'])

    def configure (self):
        targetpackage.Target_package.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
    def install (self):
        targetpackage.Target_package.install (self)
        self.system ('rm %(install_root)s/usr/lib/charset.alias')
        
