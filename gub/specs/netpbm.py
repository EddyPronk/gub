from gub import misc
from gub import tools

class Netpbm__tools (tools.AutoBuild):
    # source='svn:https://svn.sourceforge.net/svnroot/netpbm/stable&revision=172'
    source='http://lilypond.org/download/gub-sources/netpbm-patched-10.35.tar.bz2'
    def get_build_dependencies (self):
        return ['libjpeg', 'libpng', 'libtiff', 'zlib'] #libxml2? libx11-dev
    def configure (self):
        self.shadow ()
        self.dump ('\n'*3 + 'static\n' + '\n'*18, '%(builddir)s/answers')
        self.system ('cd %(builddir)s && %(srcdir)s/configure < answers')
    def force_sequential_build (self):
        return True
    def makeflags (self):
        '''
libpbm3.c:116: note: use -flax-vector-conversions to permit conversions between vectors with differing element types or numbers of subparts
libpbm3.c:116: fout: incompatible type for argument 1 of __builtin_ia32_pcmpeqb
'''
        return misc.join_lines ('''
CC=gcc
CFLAGS='-O2 -fPIC -flax-vector-conversions'
LDFLAGS='%(rpath)s -L%(builddir)s/pbm -L%(builddir)s/pgm -L%(builddir)s/pnm -L%(builddir)s/ppm'
LADD=-lm
LINUXSVGALIB=NONE
XML2LD=NONE
XML2_LIBS=NONE
XML2_CFLAGS=NONE
X11LIB=NONE
''')
    def install (self):
        # Great.  netpmb's install will not create any parent directories
        self.system ('mkdir -p %(install_root)s%(system_prefix)s')
        # but demands that the toplevel install directory does not yet exist.
        # It's a feature! :-)
        self.system ('rmdir %(install_root)s%(system_prefix)s')

        self.system ('cd %(builddir)s && make package pkgdir=%(install_root)s%(system_prefix)s %(makeflags)s')
        # Huh, we strip stuff in installer.py, no?  Hmm.
        self.system ('''rm -rf %(install_prefix)s/misc 
rm -rf %(install_root)s%(system_prefix)s/README
rm -rf %(install_root)s%(system_prefix)s/VERSION
rm -rf %(install_root)s%(system_prefix)s/link
rm -rf %(install_root)s%(system_prefix)s/misc
rm -rf %(install_root)s%(system_prefix)s/man
rm -rf %(install_root)s%(system_prefix)s/pkginfo
rm -rf %(install_root)s%(system_prefix)s/config_template
''')
    def license_files (self):
        return '%(srcdir)s/README'
