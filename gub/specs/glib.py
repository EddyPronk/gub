from gub import tools
from gub import target

class Glib (target.AutoBuild):
    ## 2.12.4 : see bug  http://bugzilla.gnome.org/show_bug.cgi?id=362918
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/glib-2.16.1.tar.bz2'
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.25/2.25.5/sources/glib-2.19.5.tar.gz'
    def _get_build_dependencies (self):
        return ['gettext-devel', 'libtool']
    def config_cache_overrides (self, str):
        return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias',
                     ignore_errors=True)
        
class Glib__darwin (Glib):
    def configure (self):
        Glib.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')

class Glib__darwin__x86 (Glib__darwin):
    def compile (self):
        self.file_sub ([('(SUBDIRS = .*) tests', r'\1'),
                        (r'GTESTER = \$.*', ''),
                        ('am__EXEEXT_2 = gtester.*', ''),
                        ('am__append_. *= *gtester', '')],
                       '%(builddir)s/glib/Makefile', must_succeed=True)
        Glib__darwin.compile (self)
        
class Glib__mingw (Glib):
    def _get_build_dependencies (self):
        return Glib._get_build_dependencies (self) + ['libiconv-devel']

class Glib__freebsd (Glib):
    patches = ['glib-2.12.12-disable-threads.patch']
    def _get_build_dependencies (self):
        return Glib._get_build_dependencies (self) + ['libiconv-devel']
    def configure_command (self):
        return Glib.configure_command (self) + ' --disable-threads'
        
class Glib__freebsd__64 (Glib__freebsd):
    patches = Glib__freebsd.patches
    def configure_command (self):
        return Glib.configure_command (self) + ' --disable-threads --disable-timeloop'

class Glib__tools (tools.AutoBuild):
    source = Glib.source
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('rm %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/lib/charset.alias',
                         ignore_errors=True)
    def _get_build_dependencies (self):
        return ['gettext', 'libtool']            
