import download
import targetpackage
import gub

class Zlib (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
	self.with (version='1.2.2',
                   mirror='http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.2.tar.gz')
        
    def patch (self):
        targetpackage.TargetBuildSpec.patch (self)

        self.system ('cp %(sourcefiledir)s/zlib.license %(license_file)s')
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/zlib-1.2.2-windows.patch')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def compile_command (self):
        return targetpackage.TargetBuildSpec.compile_command (self) + ' ARFLAGS=r '
    
    def configure_command (self):
        zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.2'

        ### UGH.
        if self.settings.platform.startswith ('mingw'):
            zlib_is_broken = 'target=mingw'

        ## doesn't use autoconf configure.
        return zlib_is_broken + ' %(srcdir)s/configure --shared '

    def install_command (self):
        return targetpackage.TargetBuildSpec.broken_install_command (self)



class Zlib__mingw (Zlib):
    def patch (self):
        Zlib.patch (self)
        self.file_sub ([("='/bin/true'", "='true'"),
                        ('mgwz','libz'),
                        ],
                       '%(srcdir)s/configure')
