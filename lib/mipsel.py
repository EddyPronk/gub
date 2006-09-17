
#
import cross
import download
import gub
import linux
import misc
import targetpackage

class Mipsel_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    pass

class Gcc_34 (cross.Gcc):
    def languages (self):
        return  ['c']
        
    def configure_command (self):
        return misc.join_lines (cross.Gcc.configure_command (self)
                               + '''
--program-suffix=-3.4
--with-ar=%(cross_prefix)s/bin/%(target_architecture)s-ar
--with-nm=%(cross_prefix)s/bin/%(target_architecture)s-nm
''')

    def configure (self):
        cross.Gcc.configure (self)
        #FIXME: --with-ar, --with-nm does not work?
        for i in ('ar', 'nm', 'ranlib'):
            self.system ('cd %(cross_prefix)s/bin && ln -sf %(target_architecture)s-%(i)s %(target_architecture)s-%(i)s-3.4', env=locals ())
                
    def install (self):
        cross.Gcc.install (self)
        # get rid of duplicates
        self.system ('''
rm -f %(install_root)s/usr/lib/libgcc_s.so
rm -f %(install_root)s/usr/lib/libgcc_s.so.1
rm -f %(install_root)s/usr/cross/lib/libiberty.a
rm -rf %(install_root)s/usr/cross/mipsel-linux/lib/libiberty.a
rm -rf %(install_root)s/usr/cross/info
rm -rf %(install_root)s/usr/cross/man
rm -rf %(install_root)s/usr/cross/share/locale
''')
        if 'c++' in self.languages ():
            self.system ('''
rm -rf %(install_root)s/usr/lib/libsupc++.la
rm -rf %(install_root)s/usr/lib/libstdc++.la
rm -rf %(install_root)s/usr/lib/libstdc++.so.6
rm -rf %(install_root)s/usr/lib/libstdc++.so
rm -rf %(install_root)s/usr/cross/mipsel-linux/lib/libsupc++.a
rm -rf %(install_root)s/usr/cross/mipsel-linux/lib/libstdc++.a
rm -rf %(install_root)s/usr/cross/mipsel-linux/lib/debug/libstdc++.a
''')

def get_cross_packages (settings):
    import debian
    return debian.get_cross_packages (settings) + [
        Gcc_34 (settings).with (version='3.4.6',
                             mirror=(download.gnubase
                                     + '/gcc/gcc-3.4.6/gcc-3.4.6.tar.bz2'),
                             format='bz2'),
        ]

def change_target_packages (packages):
    cross.change_target_packages (packages)
    cross.set_framework_ldpath ([p for p in packages.values ()
                                 if isinstance (p,
                                                targetpackage.TargetBuildSpec)])
    return packages
