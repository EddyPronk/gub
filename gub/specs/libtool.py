from gub import build
from gub import target
from gub import tools

# FIXME, need for WITH settings when building dependency 'libtool'
# This works without libtool.py:
#    ./gub-builder.py -p mingw build http://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.20.tar.gz

'''
report bug:
libtool: link: i686-mingw32-gcc -mwindows -mms-bitfields -shared  libltdl/loaders/.libs/libltdl_libltdl_la-preopen.o libltdl/.libs/libltdl_libltdl_la-lt__alloc.o libltdl/.libs/libltdl_libltdl_la-lt_dlloader.o libltdl/.libs/libltdl_libltdl_la-lt_error.o libltdl/.libs/libltdl_libltdl_la-ltdl.o libltdl/.libs/libltdl_libltdl_la-slist.o libltdl/.libs/argz.o libltdl/.libs/lt__strl.o libltdl/.libs/libltdlS.o  libltdl/.libs/libltdl.lax/dlopen.a/dlopen.o  libltdl/.libs/libltdl.lax/loadlibrary.a/loadlibrary.o   -L/home/janneke/vc/gub/target/mingw/root/usr/lib -L/home/janneke/vc/gub/target/mingw/root/usr/bin -L/home/janneke/vc/gub/target/mingw/root/usr/lib/w32api  -mwindows -mms-bitfields   -o libltdl/.libs/libltdl-7.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker libltdl/.libs/libltdl.dll.a
Creating library file: libltdl/.libs/libltdl.dll.alibltdl/.libs/libltdl.lax/dlopen.a/dlopen.o: In function `vm_sym':
/home/janneke/vc/gub/target/mingw/src/libtool-2.2.6.a/libltdl/loaders/dlopen.c:227: undefined reference to `_dlsym'
libltdl/.libs/libltdl.lax/dlopen.a/dlopen.o: In function `vm_close':
/home/janneke/vc/gub/target/mingw/src/libtool-2.2.6.a/libltdl/loaders/dlopen.c:212: undefined reference to `_dlclose'
libltdl/.libs/libltdl.lax/dlopen.a/dlopen.o: In function `vm_open':
/home/janneke/vc/gub/target/mingw/src/libtool-2.2.6.a/libltdl/loaders/dlopen.c:194: undefined reference to `_dlopen'
collect2: ld returned 1 exit status
'''

class Libtool (target.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.22.tar.gz'
    #source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.26.tar.gz'
    #source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-2.2.6a.tar.gz'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        Libtool.set_sover (self)
    def get_build_dependencies (self):
        return ['tools::libtool']
    @staticmethod
    def set_sover (self):
        # FIXME: how to automate this?
        self.so_version = '3'
        if self.source._version in ('2.2.4', '2.2.6.a'):
            self.so_version = '7'
    def get_subpackage_names (self):
        return ['devel', 'doc', 'runtime', '']
    def get_dependency_dict (self):
        return { '': ['libtool-runtime'],
                 'devel' : ['libtool'],
                 'doc' : [],
                 'runtime': [],}
    def get_subpackage_definitions (self):
        d = target.AutoBuild.get_subpackage_definitions (self)
        d['devel'].append (self.settings.prefix_dir + '/bin/libtool*')
        d['devel'].append (self.settings.prefix_dir + '/share/libltdl')
        return d
    def update_libtool (self):
        pass

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
    def get_dependency_dict (self):
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

class Libtool__tools (tools.AutoBuild):
    source = Libtool.source
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        Libtool.set_sover (self)
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
