import targetpackage
from toolpackage import Tool_package

# FIXME, need for WITH settings when building dependency 'libtool'
# This works without libtool.py:
#    ./gub-builder.py -p mingw build http://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.20.tar.gz

class Libtool (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='1.5.20')

class Libtool__local (Tool_package):
    def __init__ (self, settings):
        ##ug.h
        Tool_package.__init__ (self, settings)
        self.with (version='1.5.20')



class Libtool__darwin (Libtool):
    def install (self):
        Libtool.install (self)
        self.dump ("prependdir DYLD_LIBRARY_PATH=$INSTALLER_ROOT/usr/lib"
                   '%(install_root)s/usr/etc/relocate/libtool.reloc')
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='1.5.20')
