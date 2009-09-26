from gub.specs import fontconfig

class Fontconfig (fontconfig.Fontconfig):
    source = 'http://www.fontconfig.org/release/fontconfig-2.4.1.tar.gz'
    configure_flags = (fontconfig.Fontconfig.configure_flags
                + ' --sysconfdir=/etc --localstatedir=/var')
    subpackage_names = ['devel', 'runtime', '']
    def __init__ (self, settings, source):
        fontconfig.Fontconfig.__init__ (self, settings, source)
        self.so_version = '1'
    def get_subpackage_definitions (self):
        d = dict (fontconfig.Fontconfig.get_subpackage_definitions (self))
        # urg, must remove usr/share. Because there is no doc package,
        # runtime iso '' otherwise gets all docs.
        d['runtime'] = [self.settings.prefix_dir + '/lib']
        return d
        #return ['devel', 'doc', '']
    def get_build_dependencies (self): #cygwin
        return ['libtool', 'libfreetype2-devel', 'expat']
    def get_dependency_dict (self): #cygwin
        return {
            '': ['libfontconfig1'],
            'devel': ['libfontconfig1', 'libfreetype2-devel'],
            'runtime': ['expat', 'libfreetype26', 'zlib'],
            }
    def category_dict (self):
        return {'': 'Libs'}
    def install (self):
        self.pre_install_smurf_exe ()
        fontconfig.Fontconfig.install (self)
        name = 'fontconfig-postinstall.sh'
        postinstall = '''#! /bin/sh
# cleanup silly symlink of previous packages
rm -f /usr/X11R6/bin/fontconfig-config
'''
        self.dump (postinstall,
                   '%(install_root)s/etc/postinstall/%(name)s',
                   env=locals ())
