import cross
import misc

class Gcc (cross.Gcc):
    #FIXME: what about apply_all (%(patchdir)s/%(version)s)?
    def patch (self):
        if self.vc_repository._version == '4.1.1':
            self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-4.1.1-ppc-unwind.patch
''')
    def get_build_dependencies (self):
        return cross.Gcc.get_build_dependencies (self) + ['gcc-core', 'glibc-core']
    def get_conflict_dict (self):
        return {'': ['gcc-core'], 'doc': ['gcc-core'], 'runtime': ['gcc-core']}
    def configure_command (self):
        return (cross.Gcc.configure_command (self)
                + misc.join_lines ('''
--with-local-prefix=%(system_root)s/usr
--disable-multilib
--disable-nls
--enable-threads=posix
--enable-__cxa_atexit
--enable-symvers=gnu
--enable-c99 
--enable-clocale=gnu 
--enable-long-long
'''))
    def install (self):
        cross.Gcc.install (self)
        self.system ('''
mv %(install_root)s/usr/cross/lib/gcc/%(target_architecture)s/%(version)s/libgcc_eh.a %(install_root)s/usr/lib
''')
        
class Gcc_core (Gcc):
    def __init__ (self, settings):
        Gcc.__init__ (self, settings)
    def get_subpackage_names (self):
        return ['']
    def name (self):
        return 'gcc-core'
    def file_name (self):
        return 'gcc-core'
    def get_build_dependencies (self):
        return cross.Gcc.get_build_dependencies (self) + ['binutils']
    def get_conflict_dict (self):
        return {'': ['gcc', 'gcc-devel', 'gcc-doc', 'gcc-runtime']}
    def configure_command (self):
        return (misc.join_lines (Gcc.configure_command (self) + '''
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
        return (Gcc.install_command (self)
                .replace (' install', ' install-gcc')
                #+ ' prefix=/usr/cross/core'
                )
    def install (self):
        # cross.Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
        cross.CrossToolSpec.install (self)
    def languages (self):
        return  ['c']

