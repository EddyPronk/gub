from gub import cross
from gub import misc
from gub.specs import gcc
from gub.specs.cross import gcc as cross_gcc

class Gcc_2_95 (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-2.95.3/gcc-everything-2.95.3.tar.gz'
    configure_flags = (cross_gcc.Gcc.configure_flags
#                       .replace ('(%[(]cross_prefix[)]s)', r'\1%(cross_suffix)s')
                       + ' --build=i686-linux'
                       + ' --host=i686-linux'
                       )
#    cross_suffix = '-ancient'
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
                                    .replace ('((aclocaldir|bindir|datadir|exec_prefix|gcc_tooldir|includedir|xinfodir|libdir|libexecdir|xmandir|xprefix|sysconfdir|tooldir)=%[(]install_prefix[)]s)', r'\1/%(cross_dir)s')
                                    .replace ('bindir=%(install_prefix)s%(cross_dir)s/bin',
                                              'bindir=%(install_prefix)s/%(cross_dir)s/%(toolchain_prefix)s'))
    def install (self):
        # Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
#        cross_gcc.Gcc.install (self)
        cross.AutoBuild.install (self)
        gcc.install_missing_archprefix_binaries (self)
    def __init__ (self, settings, source):
        cross_gcc.Gcc.__init__ (self, settings, source)
        if self.settings.build_bits == '64':
            self.configure_command = (''' CFLAGS='-m32 -D_FORTIFY_SOURCE=0' '''
                                      + self.configure_command)
