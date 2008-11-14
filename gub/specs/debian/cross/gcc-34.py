from gub.specs.cross import gcc

class Gcc_34__debian__mipsel (gcc.Gcc):
    def languages (self):
        return  ['c']
        
    def configure_command (self):
        return misc.join_lines (gcc.Gcc.configure_command (self)
                               + '''
--program-suffix=-3.4
--with-ar=%(cross_prefix)s/bin/%(target_architecture)s-ar
--with-nm=%(cross_prefix)s/bin/%(target_architecture)s-nm
''')

    def configure (self):
        gcc.Gcc.configure (self)
        #FIXME: --with-ar, --with-nm does not work?
        for i in ('ar', 'nm', 'ranlib'):
            self.system ('cd %(cross_prefix)s/bin && ln -sf %(target_architecture)s-%(i)s %(target_architecture)s-%(i)s-3.4', env=locals ())
                
    def install (self):
        gcc.Gcc.install (self)
        # get rid of duplicates
        self.system ('''
rm -f %(install_prefix)s/lib/libgcc_s.so
rm -f %(install_prefix)s/lib/libgcc_s.so.1
rm -f %(install_prefix)s%(cross_dir)s/lib/libiberty.a
rm -rf %(install_prefix)s%(cross_dir)s/mipsel-linux/lib/libiberty.a
rm -rf %(install_prefix)s%(cross_dir)s/info
rm -rf %(install_prefix)s%(cross_dir)s/man
rm -rf %(install_prefix)s%(cross_dir)s/share/locale
''')
        if 'c++' in self.languages ():
            self.system ('''
rm -rf %(install_prefix)s/lib/libsupc++.la
rm -rf %(install_prefix)s/lib/libstdc++.la
rm -rf %(install_prefix)s/lib/libstdc++.so.6
rm -rf %(install_prefix)s/lib/libstdc++.so
rm -rf %(install_prefix)s%(cross_dir)s/mipsel-linux/lib/libsupc++.a
rm -rf %(install_prefix)s%(cross_dir)s/mipsel-linux/lib/libstdc++.a
rm -rf %(install_prefix)s%(cross_dir)s/mipsel-linux/lib/debug/libstdc++.a
''')

