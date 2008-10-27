from gub import toolsbuild

class Netpbm__tools (toolsbuild.AutoBuild):
    # source='svn:https://svn.sourceforge.net/svnroot/netpbm/stable&revision=172'
    source='http://lilypond.org/download/gub-sources/netpbm-patched-10.35.tar.bz2'

    def get_build_dependencies (self):
        return ['libjpeg'] # libtiff-dev libx11-dev

    def configure (self):
        self.shadow ()
        self.dump ('\n'*3 + 'static\n' + '\n'*18, '%(builddir)s/answers')
        self.system ('cd %(builddir)s && %(srcdir)s/configure < answers')

        '''
libpbm3.c:116: note: use -flax-vector-conversions to permit conversions between vectors with differing element types or numbers of subparts
libpbm3.c:116: fout: incompatible type for argument 1 of __builtin_ia32_pcmpeqb
'''
    def compile (self):
        self.system ('''cd %(builddir)s && make CC=gcc \
        CFLAGS="-O2 -fPIC -flax-vector-conversions"  \
        LDFLAGS="-L%(builddir)s/pbm -L%(builddir)s/pgm -L%(builddir)s/pnm -L%(builddir)s/ppm" \
        LADD="-lm" \
        LINUXSVGALIB="NONE" \
        XML2LIBS="NONE" \
        X11LIB="NONE"
''')
    def install (self):
        self.system ('mkdir -p %(install_root)s/')
        self.system ('cd %(builddir)s && make package pkgdir=%(install_prefix)s LINUXSVGALIB="NONE" XML2LIBS="NONE" X11LIB="NONE"')
        self.system ('''rm -rf %(install_prefix)s/misc 
rm -rf %(install_prefix)s/README
rm -rf %(install_prefix)s/VERSION
rm -rf %(install_prefix)s/link
rm -rf %(install_prefix)s/misc
rm -rf %(install_prefix)s/man
rm -rf %(install_prefix)s/pkginfo
rm -rf %(install_prefix)s/config_template
''')
    def packaging_suffix_dir (self):
        return ''

    def license_files (self):
        return '%(srcdir)s/README'
