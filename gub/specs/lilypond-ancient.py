import os
#
from gub import build
from gub import loggedos
from gub.specs import lilypond

#LilyPond = LilyPond__simple
class LilyPond (lilypond.LilyPond__simple):
    source = lilypond.url (version='v1.4')
    dependencies = [x for x in lilypond.LilyPond__simple.dependencies
                    if not x in ['system::mf', 'system::mpost']] + [
        'texlive',
        'cross/gcc-2-95',
        ]
    make_flags = (lilypond.LilyPond__simple.make_flags
                  + ' builddir=%(builddir)s'
                  + ' config=%(builddir)s/config.make'
                  )
    configure_command = ('''CPPFLAGS='-I%(system_prefix)s/include -DSCM_DEBUG_TYPING_STRICTNESS=0' '''
#                         + '''LIBS=-lstdc++-3-libc6.3-2-2.10.0 '''
#                         + '''LDFLAGS='-Wl,-L -Wl,%(system_prefix)s/%(cross_dir)s-ancient/lib -L%(system_prefix)s/lib' '''
#                         + '''LIBS=-lstdc++-3-libc6.3-2-2.10.0 '''
                         + '''LDFLAGS='-L%(system_prefix)s%(cross_dir)s-ancient/lib -L%(system_prefix)s/lib %(rpath)s' '''
                         + '''LIBS='-lstdc++ -lgcc -lkpathsea' '''
                         + lilypond.LilyPond__simple.configure_command)
    def __init__ (self, settings, source):
        lilypond.LilyPond__simple.__init__ (self, settings, source)
        build.change_dict (self, {'PATH': '%(cross_prefix)s-ancient/bin:%(tools_prefix)s/bin:%(cross_prefix)s/bin:%(tools_cross_prefix)s/bin:' + os.environ['PATH']})
    def rpath (self):
        return (r'-Wl,-rpath -Wl,\$$ORIGIN/..%(cross_dir)s/lib -Wl,-rpath -Wl,%(system_prefix)s%(cross_dir)s/lib'
                + lilypond.LilyPond__simple.rpath (self))
    def LD_PRELOAD (self):
        return ''
    def patch (self):
        lilypond.LilyPond__simple.patch (self)
        # These /are/ needed, but something breaks wrt version/name
        # getting.
        self.file_sub ([
                ('eval "REQUIRED"=', 'eval "OPTIONAL"='),
                ('(^STEPMAKE_GCC\()REQUIRED', r'\1OPTIONAL'),
                ('(^STEPMAKE_CXX\()REQUIRED', r'\1OPTIONAL'),
                ('(^STEPMAKE_GXX\()REQUIRED', r'\1OPTIONAL'),
                ('(^STEPMAKE_BISON\()REQUIRED', r'\1OPTIONAL'),
                #], '%(srcdir)s/configure.in')
                ], '%(srcdir)s/configure')
        self.file_sub ([
                ('\n\n#include "config.h"', r'''
#ifndef GUILE_MAJOR_VERSION
#ifdef SCM_MAJOR_VERSION
#define GUILE_MAJOR_VERSION SCM_MAJOR_VERSION
#define GUILE_MINOR_VERSION SCM_MINOR_VERSION
#define GUILE_PATCH_LEVEL SCM_MICRO_VERSION
#else
#include "config.h"
#endif
#endif

#ifndef gh_pair_p /* guile-1.6/1.7 backward compatibility */
inline bool ly_pair_p (SCM x) { return SCM_NFALSEP (scm_pair_p (x)); }
#define gh_pair_p ly_pair_p
inline bool ly_symbol_p (SCM x) { return SCM_SYMBOLP (x); }
#define gh_symbol_p ly_symbol_p
inline bool ly_number_p (SCM x) { return SCM_NUMBERP (x); }
#define gh_number_p ly_number_p
inline bool ly_procedure_p (SCM x) { return SCM_NFALSEP (scm_procedure_p (x)); }
#define gh_procedure_p ly_procedure_p


inline SCM ly_cdr (SCM x) { return SCM_CDR (x); }
inline SCM ly_car (SCM x) { return SCM_CAR (x); } 
inline SCM ly_caar (SCM x) { return SCM_CAAR (x); }
inline SCM ly_cdar (SCM x) { return SCM_CDAR (x); }
inline SCM ly_cadr (SCM x) { return SCM_CADR (x); }
inline SCM ly_cddr (SCM x) { return SCM_CDDR (x); }
inline SCM ly_caddr (SCM x) { return SCM_CADDR (x); }
inline SCM ly_cdadr (SCM x) { return SCM_CDADR (x); }
inline SCM ly_caadr (SCM x) { return SCM_CAADR (x); }

#define gh_car ly_car
#define gh_cdr ly_cdr
#define gh_caar ly_caar
#define gh_cadr ly_cadr
#define gh_cdar ly_cdar
#define gh_cddr ly_cddr
#define gh_caadr ly_caadr

#define scm_gc_protect_object scm_protect_object
#define scm_gc_unprotect_object scm_unprotect_object
#define scm_list_n scm_listify

#define gh_scm2bool scm_to_bool
#define gh_scm2int scm_to_int
#define gh_scm2double scm_to_double

#define gh_bool2scm scm_bool2num
#define gh_int2scm scm_int2num
#define gh_double2scm scm_double2num


#define gh_call1 scm_call_1
#define gh_call2 scm_call_2

#endif /* !gh_pair_p */

''')],
                       '%(srcdir)s/lily/include/lily-guile.hh')
        self.file_sub ([('\n\n(#ifndef YY_BUF_SIZE)',
                         r'''
/* Flex >= 2.5.29 has include stack; but we don't use that yet.  */
#if !HAVE_FLEXLEXER_YY_CURRENT_BUFFER
#define yy_current_buffer \
  (yy_buffer_stack != 0 ? yy_buffer_stack[yy_buffer_stack_top] : 0)
#endif
\1
'''),
                        ('^( *yy_current_buffer = 0;)',
                         r'''
#if HAVE_FLEXLEXER_YY_CURRENT_BUFFER
\1
#endif
''')],
                       '%(srcdir)s/lily/includable-lexer.cc')
        self.file_sub ([('''(#include <kpathsea/tex-file.h>
)[}]''',
                         r'''\1
#define kpse_find_afm(name) kpse_find_file (name, kpse_afm_format, true)
#ifndef kpse_find_tfm
#define kpse_find_tfm(name) kpse_find_file (name, kpse_tfm_format, true)
#endif
}
''')],
                       '%(srcdir)s/lily/kpath.cc')
        self.file_sub ([('''(#include "my-lily-lexer.hh")''',
                         r'''#undef yyFlexLexer
\1''')],
                       '%(srcdir)s/lily/lexer.ll')
        # FIXME: PROMOTME to texlive.
        self.file_sub ([('^(#include <kpathsea/getopt.h>)', r'//\1'),],
                       '%(system_prefix)s/include/kpathsea/kpathsea.h')
        def defer (logger):
            srcdir = self.expand ('%(srcdir)s')
            base = srcdir[:srcdir[1:].find ('/') + 1]
            loggedos.system (logger, self.expand ('cd %%(srcdir)s && ln -s %(base)s .' % locals ()))
        self.func (defer)

Lilypond_ancient = LilyPond
