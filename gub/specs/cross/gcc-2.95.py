from gub.specs.cross import gcc as cross_gcc

class Gcc_2_95 (cross_gcc.Gcc):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-2.95.3/gcc-everything-2.95.3.tar.gz'
    configure_flags = (cross_gcc.Gcc.configure_flags
                       .replace ('cross', 'cross_ancient')
                       + ' --build=i686-linux'
                       + ' --host=i686-linux'
                       )
    cross_ancient_dir = '%(cross_dir)s-ancient'
    cross_ancient_prefix = '%(cross_prefix)s-ancient'
    dependencies = cross_gcc.Gcc.dependencies + ['glibc']
    destdir_install_broken = True
#    def install_prefix (self):
#        return cross_gcc.Gcc.install_prefix (self) + '-ancient'
#    @context.subst_method
    def install_prefix (self):
        return '%(install_root)s%(prefix_dir)s%(cross_dir)s-ancient'
