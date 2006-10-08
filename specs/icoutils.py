from toolpackage import ToolBuildSpec

class Icoutils (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
	import download
        self.with (version='0.26.0', mirror=download.nongnu_savannah)
    def get_build_dependencies (self):
        return ['libpng-devel']
    def get_dependency_dict (self):
        return {'': ['libpng']}
    def configure_command (self):
        return ToolBuildSpec.configure_command (self) + ' --with-libintl-prefix=%(system_root)s/usr/ '  

    def patch (self):

        ## necessary for MacOS X.
        for f in 'wrestool', 'icotool':
            self.file_sub ([(r'\$\(LIBS\)', '$(INTLLIBS) $(LIBS)')],
                           '%(srcdir)s/' + f + "/Makefile.in")
