from gub import build
from gub import context
from gub import misc
from gub import target

class Inkscape (target.AutoBuild):
    source = 'svn:https://inkscape.svn.sourceforge.net/svnroot/inkscape&module=inkscape&branch=trunk&revision=20605'
    branch = 'trunk'
    dependencies = [
            'tools::automake',
            'tools::gettext',
            'tools::intltool',
            'tools::pkg-config',
            'boost-devel',
            'glibmm-devel',
            'gtkmm-devel',
            'gtk+-devel',
            'gsl-devel',
            'lcms-devel',
            'poppler-devel',
            'popt-devel',
            'libgc-devel',
            'libpng-devel',
            'librsvg-devel',
            'libsig++-devel',
            'libxml2-devel',
            'libxslt-devel',
            ]
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        build.add_dict (self,
                        {'ACLOCAL_FLAGS': ' -I '.join ([''] + self.aclocal_path ()), })
        source.is_tracking = misc.bind_method (lambda x: True, source)
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('AC_PATH_PROG\(PKG_CONFIG,',
                         'AC_PATH_PROG(ARE_YOU_FREAKING_MAD__OVERRIDING_PKG_CONFIG,')],
                       '%(srcdir)s/configure.ac')
    def get_build_dependencies (self):
        return self.dependencies
    def get_dependency_dict (self):
        return {'': [x.replace ('-devel', '')
                     for x in self.dependencies
                     if 'tools::' not in x and 'cross/' not in x]
                + ['cross/gcc-c++-runtime']
                }
    configure_flags = (target.AutoBuild.configure_flags
                       + ' --enable-lcms'
                       + ' --enable-binreloc=yes'
                       )
    configure_variables = (target.AutoBuild.configure_variables
                           + ' CXXFLAGS=-fpermissive'
                           )

class Inkscape__mingw (Inkscape):
    patches = ['inkscape-mingw-DATADIR.h.patch']
    dependencies = [x for x in Inkscape.dependencies
                    if 'poppler' not in x]
    configure_flags = (Inkscape.configure_flags
                       + ' --disable-poppler-cairo')

class Inkscape__freebsd (Inkscape):
    configure_variables = (Inkscape.configure_variables
                + ' CFLAGS=-pthread'
                + ' CXXFLAGS="-fpermissive -pthread"')
    def get_dependency_dict (self):
        return {'': (Inkscape.get_dependency_dict (self)['']
                     + ['cross/gcc-runtime']) }

class Inkscape__freebsd__x86 (Inkscape__freebsd):
    patches = ['inkscape-isfinite.patch', 'inkscape-wstring.patch',
               #'inkscape-round.patch',
               'inkscape-round-2.patch',
               ]
    def patch (self):
        Inkscape__freebsd.patch (self)
        self.file_sub ([
                ('wchar_t', 'char'),
                ('WCHAR_T', 'CHAR'),
                ],
                       '%(srcdir)s/src/util/ucompose.hpp')
    def configure (self):
        Inkscape__freebsd.configure (self)
        self.file_sub ([
                ('(/[*] config.h.  Generated)', r'''
#ifndef C99_ROUND
#define C99_ROUND
#ifdef __cplusplus
extern "C" {
#endif
double floor (double);
int sscanf(const char *str, const char *format, ...);
#ifdef __cplusplus
}
#endif
static inline double
round (double x)
{
  return (floor (x - 0.5) + 1.0);
}
static inline long long
atoll (char const *s)
{
    long long _l = 0LL;
    sscanf(s, "%%lld", &_l);
    return _l;
}
#define fmin(x,y) (x<y? x : y)
#define fmax(x,y) (x>y? x : y)
#define INFINITY (__builtin_inff())
#endif /* C99_ROUND */
\1'''),],
                       '%(builddir)s/config.h')

class Inkscape__darwin (Inkscape):
    dependencies = [x for x in Inkscape.dependencies
                if x.replace ('-devel', '') not in [
                'libxml2', # Included in darwin-sdk, hmm?
                ]]
