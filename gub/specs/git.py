from gub import target
from gub import tools

class Git (target.AutoBuild):
    source = 'http://kernel.org/pub/software/scm/git/git-1.6.4.4.tar.gz'
    srcdir_build_broken = True
    def get_subpackage_names (self):
        return ['']
    dependencies = ['zlib-devel']
    def config_cache_overrides (self, string):
        # PROMOTEME: at least defines
        return string + '''\n
ac_cv_c_c99_format=no
ac_cv_fread_reads_directories=no
ac_cv_snprintf_returns_bongus=yes
'''
    configure_flags = (tools.AutoBuild.configure_flags
                + ' --without-openssl')
    make_flags = '''V=1 NO_PERL=NoThanks'''

class Git__freebsd (Git):
    dependencies = Git.dependencies + ['libiconv-devel', 'regex-devel']
    make_flags = (Git.make_flags
                  + ' CFLAGS="-O2 -Duintmax_t=unsigned -Dstrtoumax=strtoul"')

class Git__mingw (Git):
    def __init__ (self, settings, source):
        Git.__init__ (self, settings, source)
        self.target_gcc_flags = ' -mms-bitfields '
    dependencies = Git.dependencies + ['libiconv-devel', 'regex-devel', 'tcltk']
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
    make_flags = (' uname_S=MINGW'
                + ' V=1 '
                ## we'll consider it if they clean up their act
                + ' SCRIPT_PERL= '
                + ' instdir_SQ=%(install_prefix)s/lib/ '
                + ' SHELL_PATH=/bin/sh'
                + ' PERL_PATH=/bin/perl')
    compile_flags = ' template_dir=../share/git-core/templates/'
    def install (self):
        Git.install (self)
        bat = r'''@echo off
"@INSTDIR@\usr\bin\wish84.exe" "@INSTDIR@\usr\bin\gitk" %1 %2 %3 %4 %5 %6 %7 %8 %9
'''.replace ('%','%%').replace ('\n','\r\n')
        self.dump (bat, '%(install_prefix)s/bin/gitk.bat.in')

class Git__tools (tools.AutoBuild, Git):
    dependencies = ['curl', 'expat', 'zlib']
    configure_flags = (tools.AutoBuild.configure_flags
                       + ' --without-openssl')
    make_flags = Git.make_flags
