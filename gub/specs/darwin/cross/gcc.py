import os
#
from gub.specs.cross import gcc as cross_gcc
from gub import loggedos

class Gcc__darwin (cross_gcc.Gcc):
    source = 'ftp://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-4.1.1/gcc-4.1.1.tar.bz2'
    def _get_build_dependencies (self):
        return ([x for x in cross_gcc.Gcc._get_build_dependencies (self)
                 if 'cross/binutils' not in x]
                + ['odcctools'])
    def patch (self):
        self.file_sub ([('/usr/bin/libtool', '%(cross_prefix)s/bin/%(target_architecture)s-libtool')],
                       '%(srcdir)s/gcc/config/darwin.h')

        self.file_sub ([('--strip-underscores', '--strip-underscore')],
                       '%(srcdir)s/libstdc++-v3/scripts/make_exports.pl')
    def languages (self):
        # objective-c is used for quartz's Carbon/Carbon.h in pango, gtk+
        return cross_gcc.Gcc.languages (self) + ['objc', 'obj-c++']
    def rewire_gcc_libs (self):
        # FIXME: why do we skip, please document?
        # I get
        '''
/home/janneke/vc/gub/target/darwin-x86/root/usr/cross/bin/i686-apple-darwin8-ld: warning can't open dynamic library: /home/janneke/vc/gub/target/darwin-x86/root/home/janneke/vc/gub/target/darwin-x86/root/usr/cross/i686-apple-darwin8/lib/libgcc_s.1.dylib referenced from: /home/janneke/vc/gub/target/darwin-x86/root/usr/lib/libstdc++.dylib (checking for undefined symbols may be affected) (No such file or directory, errno = 2)
'''
        # let's try adding libstdc++.dylib?, nah, let's not
        skip_libs = ['libgcc_s'] #, 'libstdc++']

        def rewire_one (logger, file):
            found_skips = [s for s in skip_libs if file.find (s) >= 0]
            if found_skips:
                return
            id = loggedos.read_pipe (logger,
                                     self.expand ('%(toolchain_prefix)sotool -L %(file)s', 
                                                 locals ()),
                                     env=self.get_substitution_dict ()).split ()[1]
            id = os.path.split (id)[1]
            loggedos.system (logger, 
                             self.expand ('%(toolchain_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(file)s',
                                          locals ()),
                             env=self.get_substitution_dict ())
        self.map_locate (rewire_one,
                         self.expand ('%(install_prefix)s/lib/'),
                         '*.dylib')
    def install (self):
        cross_gcc.Gcc.install (self)
        # conflicts with darwin-SDK
        self.system ('mv %(install_prefix)s/lib/libsupc++.a %(install_prefix)s/lib/libsupc++.a-')
        self.rewire_gcc_libs ()
    
class Gcc__darwin__x86 (Gcc__darwin):
    source = 'ftp://ftp.fu-berlin.de/unix/languages/gcc/releases/gcc-4.3.2/gcc-4.3.2.tar.bz2'
    def _get_build_dependencies (self):
        return Gcc__darwin._get_build_dependencies (self) + ['tools::mpfr']

class Not_used__Gcc__darwin (Gcc__darwin):
    def configure (self):
        cross_gcc.Gcc.configure (self)
    def install (self):
        cross_gcc.Gcc.install (self)
        self.rewire_gcc_libs ()
