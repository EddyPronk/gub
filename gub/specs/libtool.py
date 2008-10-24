from gub import build
from gub import targetbuild
from gub import toolsbuild

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

class Libtool (targetbuild.TargetBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.22.tar.gz'
    #source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-1.5.26.tar.gz'
    #source = 'ftp://ftp.gnu.org/pub/gnu/libtool/libtool-2.2.6a.tar.gz'
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
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
        d = targetbuild.TargetBuild.get_subpackage_definitions (self)
        d['devel'].append (self.settings.prefix_dir + '/bin/libtool*')
        d['devel'].append (self.settings.prefix_dir + '/share/libltdl')
        return d

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

class Libtool__tools (toolsbuild.ToolsBuild):
    source = Libtool.source
    def __init__ (self, settings, source):
        toolsbuild.ToolsBuild.__init__ (self, settings, source)
        Libtool.set_sover (self)
    def configure (self):
        build.UnixBuild.configure (self)
    def install (self):
        toolsbuild.ToolsBuild.install (self)
        # FIXME: urg.  Are we doing something wrong?  Why does libtool
        # ignore [have /usr prevail over] --prefix ?
        self.file_sub ([(' (/usr/lib/*[" ])', r' %(system_prefix)s/lib \1'),
                        ('((-L| )/usr/lib/../lib/* )', r'\2%(system_prefix)s/lib \1')],
                       '%(install_root)s/%(system_prefix)s/bin/libtool')
    def wrap_executables (self):
        # The libtool script calls the cross compilers, and moreover,
        # it is copied.  Two reasons why it cannot be wrapped.
        pass
