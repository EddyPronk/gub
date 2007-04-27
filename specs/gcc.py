import cross
import misc

class Gcc (cross.Gcc):
    def __init__ (self, settings):
        cross.Gcc.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version='4.1.1', format='bz2')
            
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
