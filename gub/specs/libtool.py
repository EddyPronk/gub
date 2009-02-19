#
from gub import context
from gub import misc
from gub import repository
from gub import target
from gub import tools

class Libtool (target.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-2.2.6a.tar.gz'
    #source = 'git://git.sv.gnu.org/libtool.git?branch=master&revision=77e114998457cb6170ad84b360cb5b9be90f2191'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        # repository patched in method.
        def version_from_VERSION (self):
            return '2.2.7'
        if isinstance (source, repository.Git):
            source.version = misc.bind_method (version_from_VERSION, source)
            source._version = '2.2.7'
        Libtool.set_sover (self)
    def _get_build_dependencies (self):
        if isinstance (self.source, repository.Git):
            return ['tools::libtool', 'tools::automake']
        return ['tools::libtool']
    def autoupdate (self):
        # automagic works, but takes forever
        if isinstance (self.source, repository.Git):
            self.system ('cd %(srcdir)s && reconfdirs=". libltdl" ./bootstrap')
    @staticmethod
    def set_sover (self):
        # FIXME: how to automate this?
        self.so_version = '3'
        if self.source._version in ('2.2.4', '2.2.6.a', '2.2.7'):
            self.so_version = '7'
    def get_subpackage_names (self):
        return ['devel', 'doc', 'runtime', '']
    def get_subpackage_definitions (self):
        d = target.AutoBuild.get_subpackage_definitions (self)
        d['devel'].append (self.settings.prefix_dir + '/bin/libtool*')
        d['devel'].append (self.settings.prefix_dir + '/share/libltdl')
        return d
    def update_libtool (self):
        pass
    def config_cache_overrides (self, string):
        # Workraound for bug in libtool-2.2.6a: it will use CC=$F77
        # (==/usr/bin/gfortran) -print-search-dirs instead of
        # <cross-toolchain-prefix>-gcc -print-search-dirs to determine
        # sys_lib_search_path_spec; breaking all linkages.
        # http://lists.gnu.org/archive/html/bug-libtool/2009-02/msg00017.html
        return (string
                + '''
ac_cv_prog_F77=${ac_cv_prog_F77=no}
ac_cv_prog_FC=${ac_cv_prog_FC=no}
ac_cv_prog_GCJ=${ac_cv_prog_GCJ=no}
''')
    def configure_command (self):
        # libtool's build breaks with SHELL=; CONFIG_SHELL works
        # and adds dash to libtools' #! 
        SHELL = ''
        if 'stat' in misc.librestrict ():
            SHELL = 'CONFIG_SHELL=%(tools_prefix)s/bin/dash '
        return (SHELL
                + target.AutoBuild.configure_command (self)
                .replace ('SHELL=', 'CONFIG_SHELL='))

class Libtool__darwin (Libtool):
    def install (self):
        Libtool.install (self)
        ## necessary for programs that load dynamic modules.
        self.dump ("prependdir DYLD_LIBRARY_PATH=$INSTALLER_PREFIX/lib",
                   '%(install_prefix)s/etc/relocate/libtool.reloc')

class Libtool__cygwin (Libtool):
    def only_for_cygwin_untar (self):
        cygwin.untar_cygwin_src_package_variant2 (self, self.file_name ())
    # FIXME: we do most of this for all cygwin packages
    def get_dependency_dict (self): #cygwin
        d = Libtool.get_dependency_dict (self)
        d[''].append ('cygwin')
        return d
    def category_dict (self):
        return {'': 'Devel'}
    def install (self):
        Libtool.install (self)
        # configure nowadays (what m4?) has hardcoded /usr and /lib for Cygwin
        # instead of asking gcc
        self.file_sub ([('sys_lib_search_path_spec="/usr/lib /lib/w32api /lib /usr/local/lib"', 'sys_lib_search_path_spec="%(system_prefix)s/lib %(system_prefix)s/lib/w32api %(system_prefix)s/lib %(system_prefix)s/bin"')], '%(install_prefix)s/bin/libtool')

class Libtool__tools (tools.AutoBuild, Libtool):
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        Libtool.set_sover (self)
        # Uncommenting removes IGNORE lifting from make and breaks build.
        # target.add_target_dict (self, {'LIBRESTRICT_IGNORE': ''})
        '''
        /home/janneke/tmp/gub/target/tools/root/usr/bin/make: tried to xstat () file /usr/include/stdio.h
allowed:
  /home/janneke/tmp/gub/target
  /usr/lib/gcc
  /tmp
  /dev/null
/bin/bash: line 22: 25332 Aborted                 (core dumped) make "$target-am"
'''
    def update_libtool (self):
        pass
    def install (self):
        tools.AutoBuild.install (self)
        # FIXME: urg.  Are we doing something wrong?  Why does libtool
        # ignore [have /usr prevail over] --prefix ?
        self.file_sub ([(' (/usr/lib/*[" ])', r' %(system_prefix)s/lib \1'),
                        ('((-L| )/usr/lib/../lib/* )', r'\2%(system_prefix)s/lib \1')],
                       '%(install_root)s/%(system_prefix)s/bin/libtool')
    def wrap_executables (self):
        # The libtool script calls the cross compilers, and moreover,
        # it is copied.  Two reasons why it cannot be wrapped.
        pass
