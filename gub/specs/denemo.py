'''
TODO:
  * figure out solution pango/pangocairo, lilypond/lilypondcairo mess
  * build denemo from GIT, use lilypond[cairo] from tarball 2.12.3/2.13.3?
  * try: denemo for linux, all audio and X dependencies?
  * try: adding jack on windows
  * what about timidity?
  * upstream all denemo patches
  * prefopts: move initial values into config file, instead of patching C code?
  * relocation: non-windows dynamic relocation in main.c
  * relocation: fix locale dir
  * font: Denemo.ttf?
'''

from gub import misc
from gub import repository
from gub import target

class Denemo (target.AutoBuild):
    source = 'git://git.savannah.gnu.org/denemo.git'
    #source = 'http://download.savannah.gnu.org/releases/denemo/denemo-0.8.6.tar.gz'
    # in denemo GIT now
    patches_0_8_6 = [
        'denemo-srcdir-make.patch',
        'denemo-relocate.patch'
        ]
    @staticmethod
    def version_from_configure_in (self):
        return self.version_from_configure_in ()
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        if isinstance (source, repository.Git):
            source.version = misc.bind_method (Denemo.version_from_configure_in, source)
        else:
            return
            def tracking (self):
                return True
            # let's keep srdir around for now
            self.source.is_tracking = misc.bind_method (tracking, self.source)
    def get_subpackage_names (self):
        return ['']
    def _get_build_dependencies (self):
        return [
            'tools::automake',
            'tools::gettext',
            'tools::libtool',
            'tools::pkg-config',
            'epdfview', # Hmm
            'guile-devel',
            'gtk+-devel',
            'jack-devel',
            'lash-devel',
            'libaubio-devel',
            'libgtksourceview-devel',
            'librsvg-devel', 
            'libxml2-devel',
            'lilypondcairo',
            'portaudio-devel',
            ]
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': [x.replace ('-devel', '')
                     for x in self._get_build_dependencies ()
                     if 'tools::' not in x and 'cross/' not in x]
                + [
                'cross/gcc-c++-runtime',
                ]
                }
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --enable-binreloc'
                + ' --enable-jack'
                + ' --program-prefix=')
    def compile (self):
        if isinstance (self.source, repository.Git):
            # FIXME: missing dependency
            self.system ('cd %(builddir)s/src && make lylexer.c')
        target.AutoBuild.compile (self)
    def makeflags (self):
        return 'BINRELOC_CFLAGS=-DENABLE_BINRELOC=1'

class Denemo__mingw (Denemo):
    patches_0_8_6 = Denemo.patches + [
        'denemo-mingw.patch',
        'denemo-prefops-mingw.patch',
        'denemo-relocate-mingw.patch',
        ]
    def __init__ (self, settings, source):
        Denemo.__init__ (self, settings, source)
        # Configure (link) without -mwindows for denemo-console.exe
        self.target_gcc_flags = '-mms-bitfields'
    def _get_build_dependencies (self):
        return [x for x in Denemo._get_build_dependencies (self)
                if x.replace ('-devel', '') not in [
                'jack',
                'lash',
                ]] + ['lilypad']
    def configure_command (self):
        return (Denemo.configure_command (self)
                .replace ('--enable-jack', '--disable-jack'))
    def makeflags (self):
        return ''
    def compile (self):
        Denemo.compile (self)
        self.system ('''
cd %(builddir)s/src && mv .libs/denemo.exe denemo-console.exe && rm -f denemo.exe
cd %(builddir)s/src && make AM_LDFLAGS="-mwindows" && cp -p .libs/denemo.exe denemo-windows.exe
''')
    def install (self):
        Denemo.install (self)
        self.system ('''
install -m755 %(builddir)s/src/denemo-windows.exe %(install_prefix)s/bin/denemo.exe
install -m755 %(builddir)s/src/denemo-console.exe %(install_prefix)s/bin/denemo-console.exe
''')

class Denemo__darwin (Denemo):
    def _get_build_dependencies (self):
        return [x for x in Denemo._get_build_dependencies (self)
                if x.replace ('-devel', '') not in [
                'jack',
                'lash',
                'libxml2', # Included in darwin-sdk, hmm?
                ]] + [
            'fondu',
            'osx-lilypad',
            ]
    def configure_command (self):
        return (Denemo.configure_command (self)
                .replace ('--enable-jack', '--disable-jack'))
