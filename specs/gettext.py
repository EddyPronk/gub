import download
import targetpackage
import toolpackage

class Gettext (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='0.15', mirror=download.gnu, format='gz')

    def get_build_dependencies (self):
        return ['libtool']

    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + ' --disable-threads --disable-csharp --disable-java ')

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        
        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        

class Gettext__freebsd (Gettext):
    def get_dependency_dict (self):
        d = Gettext.get_dependency_dict (self)
        if self.settings.target_architecture == 'i686-freebsd4':
            d[''].append ('libgnugetopt')
        return d

    def get_build_dependencies (self):
        if self.settings.target_architecture == 'i686-freebsd4':
            return ['libgnugetopt'] + Gettext.get_build_dependencies (self)
        return Gettext.get_build_dependencies (self)

class Gettext__mingw (Gettext):
    def __init__ (self, settings):
        Gettext.__init__ (self, settings)
        self.with (version='0.15', mirror=download.gnu, format='gz')

    def config_cache_overrides (self, str):
        return (re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
               str)
            + '''
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
''')

    def configure_command (self):
        return Gettext.configure_command (self) + ' --disable-libasprintf' 

    def configure (self):
        Gettext.configure (self)
        self.file_sub ( [(' gettext-tools ', ' ')],
                        '%(builddir)s/Makefile')
                       

    def install (self):

        ## compile of gettext triggers configure in between.  (hgwurgh.)
        self.update_libtool()
        Gettext.install (self)

class Gettext__local (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__(self,settings)
        self.with (version='0.15', mirror=download.gnu, format='gz')

    def get_build_dependencies (self):
        return ['libtool']            

    def configure (self):
        toolpackage.ToolBuildSpec.configure (self)
        self.file_sub ( [
                         ('(SUBDIRS *=.*)examples', r'\1 '),
                         ],
                        '%(builddir)s/gettext-tools/Makefile')
