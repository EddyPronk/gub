from gub import toolpackage
from gub import targetpackage
from gub import repository

class Git__local (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (mirror='http://kernel.org/pub/software/scm/git/git-%(version)s.tar.bz2',
                   version='1.5.1.4')
    def patch (self):
        self.system('cd %(srcdir)s && git reset --hard HEAD')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        self.file_sub ([('git describe','true')],
                       '%(srcdir)s/GIT-VERSION-GEN')

    def configure (self):
        self.dump ('prefix=%(system_root)s/usr', '%(builddir)s/config.mak')

    def wrap_executables (self):
        # GIT executables use ancient unix style smart name-based
        # functionality switching.  Did Linus not read or understand
        # Standards.texi?
        pass

class Git (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        source = 'git://repo.or.cz/git/mingw.git'
        repo = repository.Git (self.get_repodir (),
                               branch=settings.git_branch,
                               source=source)
        self.with_vc (repo)

        ## strip -mwindows.
        self.target_gcc_flags = ' -mms-bitfields '

    def version (self):
        return '1.5.2'

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
        self.system('cd %(srcdir)s && git reset --hard HEAD')
        self.system('cd %(srcdir)s && patch -p1 < %(patchdir)s/git-1.5.2-templatedir.patch')
        targetpackage.TargetBuildSpec.patch (self)
        self.system ('rm -rf %(builddir)s')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        self.file_sub ([('git describe','true')],
                        '%(srcdir)s/GIT-VERSION-GEN')
        self.system('cd %(srcdir)s && patch -p1 < %(patchdir)s/git-1.5-shell-anality.patch')
        
class Git__mingw (Git):
    def __init__ (self, settings):
        Git.__init__ (self, settings)
        self.target_gcc_flags = ' -mms-bitfields '

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
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

                ## we'll consider it if they 
                + ' SCRIPT_PERL= '
                + ' instdir_SQ=%(install_root)s/usr/lib/ '
                + ' SHELL_PATH=/bin/sh'
                + ' PERL_PATH=/bin/perl')

    def get_dependency_dict (self):
        d = Git.get_dependency_dict (self)
        d[''].append ('tcltk')
        return d
