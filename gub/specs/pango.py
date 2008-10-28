import re
#
from gub import misc
from gub import loggedos
from gub import targetbuild

pango_module_version_regexes = [
    (r'^1\.14', '1.5.0'),
    (r'^1\.20', '1.6.0')
    ]

class Pango (targetbuild.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/pango-1.20.0.tar.bz2'
    patches = ['pango-1.20-substitute-env.patch']
    def get_build_dependencies (self):
        return ['freetype-devel', 'fontconfig-devel', 'glib-devel', 'libtool']
    def get_dependency_dict (self):
        return {'': ['freetype', 'fontconfig', 'glib', 'libtool-runtime']}
    #FIXME: promoteme to build.py
    def configure_flags (self):
        return misc.join_lines ('''
--without-x
--without-cairo
''')
    #FIXME: promoteme to build.py
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + self.configure_flags ())

    def configure (self):
        targetbuild.AutoBuild.configure (self)                
        self.update_libtool ()

    def module_version (self):
        result = None
        version = self.version()
        for regex, candidate in pango_module_version_regexes:
            if re.match(regex, version):
                result = candidate
                break
        assert result
        return result
    
    def fix_modules (self, prefix='/usr'):
        etc = self.expand ('%(install_root)s/%(prefix)s/etc/pango', locals ())
        self.system ('mkdir -p %(etc)s' , locals ())

        def fix_prefix (logger, fname):
            loggedos.file_sub (logger, [(self.expand ('/%(prefix)s/'),
                                         '$PANGO_PREFIX/')], fname)
        pango_module_version = self.module_version()
            
        self.map_locate (fix_prefix, etc, '*')
        self.dump ('''[Pango]
ModuleFiles = $PANGO_PREFIX/etc/pango/pango.modules
ModulesPath = $PANGO_PREFIX/lib/pango/%(pango_module_version)s/modules
''' % locals (), etc + '/pangorc')
        self.copy ('%(sourcefiledir)s/pango.modules', etc)

    def install (self):
        targetbuild.AutoBuild.install (self)
        mod_version = self.module_version ()
        self.dump ("""
setfile PANGO_RC_FILE=$INSTALLER_PREFIX/etc/pango/pangorc
setdir PANGO_PREFIX=$INSTALLER_PREFIX/
set PANGO_MODULE_VERSION=%(mod_version)s
""", '%(install_prefix)s/etc/relocate/pango.reloc', env=locals ())
        self.fix_modules ()

class Pango__linux (Pango):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/pango-1.20.0.tar.bz2'
    patches = ['pango-1.20-substitute-env.patch']
    def untar (self):
        Pango.untar (self)
        # FIXME: --without-cairo switch is removed in 1.10.1,
        # pango only compiles without cairo if cairo is not
        # installed linkably on the build system.  UGH.
        self.file_sub ([('(have_cairo[_a-z0-9]*)=true', '\\1=false'),
                        ('(cairo[_a-z0-9]*)=yes', '\\1=no')],
                       '%(srcdir)s/configure')

class Pango__freebsd (Pango__linux):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/pango-1.20.0.tar.bz2'
    patches = ['pango-1.20-substitute-env.patch']
    def get_build_dependencies (self):
        return Pango__linux.get_build_dependencies (self) + ['libiconv-devel']

class Pango__darwin (Pango):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/pango-1.20.0.tar.bz2'
    patches = ['pango-1.20-substitute-env.patch']
    def configure (self):
        Pango.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')

    def install (self):
        Pango.install (self)                
        self.dump ("""
set PANGO_SO_EXTENSION=.so
""", '%(install_prefix)s/etc/relocate/pango.reloc', env=locals (), mode="a")
