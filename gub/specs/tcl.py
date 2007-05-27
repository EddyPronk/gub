from gub import mirrors
from gub import misc
from gub import targetpackage
from gub import context
 
class Tcl (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror='http://prdownloads.sourceforge.net/tcl/tcl8.4.14-src.tar.gz', version='8.4.14')
    def license_file (self):
        return "%(srcdir)s/license.terms"
    def configure_command(self):
        return "%(srcdir)s/unix/configure --prefix=%(install_prefix)s "
    def patch (self):
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/tcl-8.4.14-dde.patch")

class Tcl__mingw (Tcl):
    @context.subst_method
    def RC(self):
        return  '%(cross_prefix)s/bin/%(target_architecture)s-windres'
    
    def configure_command(self):
        return "%(srcdir)s/win/configure  --prefix=%(install_prefix)s"
