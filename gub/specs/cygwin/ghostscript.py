from gub.syntax import printf
from gub import context
from gub import misc
from gub import repository
from gub.specs import ghostscript

url='http://mirror3.cs.wisc.edu/pub/mirrors/ghost/GPL/gs860/ghostscript-8.60.tar.gz'
url='http://mirror3.cs.wisc.edu/pub/mirrors/ghost/GPL/gs850/ghostscript-8.50-gpl.tar.gz'

#8250
class Ghostscript (ghostscript.Ghostscript):
    patches = ['ghostscript-8.15-windows-wb.patch',
               'ghostscript-8.57-cygwin-esp.patch']
    def __init__ (self, settings, source):
        ghostscript.Ghostscript.__init__ (self, settings, source)
        self.fonts_source = repository.get_repository_proxy (self.settings.downloads, 'http://mirror2.cs.wisc.edu/pub/mirrors/ghost/GPL/gs860/ghostscript-fonts-std-8.11.tar.gz')
    def connect_command_runner (self, runner):
        printf ('FIXME: deferred workaround: should support multiple sources')
        if (runner):
            self.fonts_source.connect_logger (runner.logger)
        return ghostscript.Ghostscript.connect_command_runner (self, runner)
    def download (self):
        ghostscript.Ghostscript.download (self)
        self.fonts_source.download ()
    def autoupdate (self):
        self.system ('''
cd %(srcdir)s && sh ./autogen.sh --help
cd %(srcdir)s && cp Makefile.in Makefile-x11.in
''')
    def patch (self):
        from gub import cygwin
        cygwin.libpng12_fixup (self)
        ghostscript.Ghostscript.patch (self)
    def category_dict (self):
        return {'': 'Graphics'}
    def get_build_dependencies (self): #cygwin
        return ['jpeg', 'libpng12-devel', 'libXext-devel', 'libXt-devel', 'libX11-devel', 'zlib']
    def get_dependency_dict (self): #cygwin
        return {'': [
                # REMOVE after first cygwin release.
                'ghostscript-base',
                'libjpeg62', 'libpng12', 'zlib'],
                'x11': ['ghostscript', 'xorg-x11-base']}
    subpackage_names = ['doc', 'x11', '',
                # REMOVE after first cygwin release.
                'base']
    # REMOVE after first cygwin release.
    def get_subpackage_definitions (self):
        d = ghostscript.Ghostscript.get_subpackage_definitions (self)
        d['base'] = []
        return d
    configure_flags = (ghostscript.Ghostscript.configure_flags
                .replace (' --with-drivers=FILES', ' --with-drivers=ALL'))
    def compile (self):
        self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && rm -f obj/*.tr
''')
        ghostscript.Ghostscript.compile (self)
# X11 stuff
    def stages (self):
        return misc.list_insert_before (ghostscript.Ghostscript.stages (self),
                                        'package',
                                        ['configure_x11', 'compile_x11',
                                         'install_x11', 'install_fonts'])
    def config_cache (self):
        ghostscript.Ghostscript.config_cache (self)
        self.system ('cd %(builddir)s && cp -p config.cache config-x11.cache')
    @context.subst_method
    def configure_variables_x11 (self):
        return ('CONFIG_FILES=Makefile-x11'
                + ' CONFIG_STATUS=config-x11.status')
    @context.subst_method
    def configure_command_x11 (self):
        return ' sh %(configure_binary)s %(configure_flags_x11)s %(configure_variables_x11)s Makefile'
    @context.subst_method
    def configure_flags_x11 (self):
        return (self.configure_flags
                .replace ('--without-x', '--with-x')
                .replace ('config.cache', 'config-x11.cache')
                + ' --x-includes=%(system_prefix)s/X11R6/include'
                + ' --x-libraries=%(system_prefix)s/X11R6/lib')
    def configure_x11 (self):
        self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command_x11)s
''')
        self.makefile_fixup ('%(builddir)s/Makefile-x11')
    @context.subst_method
    def compile_command_x11 (self):
        return ghostscript.Ghostscript.compile_command + ' -f Makefile-x11 GS=gs-x11.exe'
    def compile_x11 (self):
        self.system ('''
cd %(builddir)s && rm -f obj/*.tr
cd %(builddir)s && %(compile_command_x11)s
''')
    @context.subst_method
    def install_command_x11 (self):
        return (ghostscript.Ghostscript.install_command
                .replace (' install ', ' install-exec ')
                + ' -f Makefile-x11 GS=gs-x11.exe prefix=/usr/X11R6')
    def install_x11 (self):
        self.system ('''
cd %(builddir)s && %(install_command_x11)s
cd %(install_prefix)s && rm -rf usr/X11R6/share
''')
    def install_fonts (self):
        printf ('FIXME: deferred workaround')
#        deferred_dump (self.font_source.update_workdir (fontdir))
        fontdir = self.expand ('%(install_prefix)s/share/ghostscript/fonts')
        def defer (logger):
            self.fonts_source.update_workdir (fontdir)
        self.func (defer)
        # Link to binmode to fix text mode mount problem
        # http://cygwin.com/ml/cygwin/2002-07/msg02302.html
        # although text mode mounts are considered evil...
    make_flags = ' CFLAGS_STANDARD="-g -O2" EXTRALIBS=-lbinmode'
    # REMOVE after first cygwin release.
    def description_dict (self):
        return {'base': 'The GPL Ghostscript PostScript interpreter - transitional package\nThis is an empty package to streamline the upgrade.'}
