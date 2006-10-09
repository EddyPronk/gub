import download
import gub
import targetpackage
import toolpackage

class Freetype (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='2.1.10', mirror=download.nongnu_savannah)

    def license_file (self):
        return '%(srcdir)s/docs/LICENSE.TXT' 

    def get_build_dependencies (self):
        return ['libtool', 'zlib-devel']

    def get_subpackage_names (self):
        return ['devel', '']
    
    def get_dependency_dict (self):
        return {'': ['zlib']}
        
    def configure (self):
#                self.autoupdate (autodir=os.path.join (self.srcdir (),
#                                                       'builds/unix'))

        self.system ('''
        rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
        targetpackage.TargetBuildSpec.configure (self)

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

class Freetype__local (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version='2.1.10', mirror=download.nongnu_savannah)

    def get_build_dependencies (self):
        return ['libtool']
