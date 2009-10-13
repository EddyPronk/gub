from gub import build
from gub import cross
from gub import misc
from gub.specs import gcc
from gub.specs.cross import gcc as cross_gcc

class Gcc_2_95 (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-2.95.3/gcc-everything-2.95.3.tar.gz'
    configure_flags = (cross_gcc.Gcc.configure_flags
                       + ' --build=i686-linux'
                       + ' --host=i686-linux'
                       )
    cross_dir = '/cross-ancient'
    cross_prefix = '%(system_prefix)s%(cross_dir)s'
    dependencies = cross_gcc.Gcc.dependencies + ['glibc']
    parallel_build_broken = True
    make_flags = misc.join_lines ('''
tooldir='%(system_prefix)s/cross/%(target_architecture)s'
gcc_tooldir='%(prefix_dir)s/%(target_architecture)s'
''')
    destdir_install_broken = True
    
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
    def patch (self):
        cross_gcc.Gcc.patch (self)
        if self.settings.build_bits == '64':
            self.dump ('', '%(srcdir)s/libio/lowlevellock.h')
            self.dump (''' # MT_CFLAGS = -D_IO_MTSAFE_IO
MTCFLAGS='-D__extern_inline=extern inline' -D__extension__=
''', '%(srcdir)s/libio/config/mtsafe.mt')
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
            build.append_dict (self, {'LIBRARY_PATH': ':/usr/lib32'})
