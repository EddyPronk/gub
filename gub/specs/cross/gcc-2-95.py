import os
#
from gub import build
from gub import cross
from gub import loggedos
from gub import misc
from gub.specs import gcc
from gub.specs.cross import gcc as cross_gcc


def move_target_libs (self, libdir):
    self.system ('mkdir -p %(install_prefix)s/lib || true')
    def move_target_lib (logger, file_name):
        base = os.path.split (self.expand (file_name))[1]
        new_name = os.path.join (self.expand ('%(install_prefix)s%(cross_dir)s/lib'), base)
        if os.path.islink (file_name):
            target = os.path.basename (misc.delinkify (file_name))
            loggedos.symlink (logger, target, new_name)
        else:
            loggedos.rename (logger, file_name, new_name)
    for suf in ['.a', '.la', '.so.*', '.dylib']:
        self.map_find_files (move_target_lib, libdir, 'lib.*%(suf)s' % locals ())
                            
class Gcc_2_95 (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-2.95.3/gcc-everything-2.95.3.tar.gz'
    configure_flags = (cross_gcc.Gcc.configure_flags
                       .replace ('%(cross_prefix)s/bin', '%(system_prefix)s/cross/bin')
                       + ' --build=i686-linux'
                       + ' --host=i686-linux'
                       )
    cross_dir = '/cross-ancient'
    cross_prefix = '%(system_prefix)s%(cross_dir)s'
    dependencies = cross_gcc.Gcc.dependencies + ['glibc']
    parallel_build_broken = True
    # weird, what about /bin?
    # tooldir='%(system_prefix)s/cross/%(target_architecture)s'
    # gcc_tooldir='%(prefix_dir)s/%(target_architecture)s'
    make_flags = misc.join_lines ('''
tooldir='%(system_prefix)s/cross/%(target_architecture)s'
gcc_tooldir='%(cross_prefix)s/%(target_architecture)s'
''')
    destdir_install_broken = True
    install_flags = (cross_gcc.Gcc.install_flags
                     .replace ('prefix=%(prefix_dir)s',
                               'prefix=%(install_prefix)s'))
    install_flags_destdir_broken = (cross_gcc.Gcc.install_flags_destdir_broken
#                                    .replace ('((aclocaldir|bindir|datadir|exec_prefix|gcc_tooldir|includedir|xinfodir|libdir|libexecdir|xmandir|xprefix|sysconfdir|tooldir)=%[(]install_prefix[)]s)', r'\1%(cross_dir)s')
                                    .replace ('%(install_prefix)s', r'%(install_prefix)s%(cross_dir)s')
                                    .replace ('bindir=%(install_prefix)s%(cross_dir)s/bin',
                                              'bindir=%(install_prefix)s/%(cross_dir)s/%(target_architecture)s/bin')
                                    .replace ('infodir=%(install_prefix)s%(cross_dir)s',
                                              'infodir=%(install_prefix)s')
                                    .replace ('mandir=%(install_prefix)s%(cross_dir)s',
                                              'mandir=%(install_prefix)s')
                                    + ' gxx_include_dir=%(install_prefix)s%(cross_dir)s/include/g++-3'
                                    )
    def get_subpackage_definitions (self):
        d = cross_gcc.Gcc.get_subpackage_definitions (self)
        d['c++-runtime'] = [self.expand ('%(prefix_dir)s%(cross_dir)s/lib/libstdc++*so*')]
        return d
    def pre_install (self):
        cross.AutoBuild.pre_install (self)
        # Only id <PREFIX>/<TARGET-ARCH>/bin exists, gcc's install installs
        # the plain gcc drivers without <TOOLCHAIN-PREFIX>gcc
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/%(target_architecture)s/bin')
    def install (self):
        # Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
#        cross_gcc.Gcc.install (self)
        cross.AutoBuild.install (self)
        gcc.install_missing_archprefix_binaries (self)
        move_target_libs (self, '%(install_prefix)s%(cross_dir)s/lib/gcc-lib/%(target_architecture)s')
    def patch (self):
        cross_gcc.Gcc.patch (self)
        # Hmm? fixed in glibc-2.3.5-10 ? http://bugs.gentoo.org/63793
        self.dump ('''
/* Initializer for compatibility lock.  */
#define LLL_MUTEX_LOCK_INITIALIZER              (0)
#define LLL_MUTEX_LOCK_INITIALIZER_LOCKED       (1)

/* Initializers for lock.  */
#define LLL_LOCK_INITIALIZER            (0)
#define LLL_LOCK_INITIALIZER_LOCKED     (1)

''', '%(srcdir)s/libio/lowlevellock.h')
        for i in ['%(srcdir)s/libio/config/mtsafe.mt',
                  '%(srcdir)s/libstdc++/config/linux.mt']:
            # _IO_MTSAFE_IO has problems, so comment out
            # MT_CFLAGS seems to be only way to get flags into build?
            self.dump ('''
MT_CFLAGS = -D_IO_MTSAFE_IO '-D__extern_inline=extern inline' -D__extension__=
''', i)
        self.system ('mkdir -p %(srcdir)s/libio/bits')
        self.dump ('''
#ifdef __cplusplus
extern "C" {
#endif
#include_next <bits/libc-lock.h>
asm (".weak _pthread_cleanup_pop_restore");
asm (".weak _pthread_cleanup_push_defer");
#ifdef __cplusplus
}
#endif
''',
                       '%(srcdir)s/libio/bits/libc-lock.h')
        # PROMOTEME: gcc_do_not_look_in_slash_lib_usr
        self.file_sub ([
                ('([ *]standard_(startfile|exec)_prefix_.*= ")(/lib|/usr)', r'\1%(system_root)s\3')],
                       '%(srcdir)s/gcc/gcc.c')
        # PROMOTEME: gcc_do_not_look_in_slash_lib_usr
        for i in [
            '%(srcdir)s/gcc/cccp.c',
            '%(srcdir)s/gcc/cppinit.c',
            '%(srcdir)s/gcc/protoize.c',
            ]:
            self.file_sub ([
                    ('(define STANDARD_INCLUDE_DIR ")(/usr)', r'\1%(system_root)s\2')],
                           i)
    def __init__ (self, settings, source):
        cross_gcc.Gcc.__init__ (self, settings, source)
        if self.settings.build_bits == '64':
            # Allow building on 64 bits buid platform
            # [requires: apt-get install gcc-multilib]
            self.configure_command = (''' CC='gcc -m32 -D_FORTIFY_SOURCE=0' '''
                                      + self.configure_command)
            self.make_flags += (''' CFLAGS='-g -Wa,--32 -Wl,--architecture=i686-linux' '''
                                + ''' libc_interface=-libc6.3 '''
                                )
