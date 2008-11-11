from gub import tools
from gub import target

class Git__tools (tools.AutoBuild):
    source = 'http://kernel.org/pub/software/scm/git/git-1.5.3.6.tar.bz2'
    def get_build_dependencies (self):
        return ['curl', 'expat', 'zlib']
    def get_dependency_dict (self):
        return {'': [
            'curl',
            'expat',
            'zlib',
            ]}
    def configure (self):
        self.shadow ()
        self.dump ('prefix=%(system_prefix)s', '%(builddir)s/config.mak')
    def patch (self):
        tools.AutoBuild.patch (self)
        self.file_sub ([('git describe','true')],
                       '%(srcdir)s/GIT-VERSION-GEN')
        # kill perl.
        self.dump ('''
install:
\ttrue
''', '%(srcdir)s/perl/Makefile')

        self.file_sub ([('\t\\$\\(QUIET_SUBDIR0\\)perl[^\n]+\n', ''),
                        ('SCRIPT_PERL = ', 'SCRIPT_PERL_X = ')],
                       '%(srcdir)s/Makefile')
    def makeflags (self):
        flags = '''V=1 SCRIPT_PERL= LDFLAGS='%(rpath)s' '''
        if 'freebsd' in self.settings.build_architecture:
            flags += ' CFLAGS="-O2 -Duintmax_t=unsigned -Dstrtoumax=strtoul"'
        return flags
    def wrap_executables (self):
        # using rpath
        # Besides: GIT executables use ancient unix style smart
        # name-based functionality switching.
        pass

class Git (target.AutoBuild):
    patches = ['git-1.5.2-templatedir.patch',
               'git-1.5-shell-anality.patch']

    def version (self):
        return '1.5.3.rc2'

    def configure (self):
        self.shadow ()
        target.AutoBuild.configure (self)

    def get_dependency_dict (self):
        return {'': [
            'zlib',
            'regex',
            'libiconv'
            ]}

    def get_subpackage_names (self):
        return ['']

    def get_build_dependencies (self):
        return ['zlib-devel',
                'regex-devel',
                'libiconv-devel',
                'tools::autoconf',
                ]

    def patch (self):
        target.AutoBuild (patch)
        self.file_sub ([('GIT-CFLAGS','$(GIT_CFLAGS_FILE)'),
                        ('\t\\$\\(MAKE\\) -C perl[^\n]\n', '')
                        ],
                        '%(srcdir)s/Makefile')
        self.file_sub ([('\.\./GIT-CFLAGS Makefile', 'Makefile')],
                        '%(srcdir)s/perl/Makefile')
        target.AutoBuild.patch (self)
        self.system ('rm -rf %(builddir)s')
        self.file_sub ([('git describe','true')],
                        '%(srcdir)s/GIT-VERSION-GEN')
        
class Git__mingw (Git):
    def __init__ (self, settings, source):
        Git.__init__ (self, settings, source)
        self.target_gcc_flags = ' -mms-bitfields '

    def configure (self):
        target.AutoBuild.configure (self)
        self.file_sub ([('CFLAGS = -g',
                         'CFLAGS = -I compat/ -g')],
                       '%(builddir)s/config.mak.autogen')
        self.file_sub ([('-lsocket',
                         '-lwsock32'),
                        ],
                       '%(builddir)s/Makefile')
        self.dump ('%(version)s-GUB', '%(builddir)s/version')

    def makeflags (self):
        return (' uname_S=MINGW'
                + ' V=1 '

                ## we'll consider it if they clean up their act
                + ' SCRIPT_PERL= '
                + ' instdir_SQ=%(install_prefix)s/lib/ '
                + ' SHELL_PATH=/bin/sh'
                + ' PERL_PATH=/bin/perl')

    def compile_command (self):

        ## want this setting to reach compile, but not install
        return Git.compile_command (self) + ' template_dir=../share/git-core/templates/ '

    def get_dependency_dict (self):
        d = Git.get_dependency_dict (self)
        d[''].append ('tcltk')
        return d

    def get_build_dependencies (self):
        d =  Git.get_build_dependencies (self)
        d.append ('tcltk')
        return d
    
    def install (self):
        Git.install (self)
        bat = r'''@echo off
"@INSTDIR@\usr\bin\wish84.exe" "@INSTDIR@\usr\bin\gitk" %1 %2 %3 %4 %5 %6 %7 %8 %9
'''.replace ('%','%%').replace ('\n','\r\n')
        self.dump (bat, '%(install_prefix)s/bin/gitk.bat.in')
