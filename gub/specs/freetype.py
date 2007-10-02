from gub import mirrors
from gub import build
from gub import targetbuild
from gub import toolsbuild

class Freetype (targetbuild.TargetBuild):
    '''Software font engine
FreeType is a software font engine that is designed to be small,
efficient, highly customizable and portable while capable of producing
high-quality output (glyph images). It can be used in graphics
libraries, display servers, font conversion tools, text image generation
tools, and many other products as well.'''

    source = mirrors.with_template (name='freetype', version='2.1.10', mirror=mirrors.nongnu_savannah)

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
        targetbuild.TargetBuild.configure (self)

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()

        self.file_sub ([('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX')], '%(builddir)s/Makefile')

    def munge_ft_config (self, file):
        self.file_sub ([('\nprefix=[^\n]+\n',
                         '\nlocal_prefix=yes\nprefix=%(system_prefix)s\n')],
                       file, must_succeed=True)

    def install (self):
        targetbuild.TargetBuild.install (self)
        # FIXME: this is broken.  for a sane target development package,
        # we want /usr/bin/freetype-config must survive.
        # While cross building, we create an  <toolprefix>-freetype-config
        # and prefer that.
        self.system ('mkdir -p %(install_prefix)s/cross/bin/')
        self.system ('mv %(install_prefix)s/bin/freetype-config %(install_prefix)s/cross/bin/freetype-config')
        self.munge_ft_config ('%(install_prefix)s/cross/bin/freetype-config')

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
    source = mirrors.with_template (name='freetype', version='2.1.10', mirror=mirrors.nongnu_savannah)
    def __init__ (self, settings, source):
        Freetype.__init__ (self, settings, source)
        self.so_version = '6'

    def patch (self):
        Freetype.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/freetype-libtool-no-version.patch')

    def get_subpackage_definitions (self):
        d = dict (Freetype.get_subpackage_definitions (self))
        # urg, must remove usr/share. Because there is no doc package,
        # runtime iso '' otherwise gets all docs.
        d['runtime'] = [self.settings.prefix_dir + '/bin/*dll',
                        self.settings.prefix_dir + '/lib/*.la']
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
        return {'': 'Libs'}

    def configure_command (self):
        return (Freetype.configure_command (self)
                + ' --sysconfdir=/etc --localstatedir=/var')

    def install (self):
        targetbuild.TargetBuild.install (self)
        self.pre_install_smurf_exe ()

class Freetype__tools (toolsbuild.ToolsBuild, Freetype):
    def get_build_dependencies (self):
        # tools is not split
        #return ['libtool-devel']
        return ['libtool']
    # FIXME, mi-urg?
    def license_file (self):
        return Freetype.license_file (self)
    def install (self):
        toolsbuild.ToolsBuild.install (self)
        self.munge_ft_config ('%(install_root)s/%(tools_prefix)s/bin/.freetype-config')
