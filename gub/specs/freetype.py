from gub import mirrors
from gub import gubb
from gub import targetpackage
from gub import toolpackage

class Freetype (targetpackage.TargetBuildSpec):
    '''Software font engine
FreeType is a software font engine that is designed to be small,
efficient, highly customizable and portable while capable of producing
high-quality output (glyph images). It can be used in graphics
libraries, display servers, font conversion tools, text image generation
tools, and many other products as well.'''

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_template (version='2.1.10', mirror=mirrors.nongnu_savannah)

    def license_file (self):
        return '%(srcdir)s/docs/LICENSE.TXT'

    def get_build_dependencies (self):
        return ['libtool-devel', 'zlib-devel']

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

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()

        self.file_sub ([('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX')], '%(builddir)s/Makefile')

    def munge_ft_config (self, file):
        self.file_sub ([('\nprefix=[^\n]+\n',
                         '\nlocal_prefix=yes\nprefix=%(system_root)s/usr\n')],
                       file, must_succeed=True)

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        # FIXME: this is broken.  for a sane target development package,
        # we want /usr/bin/freetype-config must survive.
        # While cross building, we create an  <toolprefix>-freetype-config
        # and prefer that.
        self.system ('mkdir -p %(install_root)s/usr/cross/bin/')
        self.system ('mv %(install_root)s/usr/bin/freetype-config %(install_root)s/usr/cross/bin/freetype-config')
        self.munge_ft_config ('%(install_root)s/usr/cross/bin/freetype-config')

class Freetype__mingw (Freetype):
    def configure (self):
        Freetype.configure (self)
        self.dump ('''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''',
             '%(builddir)s/Makefile',
             mode='a')

class XFreetype__cygwin (Freetype):
    def __init__ (self, settings):
        Freetype.__init__ (self, settings)
        self.with_template (version='2.1.10', mirror=mirrors.nongnu_savannah)
        self.so_version = '6'

    def patch (self):
        Freetype.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/freetype-libtool-no-version.patch')

    def get_subpackage_definitions (self):
        d = dict (Freetype.get_subpackage_definitions (self))
        # urg, must remove usr/share. Because there is no doc package,
        # runtime iso '' otherwise gets all docs.
        d['runtime'] = ['/usr/bin/*dll', '/usr/lib/*.la']
        return d

    def get_subpackage_names (self):
        #return ['devel', 'doc', '']
        return ['devel', 'runtime', '']

    def get_build_dependencies (self):
        return ['libtool']
    
    def get_dependency_dict (self):
        return {
            '': ['libfreetype26'],
            'devel': ['libfreetype26'],
            'runtime': ['zlib'],
            }

    def category_dict (self):
        return {'': 'libs',
                'runtime': 'libs',
                'devel': 'devel libs',
                'doc': 'doc'}

    def configure_command (self):
        return (Freetype.configure_command (self)
                + ' --sysconfdir=/etc --localstatedir=/var')

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        self.pre_install_smurf_exe ()

class Freetype__local (toolpackage.ToolBuildSpec, Freetype):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (version='2.1.10', mirror=mirrors.nongnu_savannah)

    def get_build_dependencies (self):
        # local is not split
        #return ['libtool-devel']
        return ['libtool']

    # FIXME, mi-urg?
    def license_file (self):
        return Freetype.license_file (self)

    def install (self):
        toolpackage.ToolBuildSpec.install (self)
        self.munge_ft_config ('%(install_root)s/%(local_prefix)s/bin/.freetype-config')
