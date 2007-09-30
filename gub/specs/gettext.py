from gub import mirrors
from gub import targetbuild
from gub import toolsbuild

class Gettext (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_template (version='0.15', mirror=mirrors.gnu, format='gz')

    def get_build_dependencies (self):
        return ['libtool']

    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + ' --disable-threads --disable-csharp --disable-java ')

    def configure (self):
        targetbuild.TargetBuild.configure (self)

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        self.file_sub ([
                ('(SUBDIRS *=.*)examples', r'\1 '),
                ],
                       '%(builddir)s/gettext-tools/Makefile')

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
        self.with_template (version='0.15', mirror=mirrors.gnu, format='gz')

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
        self.update_libtool ()
        Gettext.install (self)

class Gettext__tools (toolsbuild.ToolsBuild):
    def get_build_dependencies (self):
        return ['libtool']
    def configure (self):
        toolsbuild.ToolsBuild.configure (self)
        self.file_sub ([
                ('(SUBDIRS *=.*)examples', r'\1 '),
                ],
                       '%(builddir)s/gettext-tools/Makefile')
