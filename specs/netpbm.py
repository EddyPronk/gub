import download
import toolpackage
import repository

class Netpbm (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)

        # https://svn.sourceforge.net/svnroot/netpbm/advanced netpbm

        repo = repository.Subversion (
            dir=self.get_repodir (),
            source='https://svn.sourceforge.net/svnroot/',
            branch='netpbm',
            module='stable',
            revision="172")

        
        # self.with_vc (repo)
        self.with (mirror='http://lilypond.org/download/gub-sources/netpbm-patched-10.35.tar.bz2',
                   version='10.35')

    def configure (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        self.dump ('\n'*3 + 'static\n' + '\n'*18, '%(builddir)s/answers')

        self.system ('cd %(builddir)s && %(srcdir)s/configure < answers')

    def compile (self):
        self.system ('''cd %(builddir)s && make CC=gcc \
        CFLAGS="-O2 -fPIC"  \
        LDFLAGS="-L%(builddir)s/pbm -L%(builddir)s/pgm -L%(builddir)s/pnm -L%(builddir)s/ppm" \
        LADD="-lm" \
        LINUXSVGALIB="NONE" \
        XML2LIBS="NONE"

''')
    def install (self):
        self.system ('mkdir -p %(install_root)s/')
        self.system ('cd %(builddir)s && make package pkgdir=%(install_root)s/usr LINUXSVGALIB="NONE" XML2LIBS="NONE"')
        self.system ('''rm -rf %(install_root)s/usr/misc 
rm -rf %(install_root)s/usr/README
rm -rf %(install_root)s/usr/VERSION
rm -rf %(install_root)s/usr/link
rm -rf %(install_root)s/usr/misc
rm -rf %(install_root)s/usr/man
rm -rf %(install_root)s/usr/pkginfo
rm -rf %(install_root)s/usr/config_template
''')
    def packaging_suffix_dir (self):
        return ''

    def license_file (self):
        return '%(srcdir)s/README'
    
        foo = '''
        X11LIB=%{_libdir}/libX11.so \
        JPEGINC_DIR=%{_includedir} \
        PNGINC_DIR=%{_includedir} \
        TIFFINC_DIR=%{_includedir} \
        JPEGLIB_DIR=%{_libdir} \
        PNGLIB_DIR=%{_libdir} \
        TIFFLIB_DIR=%{_libdir} \
        '''
