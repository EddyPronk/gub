from gub import cross
from gub.specs.cross import gcc
from gub import mirrors
from gub import misc
        
class Gcc_core (gcc.Gcc_from_source):
    def __init__ (self, settings, source):
        gcc.Gcc_from_source.__init__ (self, settings, source)
        self.with_tarball (mirror=mirrors.gcc,
                           version='4.1.1', format='bz2', name='gcc')
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
        return (misc.join_lines (gcc.Gcc_from_source.configure_command (self)
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
    def compile (self):
        gcc.Gcc.compile (self)
    def install_command (self):
        return (gcc.Gcc.install_command (self)
                .replace (' install', ' install-gcc')
                #+ ' prefix=/usr/cross/core'
                )
    def install (self):
        # Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
        cross.CrossToolSpec.install (self)
    def languages (self):
        return  ['c']

