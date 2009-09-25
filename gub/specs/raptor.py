from gub import commands
from gub import misc
from gub import target

class Raptor (target.AutoBuild):
    source = 'http://download.librdf.org/source/raptor-1.4.18.tar.gz'
    patches = ['raptor-1.4.18-cross.patch']
    dependencies = ['curl-devel', 'expat-devel', 'libxml2-devel', 'libxslt-devel', 'tools::flex', 'tools::autoconf', 'tools::automake', 'tools::libtool', 'tools::gtk_doc']
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
    configure_flags = (target.AutoBuild.configure_flags
                + misc.join_lines ('''
--enable-maintainer-mode
'''))
    def config_script (self):
        return 'raptor-config'

class Raptor__mingw (Raptor):
#        return '''CFLAGS='-Dstrtok_r\(s,d,p\)=strtok\(s,d\)' '''
    makeflags = '''CFLAGS="-D'strtok_r(s,d,p)=strtok(s,d)'" '''
    configure_flags = (target.AutoBuild.configure_flags
                + misc.join_lines ('''
--enable-maintainer-mode
--enable-parsers="grddl rdfxml ntriples turtle trig guess rss-tag-soup rdfa n3"
'''))
#--enable-parsers="grddl rdfxml ntriples turtle trig guess rss-tag-soup rdfa n3"

class Raptor__darwin (Raptor):
    dependencies = [x for x in Raptor.dependencies
                if x.replace ('-devel', '') not in [
                'libxml2', # Included in darwin-sdk, hmm?
                ]]
