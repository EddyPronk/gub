from gub import target
from gub.specs import freetype

class XFreetype (freetype.Freetype):
    source = 'http://download.savannah.nongnu.org/releases/freetype/freetype-2.1.10.tar.gz&name=freetype'
    patches = ['freetype-libtool-no-version.patch']
    configure_flags = (freetype.Freetype.configure_flags
                + ' --sysconfdir=/etc --localstatedir=/var')
    subpackage_names = ['devel', 'runtime', '']
    def __init__ (self, settings, source):
        freetype.Freetype.__init__ (self, settings, source)
        self.so_version = '6'
    def get_subpackage_definitions (self):
        d = dict (freetype.Freetype.get_subpackage_definitions (self))
        # urg, must remove usr/share. Because there is no doc package,
        # runtime iso '' otherwise gets all docs.
        d['runtime'] = [self.settings.prefix_dir + '/bin/*dll',
                        self.settings.prefix_dir + '/lib/*.la']
        return d
        #return ['devel', 'doc', '']
    def get_build_dependencies (self): #cygwin
        return ['libtool']
    def get_dependency_dict (self): #cygwin
        return {
            '': ['libfreetype26'],
            'devel': ['libfreetype26'],
            'runtime': ['zlib'],
            }
    def category_dict (self):
        return {'': 'Libs'}
    def install (self):
        target.AutoBuild.install (self)
        self.pre_install_smurf_exe ()
