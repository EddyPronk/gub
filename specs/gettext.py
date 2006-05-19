import download
import targetpackage
import toolpackage

class Gettext (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='0.14.1', mirror=download.gnu, format='gz',
                   depends=['libtool'])

    def configure_command (self):
        return (targetpackage.Target_package.configure_command (self)
                + ' --disable-csharp')

    def configure (self):
        targetpackage.Target_package.configure (self)
        
        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        

class Gettext__freebsd (Gettext):
    def __init__ (self, settings):
        Gettext.__init__ (self, settings)
        self.with (version='0.14.1', mirror=download.gnu, format='gz',
                   depends=['libtool', 'libgnugetopt'])

    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/gettext-0.14.1-getopt.patch
''')

class Gettext__mingw (Gettext):
    def __init__ (self, settings):
        Gettext.__init__ (self, settings)
        self.with (version='0.14.5', mirror=download.gnu, format='gz',
                   depends=['libtool'])

    def config_cache_overrides (self, str):
        return (re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
               str)
            + '''
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
''')
    def patch (self):
        targetpackage.Target_package.patch (self)
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


class Gettext__local (toolpackage.Tool_package):
    def __init__ (self, settings):
        toolpackage.Tool_package.__init__(self,settings)
        self.with (version='0.14.1', mirror=download.gnu, format='gz',
                   depends=['libtool'])
