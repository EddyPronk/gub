from gub import toolsbuild 

class Fontforge__tools (toolsbuild.AutoBuild):
    source = 'http://lilypond.org/download/gub-sources/fontforge_full-20080927.tar.bz2'

    def configure_command (self):
        return (toolsbuild.AutoBuild.configure_command (self)
                + ' --without-freetype-src'
                + ' --disable-libff '
                # let's ignore python (and its dynamic link intracies
                # for now).
                + ' --without-python')

    def configure (self):
        self.shadow ()
        toolsbuild.AutoBuild.configure (self)

    def get_build_dependencies (self):
        return ['freetype']

    def srcdir (self):
        return toolsbuild.AutoBuild.srcdir (self).replace ('_full', '')

    def force_sequential_build (self):
        return True
    
    # actions.
    def patch (self):
        toolsbuild.AutoBuild.patch (self)
        for name in ['%(srcdir)s/fontforge/Makefile.dynamic.in',
             '%(srcdir)s/fontforge/Makefile.static.in',
             '%(srcdir)s/gdraw/Makefile.dynamic.in',
             '%(srcdir)s/gdraw/Makefile.static.in',
             '%(srcdir)s/gutils/Makefile.dynamic.in',
             '%(srcdir)s/gutils/Makefile.static.in',
             '%(srcdir)s/Unicode/Makefile.dynamic.in',
             '%(srcdir)s/Unicode/Makefile.static.in']:
            self.file_sub (
                [(' -I$(top_srcdir)/inc',
                  ' -I$(top_srcdir)/inc -I$(top_builddir)/inc')],
                name, use_re=False)
