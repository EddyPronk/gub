from gub import misc
from gub import toolsbuild

class Icoutils__tools (toolsbuild.AutoBuild):
    def get_build_dependencies (self):
        return ['libpng-devel']
    def get_dependency_dict (self):
        return {'': ['libpng']}
    def configure_command (self):
        return (toolsbuild.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--with-libintl-prefix=%(system_prefix)s
--disable-nls
'''))

class Icoutils__darwin (toolsbuild.AutoBuild):
    def patch (self):
        for f in 'wrestool', 'icotool':
            self.file_sub ([(r'\$\(LIBS\)', '$(INTLLIBS) $(LIBS)')],
                           '%(srcdir)s/' + f + "/Makefile.in")

Icoutils__darwin__x86 = Icoutils__darwin
