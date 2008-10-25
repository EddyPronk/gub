from gub import commands
from gub import context
from gub import misc
from gub import targetbuild

class Raptor (targetbuild.TargetBuild):
    source = 'http://download.librdf.org/source/raptor-1.4.18.tar.gz'
    patches = ['raptor-1.4.18-cross.patch']
    def get_build_dependencies (self):
        return ['curl-devel', 'expat-devel', 'libxml2-devel', 'libxslt-devel', 'tools::flex', 'tools::autoconf', 'tools::automake', 'tools::libtool', 'tools::gtk_doc']
    def autoupdate (self):
        self.file_sub ([('( |-I|-L)/usr', r'\1%(system_prefix)s')]
                       , '%(srcdir)s/configure.ac')
        self.runner._execute (commands.ForcedAutogenMagic (self))
    def config_cache_overrides (self, str):
        return str + '''
ac_cv_vsnprint_result_c99=1
ac_cv_libxmlparse_xml_parsercreate=no
ac_cv_expat_xml_parsercreate=yes
ac_cv_expat_initial_utf8_bom=yes
'''
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + misc.join_lines ('''
--enable-maintainer-mode
'''))
    @context.subst_method
    def config_script (self):
        return 'raptor-config'

class Raptor__mingw (Raptor):
    patches = Raptor.patches
    def makeflags (self):
#        return '''CFLAGS='-Dstrtok_r\(s,d,p\)=strtok\(s,d\)' '''
        return '''CFLAGS="-D'strtok_r(s,d,p)=strtok(s,d)'" '''
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + misc.join_lines ('''
--enable-maintainer-mode
--enable-parsers="grddl rdfxml ntriples turtle trig guess rss-tag-soup rdfa n3"
'''))
#--enable-parsers="grddl rdfxml ntriples turtle trig guess rss-tag-soup rdfa n3"
