import download
import targetpackage
import toolpackage

class Gettext (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='0.14.1', mirror=download.gnu, format='gz')

    def get_build_dependencies (self):
        return ['libtool']

    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + ' --disable-csharp')

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        
        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        

class Gettext__freebsd (Gettext):
    def __init__ (self, settings):
        Gettext.__init__ (self, settings)
        self.with (version='0.14.1', mirror=download.gnu, format='gz')

    def get_dependency_dict (self):
        d = Gettext.get_dependency_dict (self)
        d[''].append ('libgnugetopt')
        return d
    
    def patch (self):
        Gettext.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gettext-0.14.1-mingw.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/gettext-0.14.1-getopt.patch
''')

class Gettext__mingw (Gettext):
    def __init__ (self, settings):
        Gettext.__init__ (self, settings)
        self.with (version='0.14.5', mirror=download.gnu, format='gz')

    def config_cache_overrides (self, str):
        return (re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
               str)
            + '''
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
''')
    def patch (self):
        targetpackage.TargetBuildSpec.patch (self)
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/gettext-0.14.5-mingw.patch")
        self.system ("cd %(srcdir)s && patch -p0 < %(patchdir)s/gettext-xgettext-dll-autoimport.patch")
        
    def install (self):

        ## compile of gettext triggers configure in between.  (hgwurgh.)
        self.update_libtool()
        Gettext.install (self)

class Gettext__darwin (Gettext):
    def xconfigure_command (self):
        ## not necessary for 0.14.1
        return re.sub (' --config-cache', '',
                       Gettext.configure_command (self))


class Gettext__local (toolpackage.ToolBuildSpecification):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpecification.__init__(self,settings)
        self.with (version='0.14.1', mirror=download.gnu, format='gz')

    def configure (self):
        toolpackage.ToolBuildSpecification.configure (self)
        self.update_libtool ()
