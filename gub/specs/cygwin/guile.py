from gub import cygwin
from gub import gup
from gub import misc
from gub.specs import guile

class Guile (guile.Guile):
    patches = guile.Guile.patches + ['guile-1.8.7-no-complex.patch']
    config_cache_overrides = guile.Guile.config_cache_overrides + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_prefix)s/lib"}
'''
    configure_variables = (guile.Guile.configure_variables
                + misc.join_lines ('''
CFLAGS='-DHAVE_CONFIG_H=1 -I%(builddir)s'
'''))
    dependencies = gup.gub_to_distro_deps (lilypond.LilyPond.dependencies,
                                           cygwin.gub_to_distro_dict)
    EXE = '.exe'
    def category_dict (self):
        return {'': 'Interpreters'}
    def XXXconfigure (self):
        self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''', r'\1')],
                       '%(srcdir)s/configure')
        guile.Guile.configure (self)
    # C&P from guile.Guile__mingw
    def compile (self):
        ## Why the !?#@$ is .EXE only for guile_filter_doc_snarfage?
        self.system ('''cd %(builddir)s/libguile &&make %(compile_flags_native)sgen-scmconfig guile_filter_doc_snarfage.exe''')
        self.system ('cd %(builddir)s/libguile && cp guile_filter_doc_snarfage.exe guile_filter_doc_snarfage')
        guile.Guile.compile (self)
    def description_dict (self):
        return {
            '': """The GNU extension language and Scheme interpreter - executables
Guile, the GNU Ubiquitous Intelligent Language for Extension, is a scheme
implementation designed for real world programming, supporting a
rich Unix interface, a module system, and undergoing rapid development.

`guile' is a scheme interpreter that can execute scheme scripts (with a
#! line at the top of the file), or run as an inferior scheme
process inside Emacs.
""",
            'runtime': '''The GNU extension language and Scheme interpreter - runtime
Guile shared object libraries and the ice-9 scheme module.  Guile is
the GNU Ubiquitous Intelligent Language for Extension.
''',
            'devel': """The GNU extension language and Scheme interpreter - development
`libguile.h' etc. C headers, aclocal macros, the `guile-snarf' and
`guile-config' utilities, and static `libguile.a' libraries for Guile,
the GNU Ubiquitous Intelligent Language for Extension.
""",
            'doc': """The GNU extension language and Scheme interpreter - documentation
This package contains the documentation for guile, including both
a reference manual (via `info guile'), and a tutorial (via `info
guile-tut').
""",
    }
