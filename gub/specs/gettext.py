#
from gub import loggedos
from gub import misc
from gub import target
from gub import tools

class Gettext (target.AutoBuild):
    # 0.16.1 makes gcc barf on ICE.
    source = 'http://ftp.gnu.org/pub/gnu/gettext/gettext-0.15.tar.gz'
    dependencies = ['libtool']
    config_cache_overrides = (target.AutoBuild.config_cache_overrides + '''
ac_cv_prog_YACC=${ac_cv_prog_YACC=no}
ac_cv_prog_INTLBISON=${ac_cv_prog_INTLBISON=no}
ac_cv_prog_F77=${ac_cv_prog_F77=no}
ac_cv_prog_FC=${ac_cv_prog_FC=no}
ac_cv_prog_GCJ=${ac_cv_prog_GCJ=no}
ac_cv_prog_GC=${ac_cv_prog_GC=no}
ac_cv_prog_HAVE_GCJ_IN_PATH=${ac_cv_prog_HAVE_GCJ_IN_PATH=no}
ac_cv_prog_HAVE_JAVAC_IN_PATH=${ac_cv_prog_HAVE_JAVAC_IN_PATH=no}
ac_cv_prog_HAVE_JIKES_IN_PATH=${ac_cv_prog_HAVE_JIKES_IN_PATH=no}
''')
    configure_flags = (target.AutoBuild.configure_flags
                + ' --disable-threads'
                + ' --disable-csharp'
                + ' --disable-java'
                )
#    if 'stat' in misc.librestrict (): # too broken to fix
#        def LD_PRELOAD (self):
#            return '%(tools_prefix)s/lib/librestrict-open.so'
    if 'stat' in misc.librestrict (): # OPENs /USR/include/libexpat.la
        def LD_PRELOAD (self):
            return ''
#
#    if 'stat' in misc.librestrict (): # too broken to fix
#        # configure [gettext, flex] blindly look for /USR/include/libi*
#        configure_variables = (target.configure_variables
#                               + ' --without-libiconv-prefix'
#                               + ' --without-libintl-prefix')
#    def autoupdate (self):
#        target.AutoBuild.autoupdate (self)
#        if 'stat' in misc.librestrict ():
#            def defer (logger, file):
#                loggedos.file_sub (logger, [
#                        # blindly stats /USR/share/locale/fr*
#                        # /USR/lib/jdk -- never mind --disable-java
#                        (' /usr(/share/locale|/lib/jdk)',
#                         self.expand (r'%(system_prefix)s/\1'))], file)
#            self.map_find_files (defer, '%(srcdir)s', '^configure$')
    def configure (self):
        target.AutoBuild.configure (self)
        self.file_sub ([
                ('(SUBDIRS *=.*)examples', r'\1 '),
                ],
                       '%(builddir)s/gettext-tools/Makefile')

class Gettext__freebsd__x86 (Gettext):
    dependencies = (Gettext.dependencies + ['libgnugetopt'])

class Gettext__mingw (Gettext):
    patches = ['gettext-0.15-mingw.patch']
    config_cache_overrides = (Gettext.config_cache_overrides
                              #FIXME: promoteme? see Gettext/Python
                              .replace ('ac_cv_func_select=yes',
                                        'ac_cv_func_select=no')
                              + '''
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
''')
    configure_flags = Gettext.configure_flags + ' --disable-libasprintf'
    def configure (self):
        Gettext.configure (self)
        self.file_sub ( [(' gettext-tools ', ' ')],
                        '%(builddir)s/Makefile')
    def install (self):
        ## compile of gettext triggers configure in between.  (hgwurgh.)
        self.update_libtool ()
        Gettext.install (self)

class Gettext__tools (tools.AutoBuild):
    dependencies = [
#            'system::g++',
            'libtool',
            ]
    configure_flags = (tools.AutoBuild.configure_flags
                + ' --disable-libasprintf')
    def configure (self):
        tools.AutoBuild.configure (self)
        self.file_sub ([
                ('(SUBDIRS *=.*)examples', r'\1 '),
                ],
                       '%(builddir)s/gettext-tools/Makefile')
