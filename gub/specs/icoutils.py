from gub import toolsbuild

class Icoutils (toolsbuild.AutoBuild):
    def get_build_dependencies (self):
        return ['libpng-devel']
    def get_dependency_dict (self):
        return {'': ['libpng']}
    def configure_command (self):
        return (toolsbuild.AutoBuild.configure_command (self)
                + ' --with-libintl-prefix=%(system_prefix)s/ ')

class Icoutils__darwin (Icoutils):
    def patch (self):
        for f in 'wrestool', 'icotool':
            self.file_sub ([(r'\$\(LIBS\)', '$(INTLLIBS) $(LIBS)')],
                           '%(srcdir)s/' + f + "/Makefile.in")

Icoutils__darwin__x86 = Icoutils__darwin
