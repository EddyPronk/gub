import download
import gub
import targetpackage
import toolpackage

class Freetype (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='2.1.10', mirror=download.nongnu_savannah,
             builddeps=['libtool', 'zlib'])

    def configure (self):
#                self.autoupdate (autodir=os.path.join (self.srcdir (),
#                                                       'builds/unix'))

        gub.Package.system (self, '''
        rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
        targetpackage.Target_package.configure (self)

        # # FIXME: libtool too old for cross compile
        self.update_libtool ()

        self.file_sub ([('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX')], '%(builddir)s/Makefile')

class Freetype__mingw (Freetype):
    def configure (self):
        Freetype.configure (self)
        self.dump ('''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''',
             '%(builddir)s/Makefile',
             mode='a')

class Freetype__local (toolpackage.Tool_package):
    def __init__ (self, settings):
        toolpackage.Tool_package.__init__ (self, settings)
        self.with (version='2.1.10', mirror=download.nongnu_savannah,
             builddeps=['libtool'])
        
