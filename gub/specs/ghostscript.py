import re
#
from gub.syntax import printf
from gub import context
from gub import misc
from gub import repository
from gub import target
from gub import tools

# FIXME: static for now
#  - shell_rpath hack does not work anymore
#  - mingw untested
#  - obj/sobj
shared = False
dynamic = False

class Ghostscript (target.AutoBuild):
    '''The GPL Ghostscript PostScript interpreter
Ghostscript is used for PostScript preview and printing.  It can
display PostScript documents in an X11 environment.  It can render
PostScript files as graphics to be printed on non-PostScript printers.
Supported printers include common dot-matrix, inkjet and laser
models.'''

    #source = 'svn:http://svn.ghostscript.com:8080/ghostscript&branch=trunk/gs&revision=7881'
    # HEAD - need to load TTF fonts on fedora without crashing.
    revision = 'b35333cf3579e85725bd7d8d39eacc9640515eb8'
    #source = 'git://git.infradead.org/ghostscript.git?branch=refs/remotes/git-svn&revision=' + revision
    source = 'http://mirror2.cs.wisc.edu/pub/mirrors/ghost/GPL/gs870/ghostscript-8.70.tar.gz'
    parallel_build_broken = True
    # For --enable-compile-inits, see comment in compile()
    configure_flags = (target.AutoBuild.configure_flags
                       + misc.join_lines ('''
--enable-debug
--with-drivers=FILES
--without-pdftoraster
--disable-fontconfig 
--disable-gtk
--disable-cairo
--without-x
--disable-cups
--without-ijs
--without-omni
--without-jasper
--disable-compile-inits
'''))
    if dynamic:
        configure_flags = (configure_flags
                           .replace ('--disable-static', '--enable-dynamic'))
    compile_flags = (' INCLUDE=%(system_prefix)s/include'
                     + ' PSDOCDIR=%(prefix_dir)s/share/doc'
                     + ' PSMANDIR=%(prefix_dir)s/share/man'
                     + r''' XLDFLAGS='%(shell_rpath)s' ''')
    install_command = (target.AutoBuild.install_command
                + ' install_prefix=%(install_root)s'
                + ' mandir=%(prefix_dir)s/share/man/ '
                + ' docdir=%(prefix_dir)s/share/doc/ghostscript/doc '
                + ' exdir=%(prefix_dir)s/share/doc/ghostscript/examples ')
    @staticmethod
    def static_version ():
        return misc.version_from_url (Ghostscript.source)
    obj = 'obj'
    if shared:
        obj = 'sobj'
        compile_flags = compile_flags + ' so'
        install_flags = (target.AutoBuild.install_flags
                         .replace (' install', ' soinstall'))
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        if (isinstance (source, repository.Repository)
            and not isinstance (source, repository.TarBall)):
            source.version = misc.bind_method (Ghostscript.version_from_VERSION, source)
    @staticmethod
    def version_from_VERSION (self):
        try:
            s = self.read_file ('base/version.mak')
            if not 'GS_VERSION_MAJOR' in s:
                urg
            d = misc.grok_sh_variables_str (s)
            return '%(GS_VERSION_MAJOR)s.%(GS_VERSION_MINOR)s' % d
        except:
            pass
        return '0.0'
    dependencies = ['libjpeg-devel', 'libpng-devel']
    subpackage_names = ['doc', '']
    def srcdir (self):
        return re.sub ('-source', '',
                       target.AutoBuild.srcdir (self))
    def builddir (self):
        return re.sub ('-source', '',
                       target.AutoBuild.builddir (self))
    def name (self):
        return 'ghostscript'
    def autoupdate (self):
        # generate Makefile.in
        self.system ('cd %(srcdir)s && sh ./autogen.sh --help')
        disable_re = ('(DEVICE_DEVS[0-9]+)=([^\n]+(%s))'
                      % '|'.join (['tiff', 'pcx', 'uniprint',
                                   'deskjet', 'djet500', 'bmp', 'pbm',
                                   'bjc200', 'cdeskjet', 'faxg3', 'cljet5']))
        self.file_sub ([(disable_re, r'#\1= -DISABLED- \2 ')],
                       '%(srcdir)s/Makefile.in')
    def fixup_arch (self):
        # FIXME: wow, this is broken, cross-compile-wise.  Use a compiled
        # c program to determine the size of basic types *after* an
        # autoconf run.  Should see if afpl ghostscript also uses autoconf
        # and send a patch that generates arch.h from configure.

        cache_size = 1024*1024
        big_endian = 0
        can_shift = 1
        align_long_mod = 4
        align_ptr_mod = 4
        log2_sizeof_long = 2
        sizeof_ptr = 4
        
        if 'powerpc' in self.settings.target_architecture:
            big_endian = 1
            can_shift = 1
            cache_size = 2097152
        elif re.search ('i[0-9]86', self.settings.target_architecture):
            big_endian = 0
            can_shift = 0
            cache_size = 1048576

        if '64' in self.settings.target_architecture:
            align_long_mod = 8
            align_ptr_mod = 8
            log2_sizeof_long = 3
            sizeof_ptr = 8

        # obsolete
        self.file_sub (
            [('#define ARCH_CAN_SHIFT_FULL_LONG .',
              '#define ARCH_CAN_SHIFT_FULL_LONG %(can_shift)d' % locals ()),
             ('#define ARCH_CACHE1_SIZE [0-9]+',
              '#define ARCH_CACHE1_SIZE %(cache_size)d' % locals ()),
             ], '%(builddir)s/%(obj)s/arch.h')
        
        # cannot use: must_succeed=5, they may be okay..
        self.file_sub ([
             ('#define ARCH_IS_BIG_ENDIAN [0-9]',
              '#define ARCH_IS_BIG_ENDIAN %(big_endian)d' % locals ()),
             ('#define ARCH_ALIGN_LONG_MOD [0-9]',
              '#define ARCH_ALIGN_LONG_MOD %(align_long_mod)d' % locals ()),
             ('#define ARCH_ALIGN_PTR_MOD [0-9]',
              '#define ARCH_ALIGN_PTR_MOD %(align_ptr_mod)d' % locals ()),
             ('#define ARCH_LOG2_SIZEOF_LONG [0-9]',
              '#define ARCH_LOG2_SIZEOF_LONG %(log2_sizeof_long)d' % locals ()),
             ('#define ARCH_SIZEOF_PTR [0-9]',
              '#define ARCH_SIZEOF_PTR %(sizeof_ptr)d' % locals ()),
             ], '%(builddir)s/%(obj)s/arch.h')

    def configure (self):
        target.AutoBuild.configure (self)
        self.makefile_fixup ('%(builddir)s/Makefile')
    def makefile_fixup (self, file):
        self.file_sub ([
            ('-Dmalloc=rpl_malloc', ''),
            ('GLSRCDIR=./base', 'GLSRCDIR=%(srcdir)s/base'),
            ('PSSRCDIR=./psi', 'PSSRCDIR=%(srcdir)s/psi'),
            ('PSLIBDIR=./lib', 'PSLIBDIR=%(srcdir)s/lib'),
            ('PSRESDIR=./Resource', 'PSRESDIR=%(srcdir)s/Resource'),
            ('ICCSRCDIR=icclib', 'ICCSRCDIR=%(srcdir)s/icclib'),
            ('IJSSRCDIR=src', 'IJSSRCDIR=%(srcdir)s/src'),
            ('IMDISRCDIR=imdi', 'IMDISRCDIR=%(srcdir)s/imdi'),
            ('CONTRIBDIR=./contrib', 'CONTRIBDIR=%(srcdir)s/contrib'),
            ('include contrib/', 'include %(srcdir)s/contrib/'),
            # ESP-specific: addonsdir, omit zillion of
            # warnings (any important ones may be noticed
            # easier).
            ('ADDONSDIR=./addons', 'ADDONSDIR=%(srcdir)s/addons'),
            (' -Wmissing-prototypes ', ' '),
            (' -Wstrict-prototypes ', ' '),
            (' -Wmissing-declarations ', ' '),

            ## ugh:  GS compile adds another layer of shell expansion. Yuck.
            (r'\$\${ORIGIN}', '\\$${ORIGIN}'),
            ],
               file)

    @context.subst_method
    def shell_rpath (self):
        return self.rpath ().replace (r'\$', r'\\\$')

    def compile (self):
        # obj/mkromfs is needed for --enable-compile-inits but depends on native -liconv.
        self.system ('''
cd %(builddir)s && mkdir -p %(obj)s
cd %(builddir)s && make CC=cc CCAUX=cc C_INCLUDE_PATH= CFLAGS= CPPFLAGS= GCFLAGS= LIBRARY_PATH= OBJ=build-o %(obj)s/genconf %(obj)s/echogs %(obj)s/genarch %(obj)s/arch.h 
''')
        self.fixup_arch ()
        target.AutoBuild.compile (self)

    def install (self):
        target.AutoBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s/etc/relocate/')
        self.dump ('''
prependdir GS_FONTPATH=$INSTALLER_PREFIX/share/ghostscript/%(version)s/fonts
prependdir GS_FONTPATH=$INSTALLER_PREFIX/share/gs/fonts
prependdir GS_LIB=$INSTALLER_PREFIX/share/ghostscript/%(version)s/Resource
prependdir GS_LIB=$INSTALLER_PREFIX/share/ghostscript/%(version)s/Resource/Init
''', '%(install_prefix)s/etc/relocate/gs.reloc')
        if shared:
            self.system ('mv %(install_prefix)s/bin/gsc %(install_prefix)s/bin/gs')

class Ghostscript__mingw (Ghostscript):
    # source = 'ftp://mirror.cs.wisc.edu/pub/mirrors/ghost/GPL/gs860/ghostscript-8.60.tar.bz2'
    patches = ['ghostscript-8.65-mingw.patch']
    def __init__ (self, settings, source):
        Ghostscript.__init__ (self, settings, source)
        # Configure (compile) without -mwindows for console
        # FIXME: should add to CPPFLAGS...
        self.target_gcc_flags = '-mms-bitfields -D_Windows -D__WINDOWS__'
    config_cache_overrides = Ghostscript.config_cache_overrides + '''
ac_cv_lib_pthread_pthread_create=no
'''
    def patch (self):
        self.symlink('base', self.expand('%(srcdir)s/src'))
        Ghostscript.patch (self)
    def configure (self):
        Ghostscript.configure (self)
        if dynamic: # Dynamic is a configure cross-compile disaster area,
            # it uses BUILD's uname to determine HOST libraries.
            self.file_sub ([('^(EXTRALIBS *=.*)(-ldl )', r'\1'),
                            ('^(EXTRALIBS *=.*)(-rdynamic )', r'\1')],
                           '%(builddir)s/Makefile')
        self.file_sub ([('^(EXTRALIBS *=.*)', r'\1 -lwinspool -lcomdlg32 -lz')],
                       '%(builddir)s/Makefile')
        self.file_sub ([('^unix__=.*', misc.join_lines ('''unix__=
$(GLOBJ)gp_mswin.$(OBJ)
$(GLOBJ)gp_wgetv.$(OBJ)
$(GLOBJ)gp_stdia.$(OBJ)
$(GLOBJ)gp_ntfs.$(OBJ)
$(GLOBJ)gp_win32.$(OBJ)
$(GLOBJ)gp_upapr.$(OBJ) 
'''))],
               '%(srcdir)s/base/unix-aux.mak')        
        self.dump ('''
GLCCWIN=$(CC) $(CFLAGS) -I$(GLOBJDIR)
PSCCWIN=$(CC) $(CFLAGS) -I$(GLOBJDIR)

include $(GLSRCDIR)/winplat.mak
''',
             '%(builddir)s/Makefile',
             mode='a')

class Ghostscript__freebsd (Ghostscript):
    dependencies = Ghostscript.dependencies + ['libiconv-devel']

class Ghostscript__tools (tools.AutoBuild, Ghostscript):
    parallel_build_broken = True
    dependencies = ['libjpeg', 'libpng']
    configure_flags = (tools.AutoBuild.configure_flags
                       + Ghostscript.configure_flags)
    make_flags = Ghostscript.make_flags
    def configure (self):
        tools.AutoBuild.configure (self)
        self.makefile_fixup ('%(builddir)s/Makefile')
    def compile (self):
        self.system ('''
cd %(builddir)s && mkdir -p obj
cd %(builddir)s && make CC=cc CCAUX=cc C_INCLUDE_PATH= CFLAGS= CPPFLAGS= GCFLAGS= LIBRARY_PATH= obj/genconf obj/echogs obj/genarch obj/arch.h
cd %(builddir)s && make INCLUDE=/usr/include gconfig__h=gconfig_-native.h gconfig_-native.h
cd %(builddir)s && make INCLUDE=%(system_prefix)s/include gconfig__h=gconfig_-tools.h gconfig_-tools.h
cd %(builddir)s && sort -u gconfig_-native.h gconfig_-tools.h > obj/gconfig_.h
''')
#        self.fixup_arch ()
        tools.AutoBuild.compile (self)
    install_command = (tools.AutoBuild.install_command
                + ' install_prefix=%(install_root)s'
                + ' mandir=%(prefix_dir)s/share/man/ '
                + ' docdir=%(prefix_dir)s/share/doc/ghostscript/doc '
                + ' exdir=%(prefix_dir)s/share/doc/ghostscript/examples '
                )

def test ():
    printf ('Ghostscript.static_version:', Ghostscript.static_version ())

if __name__ =='__main__':
    test ()
