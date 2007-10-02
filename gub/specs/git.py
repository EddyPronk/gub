from gub import toolsbuild
from gub import targetbuild
from gub import repository

class Git__tools (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='git', mirror='http://kernel.org/pub/software/scm/git/git-%(version)s.tar.bz2',
                   version='1.5.1.4')
    def configure (self):
        self.dump ('prefix=%(system_prefix)s', '%(builddir)s/config.mak')

    def patch (self):
        toolsbuild.ToolsBuild.patch (self)
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
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
  
    def wrap_executables (self):
        # GIT executables use ancient unix style smart name-based
        # functionality switching.  
        pass

    def makeflags (self):
        return ' SCRIPT_PERL= '
                
class Git (targetbuild.TargetBuild):

    # TODO: where should this go?
    ## strip -mwindows.
    #self.target_gcc_flags = ' -mms-bitfields '

    def version (self):
        return '1.5.3.rc2'

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
                'libiconv-devel'
                ]

    def patch (self):
        self.file_sub ([('GIT-CFLAGS','$(GIT_CFLAGS_FILE)'),
                        ('\t\\$\\(MAKE\\) -C perl[^\n]\n', '')
                        ],
                        '%(srcdir)s/Makefile')
        self.file_sub ([('\.\./GIT-CFLAGS Makefile', 'Makefile')],
                        '%(srcdir)s/perl/Makefile')

        self.system('cd %(srcdir)s && patch -p1 < %(patchdir)s/git-1.5.2-templatedir.patch')
        targetbuild.TargetBuild.patch (self)
        self.system ('rm -rf %(builddir)s')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        self.file_sub ([('git describe','true')],
                        '%(srcdir)s/GIT-VERSION-GEN')
        self.system('cd %(srcdir)s && patch -p1 < %(patchdir)s/git-1.5-shell-anality.patch')
        self.autoupdate()
        
class Git__mingw (Git):
    def __init__ (self, settings, source):
        Git.__init__ (self, settings, source)
        self.target_gcc_flags = ' -mms-bitfields '

    def configure (self):
        targetbuild.TargetBuild.configure (self)
        self.file_sub ([('CFLAGS = -g',
                         'CFLAGS = -I compat/ -g')],
                       '%(builddir)s/config.mak.autogen')
        self.file_sub ([('-lsocket',
                         '-lwsock32'),
                        ],
                       '%(builddir)s/Makefile')
        self.dump('%(version)s-GUB', '%(builddir)s/version')

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
        Git.install(self)
        bat = r'''@echo off
"@INSTDIR@\usr\bin\wish84.exe" "@INSTDIR@\usr\bin\gitk" %1 %2 %3 %4 %5 %6 %7 %8 %9
'''.replace ('%','%%').replace ('\n','\r\n')
        self.dump (bat, '%(install_prefix)s/bin/gitk.bat.in')
