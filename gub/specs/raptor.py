from gub import commands
from gub import targetbuild

class Raptor (targetbuild.TargetBuild):
    source = 'http://download.librdf.org/source/raptor-1.4.18.tar.gz'
    patches = ['raptor-1.4.18-cross.patch']
    def get_build_dependencies (self):
        return ['expat-devel', 'libxml2-devel']
    def autoupdate (self):
        self.runner._execute (commands.ForcedAutogenMagic (self))
        return
#        self.system ('cd %(srcdir)s && bash ./autogen.sh --help')
        self.system ('''
#cd %(srcdir)s && libtoolize
#cd %(srcdir)s && gtkdocize
cd %(srcdir)s && aclocal
cd %(srcdir)s && autoheader
cd %(srcdir)s && autoconf
cd %(srcdir)s && automake --force --foreign --copy --add-missing
''')
        
    def config_cache_overrides (self, str):
        return str + '''
ac_cv_vsnprint_result_c99=1
ac_cv_libxmlparse_xml_parsercreate=no
ac_cv_expat_xml_parsercreate=yes
ac_cv_expat_initial_utf8_bom=yes
'''
