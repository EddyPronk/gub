from gub import commands 
from gub import toolsbuild 
from gub import mirrors

class Fontforge (toolsbuild.ToolsBuild):
    source = 'http://lilypond.org/download/gub-sources/fontforge_full-20071210.tar.bz2'

    auto_source = mirrors.with_template (name='fontforge', mirror='http://lilypond.org/download/gub-sources/fontforge_full-%(version)s.tar.bz2',
                   version='20070607')

    # build settings
    def configure_command (self):
        return (toolsbuild.ToolsBuild.configure_command (self)
                + ' --without-freetype-src'

                # urgh - I just love libtool relinking.
                + ' --enable-static --disable-shared'
                # let's ignore python (and its dynamic link intracies
                # for now).
                + ' --without-python')

    def get_build_dependencies (self):
        return ['freetype']

    def install_command (self):
        return self.broken_install_command ()

    def packaging_suffix_dir (self):
        return ''

    def srcdir (self):
        return toolsbuild.ToolsBuild.srcdir (self).replace ('_full', '')
    def force_sequential_build (self):
        return True
    
    # actions.
    def patch (self):
        toolsbuild.ToolsBuild.patch (self)
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
                    
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
