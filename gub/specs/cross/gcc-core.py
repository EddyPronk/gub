from gub import cross
from gub.specs.cross import gcc
from gub import misc
        
class Gcc_core (gcc.Gcc__from__source):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.1/gcc-4.1.1.tar.bz2'
    def get_build_dependencies (self):
        return gcc.Gcc.get_build_dependencies (self)
    def get_subpackage_names (self):
        return ['']
    def name (self):
        return 'cross/gcc-core'
    def file_name (self):
        return 'gcc-core'
    def get_conflict_dict (self):
        return {'': ['cross/gcc', 'cross/gcc-devel', 'cross/gcc-doc', 'cross/gcc-runtime']}
    def configure_command (self):
        return (misc.join_lines (gcc.Gcc__from__source.configure_command (self)
                                 + '''
--prefix=%(cross_prefix)s
--prefix=%(prefix_dir)s
--with-newlib
--enable-threads=no
--without-headers
--disable-shared
''')
                .replace ('enable-shared', 'disable-shared')
                .replace ('disable-static', 'enable-static')
                .replace ('enable-threads=posix', 'enable-threads=no'))
    def compile_command (self):
        return (gcc.Gcc.compile_command (self) + ' all-gcc')
    def install_command (self):
        return (gcc.Gcc.install_command (self)
                .replace (' install', ' install-gcc'))
    def install (self):
        # Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
        cross.AutoBuild.install (self)
    def languages (self):
        return  ['c']

