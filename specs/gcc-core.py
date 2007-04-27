import cross
import gcc
import mirrors
import misc
        
class Gcc_core (gcc.Gcc):
    def __init__ (self, settings):
        gcc.Gcc.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu,
                           version='4.1.1', format='bz2', name='gcc')

    def get_subpackage_names (self):
        return ['']
    def name (self):
        return 'gcc-core'
    def file_name (self):
        return 'gcc-core'
    def get_conflict_dict (self):
        return {'': ['gcc', 'gcc-devel', 'gcc-doc', 'gcc-runtime']}
    def configure_command (self):
        return (misc.join_lines (gcc.Gcc.configure_command (self) + '''
--prefix=%(cross_prefix)s
--prefix=/usr
--with-newlib
--enable-threads=no
--without-headers
--disable-shared
''')
                .replace ('enable-shared', 'disable-shared')
                .replace ('disable-static', 'enable-static')
                .replace ('enable-threads=posix', 'enable-threads=no'))
    def compile_command (self):
        return (cross.Gcc.compile_command (self) + ' all-gcc')
    def compile (self):
        cross.Gcc.compile (self)
    def install_command (self):
        return (gcc.Gcc.install_command (self)
                .replace (' install', ' install-gcc')
                #+ ' prefix=/usr/cross/core'
                )
    def install (self):
        # cross.Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
        cross.CrossToolSpec.install (self)
    def languages (self):
        return  ['c']

