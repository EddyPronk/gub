from gub import misc
from gub import tools

class Icoutils__tools (tools.AutoBuild):
    def _get_build_dependencies (self):
        return ['libpng-devel']
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--with-libintl-prefix=%(system_prefix)s
--disable-nls
'''))

class Icoutils__darwin (tools.AutoBuild):
    def patch (self):
        for f in 'wrestool', 'icotool':
            self.file_sub ([(r'\$\(LIBS\)', '$(INTLLIBS) $(LIBS)')],
                           '%(srcdir)s/' + f + "/Makefile.in")

Icoutils__darwin__x86 = Icoutils__darwin
