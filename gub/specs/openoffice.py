import operator
import os
import re
#
from gub.syntax import printf
from gub import context
from gub import loggedos
from gub import misc
from gub import octal
from gub import repository
from gub import target
from gub import tools

# If TRUE: do not build tools::OpenOffice, rather use user-prebuilt
# tools from $OOO_TOOLS_DIR.  Obsolete.
out_of_gub_OOO_TOOLS_DIR = False

'''
Module 'solenv' delivered successfully. 0 files copied, 1 files unchanged
Module 'stlport' delivered successfully. 0 files copied, 8 files unchanged
Module 'soltools' delivered successfully. 0 files copied, 14 files unchanged
Module 'external' delivered successfully. 0 files copied, 30 files unchanged
Module 'libwpd' delivered successfully. 0 files copied, 12 files unchanged
Module 'xml2cmp' delivered successfully. 0 files copied, 5 files unchanged
Module 'sal' delivered successfully. 11 files copied, 99 files unchanged
Module 'vos' delivered successfully. 0 files copied, 31 files unchanged
Module 'sandbox' delivered successfully. 0 files copied, 2 files unchanged
Module 'afms' delivered successfully. 0 files copied, 2 files unchanged
Module 'beanshell' delivered successfully. 0 files copied, 2 files unchanged
Module 'cppunit' delivered successfully. 4 files copied, 65 files unchanged
Module 'testshl2' delivered successfully. 0 files copied, 12 files unchanged
Module 'salhelper' delivered successfully. 0 files copied, 12 files unchanged
Module 'extras' delivered successfully. 0 files copied, 70 files unchanged
Module 'fondu' delivered successfully. 0 files copied, 2 files unchanged
Module 'hsqldb' delivered successfully. 0 files copied, 2 files unchanged
Module 'hunspell' delivered successfully. 0 files copied, 15 files unchanged
Module 'hyphen' delivered successfully. 0 files copied, 5 files unchanged
Module 'icc' delivered successfully. 0 files copied, 2 files unchanged
Module 'libtextcat' delivered successfully. 0 files copied, 81 files unchanged
Module 'libwpg' delivered successfully. 0 files copied, 16 files unchanged
Module 'libwps' delivered successfully. 0 files copied, 6 files unchanged
Module 'libxmlsec' delivered successfully. 0 files copied, 1 files unchanged
Module 'lucene' delivered successfully. 0 files copied, 1 files unchanged
Module 'np_sdk' delivered successfully. 0 files copied, 9 files unchanged
Module 'o3tl' delivered successfully. 0 files copied, 5 files unchanged
Module 'psprint_config' delivered successfully. 0 files copied, 1 files unchanged
Module 'rhino' delivered successfully. 0 files copied, 2 files unchanged
Module 'sane' delivered successfully. 0 files copied, 2 files unchanged
Module 'store' delivered successfully. 0 files copied, 8 files unchanged
Module 'registry' delivered successfully. 0 files copied, 23 files unchanged
Module 'idlc' delivered successfully. 0 files copied, 7 files unchanged
Module 'udkapi' delivered successfully. 1 files copied, 417 files unchanged
Module 'offapi' delivered successfully. 3 files copied, 3518 files unchanged
Module 'codemaker' delivered successfully. 0 files copied, 23 files unchanged
Module 'offuh' delivered successfully. 0 files copied, 5518 files unchanged
Module 'cppu' delivered successfully. 0 files copied, 47 files unchanged
Module 'cppuhelper' delivered successfully. 0 files copied, 65 files unchanged
Module 'rdbmaker' delivered successfully. 0 files copied, 4 files unchanged
Module 'ucbhelper' delivered successfully. 0 files copied, 35 files unchanged
Module 'comphelper' delivered successfully. 0 files copied, 107 files unchanged
Module 'basegfx' delivered successfully. 4 files copied, 65 files unchanged
Module 'ridljar' delivered successfully. 0 files copied, 5 files unchanged
Module 'jurt' delivered successfully. 0 files copied, 4 files unchanged
Module 'jvmaccess' delivered successfully. 0 files copied, 6 files unchanged
Module 'bridges' delivered successfully. 1 files copied, 9 files unchanged
Module 'jvmfwk' delivered successfully. 0 files copied, 15 files unchanged
Module 'stoc' delivered successfully. 0 files copied, 28 files unchanged
Module 'cli_ure' delivered successfully. 0 files copied, 6 files unchanged
Module 'unoil' delivered successfully. 0 files copied, 5 files unchanged
Module 'javaunohelper' delivered successfully. 0 files copied, 3 files unchanged
Module 'cpputools' delivered successfully. 0 files copied, 13 files unchanged
Module 'oovbaapi' delivered successfully. 0 files copied, 2 files unchanged
Module 'sax' delivered successfully. 2 files copied, 7 files unchanged
Module 'animations' delivered successfully. 0 files copied, 5 files unchanged
Module 'i18nutil' delivered successfully. 0 files copied, 8 files unchanged
Module 'io' delivered successfully. 0 files copied, 12 files unchanged
Module 'jut' delivered successfully. 0 files copied, 3 files unchanged
Module 'remotebridges' delivered successfully. 0 files copied, 17 files unchanged
Module 'bean' delivered successfully. 0 files copied, 4 files unchanged
Module 'embedserv' delivered successfully. 0 files copied, 1 files unchanged
Module 'eventattacher' delivered successfully. 0 files copied, 2 files unchanged
Module 'hwpfilter' delivered successfully. 0 files copied, 4 files unchanged
Module 'package' delivered successfully. 0 files copied, 6 files unchanged
Module 'regexp' delivered successfully. 0 files copied, 4 files unchanged
Module 'i18npool' delivered successfully. 1 files copied, 40 files unchanged
Module 'tools' delivered successfully. 14 files copied, 92 files unchanged
Module 'unotools' delivered successfully. 3 files copied, 44 files unchanged
Module 'transex3' delivered successfully. 11 files copied, 22 files unchanged
Module 'sot' delivered successfully. 4 files copied, 17 files unchanged
Module 'fileaccess' delivered successfully. 1 files copied, 3 files unchanged
Module 'officecfg' delivered successfully. 1 files copied, 224 files unchanged
Module 'setup_native' delivered successfully. 1 files copied, 57 files unchanged
Module 'rsc' delivered successfully. 2 files copied, 6 files unchanged
Module 'oox' delivered successfully. 1 files copied, 8 files unchanged
Module 'psprint' delivered successfully. 0 files copied, 14 files unchanged
Module 'pyuno' delivered successfully. 0 files copied, 21 files unchanged
Module 'sysui' delivered successfully. 4 files copied, 128 files unchanged
Module 'UnoControls' delivered successfully. 1 files copied, 1 files unchanged
Module 'dtrans' delivered successfully. 3 files copied, 9 files unchanged
Module 'idl' delivered successfully. 1 files copied, 2 files unchanged
Module 'readlicense_oo' delivered successfully. 0 files copied, 12 files unchanged
Module 'sccomp' delivered successfully. 1 files copied, 3 files unchanged
Module 'scp2' delivered successfully. 9 files copied, 82 files unchanged
Module 'testtools' delivered successfully. 0 files copied, 1 files unchanged
Module 'twain' delivered successfully. 0 files copied, 2 files unchanged
Module 'unodevtools' delivered successfully. 0 files copied, 4 files unchanged
Module 'unoxml' delivered successfully. 0 files copied, 3 files unchanged
Module 'ure' delivered successfully. 0 files copied, 9 files unchanged
Module 'vigra' delivered successfully. 0 files copied, 83 files unchanged
Module 'basebmp' delivered successfully. 2 files copied, 35 files unchanged
Module 'wizards' delivered successfully. 0 files copied, 27 files unchanged
Module 'x11_extensions' delivered successfully. 0 files copied, 7 files unchanged
Module 'vcl' delivered successfully. 3 files copied, 140 files unchanged
Module 'toolkit' delivered successfully. 2 files copied, 55 files unchanged
Module 'svtools' delivered successfully. 15 files copied, 300 files unchanged
Module 'uui' delivered successfully. 2 files copied, 4 files unchanged
Module 'goodies' delivered successfully. 27 files copied, 62 files unchanged
Module 'xmloff' delivered successfully. 3 files copied, 124 files unchanged
Module 'ucb' delivered successfully. 0 files copied, 35 files unchanged
Module 'canvas' delivered successfully. 5 files copied, 39 files unchanged
Module 'configmgr' delivered successfully. 0 files copied, 9 files unchanged
Module 'connectivity' delivered successfully. 11 files copied, 71 files unchanged
Module 'xmlscript' delivered successfully. 0 files copied, 12 files unchanged
Module 'fpicker' delivered successfully. 5 files copied, 7 files unchanged
Module 'framework' delivered successfully. 6 files copied, 35 files unchanged
Module 'xmlhelp' delivered successfully. 0 files copied, 10 files unchanged
Module 'accessibility' delivered successfully. 1 files copied, 5 files unchanged
Module 'cppcanvas' delivered successfully. 2 files copied, 15 files unchanged
Module 'embeddedobj' delivered successfully. 0 files copied, 5 files unchanged
Module 'helpcontent2' delivered successfully. 1 files copied, 12 files unchanged
Module 'padmin' delivered successfully. 0 files copied, 4 files unchanged
Module 'scaddins' delivered successfully. 2 files copied, 5 files unchanged
Module 'shell' delivered successfully. 4 files copied, 24 files unchanged
Module 'sj2' delivered successfully. 3 files copied, 3 files unchanged
Module 'basic' delivered successfully. 7 files copied, 45 files unchanged
Module 'sfx2' delivered successfully. 4 files copied, 119 files unchanged
Module 'avmedia' delivered successfully. 2 files copied, 9 files unchanged
Module 'linguistic' delivered successfully. 2 files copied, 11 files unchanged
Module 'svx' delivered successfully. 5 files copied, 637 files unchanged
Module 'dbaccess' delivered successfully. 8 files copied, 62 files unchanged
Module 'automation' delivered successfully. 8 files copied, 12 files unchanged
Module 'basctl' delivered successfully. 1 files copied, 17 files unchanged
Module 'chart2' delivered successfully. 4 files copied, 8 files unchanged
Module 'desktop' delivered successfully. 15 files copied, 85 files unchanged
Module 'extensions' delivered successfully. 12 files copied, 35 files unchanged
Module 'filter' delivered successfully. 9 files copied, 110 files unchanged
Module 'forms' delivered successfully. 1 files copied, 4 files unchanged
Module 'lingucomponent' delivered successfully. 8 files copied, 5 files unchanged
Module 'lotuswordpro' delivered successfully. 1 files copied, 1 files unchanged
Module 'reportdesign' delivered successfully. 3 files copied, 28 files unchanged
Module 'sc' delivered successfully. 4 files copied, 172 files unchanged
Module 'scripting' delivered successfully. 5 files copied, 13 files unchanged
Module 'sd' delivered successfully. 5 files copied, 173 files unchanged
Module 'slideshow' delivered successfully. 2 files copied, 4 files unchanged
Module 'starmath' delivered successfully. 2 files copied, 14 files unchanged
Module 'writerfilter' delivered successfully. 1 files copied, 5 files unchanged
Module 'writerperfect' delivered successfully. 3 files copied, 1 files unchanged
Module 'sw' delivered successfully. 3 files copied, 260 files unchanged
Module 'xmerge' delivered successfully. 0 files copied, 12 files unchanged
Module 'xmlsecurity' delivered successfully. 0 files copied, 7 files unchanged
checkdeliver.pl - checking delivered binaries
Module 'postprocess' delivered successfully. 0 files copied, 2 files unchanged
Module 'packimages' delivered successfully. 6 files copied, 2 files unchanged
145

Build succeeded ...!
touch stamp/build

... creating preregistered services.rdb ...

**************************************************
ERROR: ERROR: Could not register all components for file services.rdb (gid_Starr
egistry_Services_Rdb)!
in function: create_services_rdb
**************************************************

**************************************************
ERROR: Saved logfile: /home/janneke/vc/gub/target/mingw/build/openoffice-trunk/b
uild/ooo300-m9/instsetoo_native/util/OpenOffice//logging/en-US/log_OOO300_en-US.
log
**************************************************
... cleaning the output tree ...
... removing directory /home/janneke/vc/gub/target/mingw/build/openoffice-trunk/
build/ooo300-m9/instsetoo_native/util/OpenOffice//zip/en-US ...
... removing directory /home/janneke/vc/gub/target/mingw/build/openoffice-trunk/
build/ooo300-m9/instsetoo_native/util/OpenOffice//gid_Starregistry_Services_Rdb_
servicesrdb/en-US_witherror_1 ...
Thu Feb 19 14:30:56 2009 (01:23 min.)
Failed to install:  at ./ooinstall line 143.
make: *** [install] Error 1

And the logs say

    terminate called after throwing an instance of 'com::sun::star::registry::CannotRegisterImplementationException'
    terminate called after throwing an instance of 'com::sun::star::uno::RuntimeException'

Saved logs at:

    http://lilypond.org/~janneke/software/ooo/gub-mingw/

'''

class OpenOffice (target.AutoBuild):
    source = 'git://anongit.freedesktop.org/git/ooo-build/ooo-build&revision=207309ec6d428c6a6698db061efb670b36d5df5a'

    patches = ['openoffice-srcdir-build.patch']
    upstream_patches = [
        'openoffice-config_office-cross.patch',
        'openoffice-solenv-cross.patch',
        'openoffice-solenv.patch',
        'openoffice-sal-cross.patch',
        'openoffice-soltools-cross.patch',
        'openoffice-icc-cross.patch',
        'openoffice-i18npool-cross.patch',
        'openoffice-lingucomponent-mingw.patch',
        'openoffice-accessibility-nojava.patch',
        'openoffice-sw-disable-vba-consistency.patch'
        ]
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        # let's keep source tree around
        def tracking (self):
            return True
        self.source.is_tracking = misc.bind_method (tracking, self.source)
        if not out_of_gub_OOO_TOOLS_DIR:
            os.environ['OOO_TOOLS_DIR'] = self.settings.tools_prefix + '/bin'
    def _get_build_dependencies (self):
        return ['tools::autoconf', 'tools::rebase', 'tools::openoffice', 'boost-devel', 'curl-devel', 'cppunit-devel', 'db-devel', 'expat-devel', 'fontconfig-devel', 'hunspell-devel', 'libicu-devel', 'libjpeg-devel', 'libpng-devel', 'liblpsolve-devel', 'python-devel', 'redland-devel', 'saxon-java', 'xerces-c', 'zlib-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': [x.replace ('-devel', '')
                     for x in self._get_build_dependencies ()
                     if 'tools::' not in x and 'cross/' not in x]
                + ['cross/gcc-c++-runtime']
                }
    def get_subpackage_names (self):
        return ['']
    def stages (self):
        return misc.list_insert_before (target.AutoBuild.stages (self),
                                        'compile',
                                        ['dotslash_download', 'make_unpack', 'patch_upstream'])
    def dotslash_download (self):
        self.system ('mkdir -p %(downloads)s/openoffice-src')
        self.system ('cd %(builddir)s && ln %(downloads)s/openoffice-src/* src || :')
        self.system ('cd %(builddir)s && ./download')
        self.system ('cd %(builddir)s && ln src/* %(downloads)s/openoffice-src || :')
    @context.subst_method
    def bran (self):
        return 'ooo'
    @context.subst_method
    def ver (self):
        return '310'
    @context.subst_method
    def milestone (self):
        return 'm8'
    @context.subst_method
    def cvs_tag (self):
        return '%(bran)s%(ver)s-%(milestone)s'
    @context.subst_method
    def upstream_dir (self):
        return '%(builddir)s/build/%(cvs_tag)s'
    @context.subst_method
    def OOO_TOOLS_DIR (self):
        if 'OOO_TOOLS_DIR' not in os.environ:
            message = '''OOO_TOOLS_DIR not set
Set OOO_TOOLS_DIR to a recent pre-compiled native solver, I do

export OOO_TOOLS_DIR=/home/janneke/vc/ooo310-m8/build/ooo310-m8/solver/310/unxlngx6.pro/bin
'''
            printf (message)
            raise Exception (message)
        return os.environ['OOO_TOOLS_DIR']
    @context.subst_method
    def LD_LIBRARY_PATH (self):
        return '%(OOO_TOOLS_DIR)s/../lib' + misc.append_path (os.environ.get ('LD_LIBRARY_PATH', ''))
    def autoupdate (self):
        self.system ('cd %(srcdir)s && NOCONFIGURE=1 ./autogen.sh --noconfigure')
    def config_cache_overrides (self, str):
        return str + '''
ac_cv_file__usr_share_java_saxon9_jar=${ac_cv_file__usr_share_java_saxon9_jar=yes}
ac_cv_file__usr_share_java_saxon_jar=${ac_cv_file__usr_share_java_saxon_jar=yes}
ac_cv_db_version_minor=${ac_cv_db_version_minor=7}
ac_cv_icu_version_minor=${ac_cv_icu_version_minor=3.81}
'''
#    @context.subst_method
#    def ANT (self):
#        return 'ant'
    def configure_options (self):
        return misc.join_lines ('''
--with-vendor=\"GUB -- http://lilypond.org/gub\"
--disable-Xaw
--disable-access
--disable-activex
--disable-activex-component
--disable-atl
--disable-binfilter
--disable-build-mozilla
--disable-cairo
--disable-crypt-link
--disable-cups
--disable-dbus
--disable-directx
--disable-epm
--disable-evolution2
--disable-extensions
--disable-fontooo
--disable-gconf
--disable-gio
--disable-gnome-vfs
--disable-gstreamer
--disable-gtk
--disable-kde
--disable-kdeab
--disable-largefile
--disable-layout
--disable-ldap
--disable-ldap
--disable-libsn
--disable-lockdown
--disable-mathmldtd
--disable-mono
--disable-mozilla
--disable-neon
--disable-odk
--disable-opengl
--disable-pam
--disable-pasf
--disable-pch
--disable-qadevooo
--disable-randr
--disable-rpath
--disable-scsolver
--disable-systray
--disable-vba
--disable-xrender-link
--disable-atl

--enable-fontconfig
--enable-verbose

--without-gpc
--without-agg
--without-java
--without-myspell-dicts

--with-system-boost
--with-system-cairo
--with-system-curl
--with-system-db
--with-system-expat
--with-system-hunspell
--with-system-icu
--with-system-jpeg
--with-system-libxslt
--with-system-lpsolve
--with-system-neon
--with-system-odbc-headers
--with-system-portaudio
--with-system-redland
--with-system-sablot
--with-system-saxon
--with-system-sndfile
--with-system-xalan
--with-system-xerces
--with-system-xml-apis
--with-system-xrender-headers
--with-saxon-jar=%(system_prefix)s/share/java/saxon9.jar
--without-system-mozilla

--with-ant-home=/usr/share/ant
''')
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + self.configure_options ()
                + misc.join_lines ('''
--with-additional-sections=MinGW

--cache-file=%(builddir)s/config.cache

--with-tools-dir=%(OOO_TOOLS_DIR)s
'''))

# TODO:
# --with-system-libwpd
# --with-system-libwps
# --with-system-libwpg

    def make_unpack (self):
        # FIXME: python detection is utterly broken, should use python-config
        self.system ('cd %(builddir)s && make unpack')
        self.system ('cd %(builddir)s && make patch.apply')
    def apply_upstream_patch (self, name, strip_component=0):
        patch_strip_component = str (strip_component)
        self.system ('''
cd %(builddir)s/build/%(cvs_tag)s && patch -p%(patch_strip_component)s < %(patchdir)s/%(name)s
''', locals ())
    def upstream_patched_files (self):
        def files_in_patch (patch):
            string = file (self.expand ('%(patchdir)s/%(patch)s', locals ())).read ()
            def file_name (chunk):
                if chunk.find ('\n+++ ') >= 0:
                    return re.search ('\n[+]{3}\s+([.]/)?([^\s]+)', chunk).group (2)
                return ''
            return list (map (file_name, ('\n' + string).split ('\n---')[1:]))
        files_with_patches = list (map (files_in_patch, self.upstream_patches))
        return reduce (operator.__add__, files_with_patches)
    def upstream_patch_reset (self):
        upstream_dir = self.upstream_dir ()
        for f in self.upstream_patched_files ():
            self.system ('cp -p %(upstream_dir)s/%(f)s %(upstream_dir)s/%(f)s.patched' % locals ())
            self.system ('cp -p %(upstream_dir)s/%(f)s.pristine %(upstream_dir)s/%(f)s || cp -p %(upstream_dir)s/%(f)s %(upstream_dir)s/%(f)s.pristine' % locals ())
    def upstream_patched_unchanged_preserve_mtime (self):
        upstream_dir = self.upstream_dir ()
        for f in self.upstream_patched_files ():
            self.system ('cmp %(upstream_dir)s/%(f)s.patched %(upstream_dir)s/%(f)s && cp -p %(upstream_dir)s/%(f)s.patched %(upstream_dir)s/%(f)s || true' % locals ())
    def patch_upstream (self):
        # config_office is gone? but avoid rewriting everything for
        # now -- how's upstream?
        self.system ('cd %(upstream_dir)s && rm -f config_office && ln -s . config_office')
        self.upstream_patch_reset ()
        list (map (self.apply_upstream_patch, self.upstream_patches))
        self.upstream_patched_unchanged_preserve_mtime ()

        # configure blindly adds /usr includes, even when not necessary
        self.system ('sed -i -e "s@=/usr/include@=%(system_prefix)s/include@" %(upstream_dir)s/config_office/configure.in')

        # configure.in uses AC_CHECK_FILE, which simply assert-fails
        # when cross compiling slated for removal in ~2000
        # http://www.mail-archive.com/autoconf@gnu.org/msg02857.html
        self.system ('sed -i -e "s@AC_CHECK_FILE(@AC_CHECK_FILE_CROSS(@" %(upstream_dir)s/config_office/configure.in')

        # TODO: ASM is handled in individual solenv/inc/*mk
        self.system (misc.join_lines ('''sed -i.guborig
-e 's@\<ar\>@$(AR)@g'
-e 's@\<dlltool\>@$(DLLTOOL)@g'
-e 's@\<ld\>\([^-]\|$\)@$(LD)\\1@g'
-e 's@\<nm\>@$(NM)@g'
-e 's@\<ranlib\>@$(RANLIB)@g'
-e 's@\<windres\>@$(WINDRES)@g'
%(upstream_dir)s/solenv/inc/*mk'''))

        self.system ('chmod +x %(upstream_dir)s/solenv/bin/build.pl %(upstream_dir)s/solenv/bin/deliver.pl')

        have_wine = True
        disable_modules = [
            'bean', # com_sun_star_comp_beans_LocalOfficeWindow.c:39:18: error: jawt.h: No such file or directory
            'embedserv', # uses ATL http://article.gmane.org/gmane.comp.gnu.mingw.user/18483
            ]
        if not out_of_gub_OOO_TOOLS_DIR:
            disable_modules += ['testtools']
        # ~/.wine/system.reg
        # "PATH"=str(2):"C:/windows/system32;C:/windows;z:/home/janneke/vc/gub/target/mingw/build/openoffice-trunk/build/ooo300-m9/solver/300/bin/wntgcci.pro/bin;z:/home/janneke/vc/gub/target/mingw/root/usr/bin;z:/home/janneke/vc/gub/target/mingw/root/usr/lib;"
        wine_modules = [
            'testtools',
            'goodies',
            # Hmmm
            # wine   ../../../solver/300/wntgcci.pro/bin/regcomp.exe -register -r applicat.rdb -c i18npool.uno.dll
        ]

        for module in disable_modules:
            self.file_sub ([('(^[^#].*[ \t](all|n|w|w,vc[0-9])[ \t])', r'#\1')], '%(upstream_dir)s/%(module)s/prj/build.lst', env=locals ())

        module = 'setup_native'
        self.file_sub ([('^(pk.*customactions.*)', r'#\1')], '%(upstream_dir)s/%(module)s/prj/build.lst', env=locals ())

        # uses oledb.h from psdk 
        module = 'connectivity'
        self.file_sub ([(r'^([^#].*drivers.ado.*[ \t]w[ \t])', r'#\1')], '%(upstream_dir)s/%(module)s/prj/build.lst', env=locals ())

    def makeflags (self):
        return misc.join_lines ('''
NASM=nasm
CC_FOR_BUILD=cc
CXX_FOR_BUILD=c++
LDFLAGS_FOR_BUILD=
C_INCLUDE_PATH=
LIBRARY_PATH=
EXECPOST=
LD_LIBRARY_PATH=%(LD_LIBRARY_PATH)s
''')
##main configure barfs
##CPPFLAGS=
    def install (self):
        # build cppuhelper with debug -- try to squeeze more info out
        # of the failing regcomp than
        #    terminate called after throwing an instance of 'com::sun::star::registry::CannotRegisterImplementationException'
        #    terminate called after throwing an instance of 'com::sun::star::uno::RuntimeException'
        self.system ('''
cd %(upstream_dir)s/cppuhelper && rm -rf wntgcci.pro-
cd %(upstream_dir)s/cppuhelper && mv wntgcci.pro wntgcci.pro-
cd %(upstream_dir)s/cppuhelper && . ../*Env.Set.sh && perl $SOLARENV/bin/build.pl debug=true && perl $SOLARENV/bin/deliver.pl
''')
        regcomp_just_do_not_fail = True
        if regcomp_just_do_not_fail:
            # Well, that does not help.  Make non-failing regcomp wrapper...
            self.system ('cd %(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin && mv regcomp.exe regcomp-bin.exe')
            self.dump ('''#! /bin/sh
%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin/regcomp-bin.exe "$@"
exit 0
''',
                   '%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin/regcomp.exe',
                   permissions=octal.o755)
        target.AutoBuild.install (self)
        self.system ('rm -f %(install_prefix)s/bin/soffice3.1')
        if regcomp_just_do_not_fail:
            self.system ('cd %(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin && mv regcomp-bin.exe regcomp.exe')
            self.system ('cd "%(install_prefix)s/lib/ooo-3.1/OpenOffice.org 3" && /bin/tar -xzvf %(downloads)s/rdb/rdb.tar.gz || true')

class OpenOffice__mingw (OpenOffice):
    upstream_patches = OpenOffice.upstream_patches + [
        'openoffice-config_office-mingw.patch',
        'openoffice-solenv-mingw.patch',
        'openoffice-sal-mingw.patch',
        'openoffice-external-mingwheaders.patch',
        'openoffice-cppunit-mingw.patch',
        'openoffice-cppuhelper-mingw.patch',
        'openoffice-i18npool-mingw.patch',
        'openoffice-tools-mingw.patch',
        'openoffice-setup_native-mingw.patch',
        'openoffice-pyuno-mingw.patch',
        'openoffice-sysui-mingw.patch',
        'openoffice-dtrans-mingw.patch',
        'openoffice-fpicker-mingw.patch',
        'openoffice-sccomp-mingw.patch',
        'openoffice-vcl-mingw.patch',
        'openoffice-connectivity-mingw.patch',
        'openoffice-unotools-mingw.patch',
        'openoffice-goodies-mingw.patch',
        'openoffice-embeddedobj-mingw.patch',
        'openoffice-shell-mingw.patch',
        'openoffice-svx-mingw.patch',
        'openoffice-dbaccess-mingw.patch',
        'openoffice-desktop-mingw.patch',
        'openoffice-vbahelper-mingw.patch',
        'openoffice-scripting-mingw.patch',
        'openoffice-postprocess-mingw.patch',
        'openoffice-instsetoo_native-mingw.patch',
        'openoffice-solenv-mingw-installer.patch',
        'openoffice-scp2-mingw.patch',
        'openoffice-helpcontent2-mingw.patch', 
       ]
    # I do not understand external/mingwheaders.  It patches header
    # files and is thus strictly tied to a gcc version; that can never
    # build.  How can patching header files ever work, when not
    # patching the corresponding libraries?  Some patches remove
    # #ifdef checks that can be enabled by setting a #define.  Other
    # patches only affect OO.o client code already inside __MINGW32__
    # defines.  Why not fix OO.o makefiles and client code?
    upstream_patches += ['openoffice-sal-mingw-c.patch']
    # Kendy's MinGW patches are already applied
    kendy = [
        'openoffice-transex3-mingw.patch',
        'openoffice-soltools-mingw.patch'
        ]
    def _get_build_dependencies (self):
        return (OpenOffice._get_build_dependencies (self)
                + ['libunicows-devel', 'tools::pytt'])
    def patch (self):
        self.system ('cd %(srcdir)s && git clean -f')
        self.system ('cd %(srcdir)s && rm -f patches/dev300/layout-simple-dialogs-svx-no-gtk.diff')
        OpenOffice.patch (self)
        # disable Kendy's patch for Cygwin version of mingw
        self.file_sub ([('^(mingw-build-without-stlport-stlport.diff)', r'#\1'),
                        ('^(mingw-thread-wait-instead-of-sleep.diff)', r'#\1'),
                        ('^(redirect-extensions.diff)', r'#\1'),
                        ('^(slideshow-effect-rewind.diff)', r'#\1'),
                        ('^(layout-simple-dialogs-svx).diff', r'\1-no-gtk.diff')],
                       '%(srcdir)s/patches/dev300/apply')
        # setup wine hack -- TODO: CC_FOR_BUILD + SAL_DLL* for
        # cpputools/source/registercomponent/registercomponent.cxx
        wine_userdef = os.path.join (os.environ['HOME'], '.wine/user.reg')
        s = file (wine_userdef).read ()
#        if not self.expand ('%(upstream_dir)s/solver/%(ver)s') in s:
        if not 'CPLD_ACCESSPATH' in s:
            # Huh? > taking path: "file:///home/janneke/vc/gub/target/mingw/build/openoffice-anongit.freedesktop.org--git-ooo-build-ooo-build-/build/ooo310-m8/solver/310/wntgcci.pro/bin/canvasfactory.uno.dll" ...does not match given path "/home/janneke/vc/gub/target/mingw/build/openoffice-anongit.freedesktop.org--git-ooo-build-ooo-build-/build/ooo310-m8/solver/310/wntgcci.pro/bin/".
            # Even more strange: someone's eaten the space, but the directories
            # are the same!? > taking path: "file:///C:/ProgrammaBestanden/openoffice/usr/lib/ooo-3.1/OpenOffice.org/URE/bin/bootstrap.uno.dll" ...does not match given path "file:///C:/ProgrammaBestanden/openoffice/usr/lib/ooo-3.1/OpenOffice.org/URE/bin/".
            #(14:06:06) erAck: janneke: 'jsc' or 'sb' may know details. Not in irc though. I suggest dev@udk mailing list.
            self.dump ('''
[Environment]
"DISPLAY"="localhost:0.0"
"PATH"="%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin;%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/lib;%(system_prefix)s/bin;%(system_prefix)s/lib;Z:%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin;%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/lib;Z:%(system_prefix)s/bin;Z:%(system_prefix)s/lib;"
"CPLD_ACCESSPATH"="Z:%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin/;%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin/;.;C:/Programma Bestanden/openoffice/usr/lib/ooo-3.1/OpenOffice.org 3/Basis/program/;C:/Programma Bestanden/openoffice/usr/lib/ooo-3.1/OpenOffice.org 3/URE/bin;C:/Program Files/openoffice/usr/lib/ooo-3.1/OpenOffice.org 3/Basis/program/;C:/Program Files/openoffice/usr/lib/ooo-3.1/OpenOffice.org 3/URE/bin;%(install_prefix)s/bin/;%(install_prefix)s/lib/;%(system_prefix)s/bin/;%(system_prefix)s/lib/;Z:%(install_prefix)s/bin/;Z:%(install_prefix)s/lib/;Z:%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/bin/;Z:%(upstream_dir)s/solver/%(ver)s/wntgcci.pro/lib/;Z:%(system_prefix)s/lib/;Z:%(system_prefix)s/lib/"
''',
                   wine_userdef, mode='a')
        # fixup gen_makefile disaster -- TODO: CC_FOR_BUILD
        if out_of_gub_OOO_TOOLS_DIR:
            self.system ('''cp -pvf $OOO_TOOLS_DIR/../../../../sal/unx*/bin/gen_makefile $OOO_TOOLS_DIR/gen_makefile''')
            self.system ('''cp -pvf $OOO_TOOLS_DIR/../../../../icc/unx*/bin/create_sRGB_profile $OOO_TOOLS_DIR/create_sRGB_profile''')
            self.system ('''cp -pvf $OOO_TOOLS_DIR/../../../../i18npool/unx*/bin/* $OOO_TOOLS_DIR''')
    def configure_command (self):
        return (OpenOffice.configure_command (self)
                .replace ('--with-system-xrender-headers', '')
                + ' --disable-xrender-link'
                + ' --with-distro=Win32')
    def patch_upstream (self):
        self.system ('chmod -R ugo+w %(upstream_dir)s/dtrans %(upstream_dir)s/fpicker %(upstream_dir)s/dbaccess')
        OpenOffice.patch_upstream (self)
        # avoid juggling of names for windows-nt
        self.system ('sed -i -e "s@WINNT@WNT@" %(upstream_dir)s/config_office/configure.in')
        self.file_sub ([
                ('( [.](type|size))', r'//\1'),
                ('( [.]note.*)', ''),
                ('(,@.*)', '')],
                       '%(upstream_dir)s/bridges/source/cpp_uno/mingw_intel/call.s')

        self.system ('chmod +x %(upstream_dir)s/solenv/bin/addsym-mingw.sh')
        
        self.system ('cp -f %(upstream_dir)s/sal/osl/w32/MAKEFILE.MK %(upstream_dir)s/sal/osl/w32/makefile.mk')

        self.dump ('''\
#! /bin/sh
set -e
in=$(eval echo '$'$#)
dir=$(dirname $in)
/usr/bin/wrc "$@"
if test "$dir" != "." -a -e $(basename $in .rc).res; then
    mv $(basename $in .rc).res $dir
fi
''',
             '%(upstream_dir)s/solenv/bin/wrc',
                   permissions=octal.o755)
        self.system ('mkdir -p %(upstream_dir)s/solver/%(ver)s/wntgcci.pro/inc')
        self.system ('cp -pv %(sourcefiledir)s/mingw-headers/*.h %(upstream_dir)s/solver/%(ver)s/wntgcci.pro/inc')


# Attempt at building a `tiny fraction' of openoffice for essential
# native binary build tools, aiming to remove out_of_gub_OOO_TOOLS_DIR

# The dependencies for some OO.o build tools are rather crude, the
# whole module (eg: shell, svtools) the tool is built in may depend on
# toolkit/vcl, but tool itself (eg: langconvex.EXE, HelpLinker) really
# doesn't?  I may hope...

# Build tools provided by OpenOffice__tools

# MODULE       --> BINARY TOOL:   TOOL's MODULE[, DEPENDENCIES]
# */pyuno      --> regcomp:       cpputools
# *            --> gen_makefile:  sal
# sccomp       --> rsc:           rsc
# sfx2         --> svidl:         idl
# udkapi       --> idlc:          idlc, registry
# udkapi       --> regmerge:      cpputools
# officecfg    --> cfgex:         transex3
# scp2         --> ulfconv:       setup_native
# i18npool     --> gendict:       i18npool

# Build tools not yet provided by OpenOffice__tools [expensive]

# MODULE       --> BINARY TOOL:   TOOL's MODULE[, DEPENDENCIES]
# regcomp --windows: a cross unix regcomp that registers .DLLs
# shell        --> lngconvex.EXE: shell (but: huh, windows only?), VCL
# helpcontent2 --> HelpLinker:    svtools, VCL

module_deps = {
    'cpputools' : ['salhelper', 'cppuhelper', 'cppu'],
    'salhelper' : ['sal'],
    'cppuhelper' : ['codemaker', 'cppu', 'offuh'],
    'codemaker' : ['udkapi'],
    'offuh' : ['offapi'],
    'generic_build' : ['dmake', 'solenv'],
    'udkapi' : ['idlc'],
    'idlc' : ['registry'],
    'sal' : ['xml2cmp'],
    'registry' : ['store'],
    'xml2cmp' : ['soltools', 'stlport'],
    'tools' : ['vos', 'basegfx', 'comphelper', 'i18npool'],
    'transex3' : ['tools'],
    'i18npool' : ['bridges', 'sax', 'stoc', 'comphelper', 'i18nutil', 'regexp'],
    'basegfx' : ['o3tl', 'sal', 'offuh', 'cppuhelper', 'cppu'],
    'comphelper' : ['cppuhelper', 'ucbhelper', 'offuh', 'vos', 'salhelper'],
    'stoc' : ['rdbmaker', 'cppuhelper', 'cppu',
              #'jvmaccess',
              'sal', 'salhelper'],
    'icc' : ['solenv'],
    'pyuno': ['stoc', 'cpputools', 'cppuhelper', 'bridges', 'tools'],
    'rsc': ['tools'],
    'setup_native': ['soltools', 'xml2cmp', 'sal', 'officecfg', 'unoil'],
    'unoil': ['offapi', 'ridljar', 'solenv', 'cli_ure'],

    # This is getting ridiculous, we need a graphical toolkit, almost
    # all of office for getting at a HelpLinker tool?
    'xmlhelp': ['ucbhelper', 'unoil', 'svtools', 'unotools',
                #'javaunohelper'
                ],
    'svtools': ['vcl'], # try minimal...
    'unotools': ['comphelper', 'cppuhelper', 'offuh', 'tools', 'ucbhelper'],
    'vcl': ['psprint', 'rsc', 'sot', 'ucbhelper', 'unotools', 'i18npool', 'i18nutil', 'unoil', 'ridljar', 'offuh', 'basegfx', 'tools', 'transex3', 'icc'],
    'idl': ['tools'],
    }

def ooo_deps (deps):
    lst = deps[:]
    for d in deps:
        lst += ooo_deps (module_deps.get (d, []))
    return lst

class OpenOffice__tools (tools.AutoBuild, OpenOffice):
    source = 'svn://svn@svn.services.openoffice.org/&module=ooo&branch=tags/OOO310_m8&depth=files'
    patches = [
        'openoffice-o3tl-no-cppunit.patch',
        'openoffice-basegfx-no-cppunit.patch',
        'openoffice-store-core.patch',
        'openoffice-store-registry.patch',
        'openoffice-funit-char-line.patch',
#        'openoffice-svtools-minimal.patch',
        ]
    generic_build = ['dmake', 'solenv', 'pyuno']
    regcomp = 'cpputools'
    gen_makefile = 'sal'
    svidl = 'idl'
    ulfconv = 'setup_native'
    gendict = 'i18npool'
    tool_modules = ['icc', regcomp, gen_makefile, 'transex3', 'rsc', ulfconv, 'idl', gendict]
    toplevel_modules = generic_build + tool_modules
    modules = misc.uniq (ooo_deps (toplevel_modules))
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        # Let's keep source tree around
        def tracking (self):
            return True
        self.source.is_tracking = misc.bind_method (tracking, self.source)
        self.source.dir = self.settings.downloads + '/openoffice-tools'
        if not os.path.isdir (self.source.dir):
            os.system ('mkdir -p ' + self.source.dir)
    def _get_build_dependencies (self):
        return ['boost', 'db', 'expat', 'libicu', 'libxslt', 'python', 'zlib']
    def stages (self):
        return tools.AutoBuild.stages (self)
    def autoupdate (self):
        tools.AutoBuild.autoupdate (self)
    def module_repo (self, module):
        repo = repository.get_repository_proxy (self.settings.downloads + '/openoffice-tools',
                                                OpenOffice__tools.source.replace ('depth=files', 'branchmodule=' + module))
        def tracking (self):
            return True
        repo.is_tracking = misc.bind_method (tracking, repo)
        return repo
    def download_module (self, module):
        self.module_repo (module).download ()
    def download (self):
        tools.AutoBuild.download (self)
        list (map (self.download_module, self.modules))
    def untar_module (self, module):
        def defer (logger):
            self.module_repo (module).update_workdir (self.expand ('%(srcdir)s/' + module))
        self.func (defer)
    def untar (self):
        tools.AutoBuild.untar (self)
        list (map (self.untar_module, self.modules))
    @context.subst_method
    def ver (self):
        return '310'
    def patch (self):
        OpenOffice.patch (self)
        # Make a handy fake toplevel GUB module to build everything.
        self.system ('''mkdir -p %(srcdir)s/gub/prj''')
        tool_modules_str = ' '.join (self.tool_modules)
        toplevel_modules_str = ' '.join (self.toplevel_modules)
        self.dump ('''gub	gub	:	%(toplevel_modules_str)s NULL''', '%(srcdir)s/gub/prj/build.lst', env=locals ())
        self.dump ('''
.PHONY: all install
DESTDIR=
prefix=@prefix@
bin=solver/%(ver)s/unxlngx*.pro/bin
lib=solver/%(ver)s/unxlngx*.pro/lib
out=unxlngx*.pro
tool_modules = %(tool_modules_str)s

all:
	. ./*Env.Set.sh && ./bootstrap && (cd gub && ../solenv/bin/build.pl --all)
install:
	$(foreach m,$(tool_modules),cp -pv $(m)/$(out)/bin/* $(bin) &&) true
	install -d $(DESTDIR)$(prefix)
	rm -rf $(bin)/ure $(bin)/install $(bin)/uninstall
	cp -prv $(bin) $(DESTDIR)$(prefix)
	cp -prv $(lib) $(DESTDIR)$(prefix)
''', '%(srcdir)s/Makefile.in', env=locals ())
    def configure_command (self):
        return ('x_libraries=no_x_libraries x_includes=no_x_includes '
                + tools.AutoBuild.configure_command (self)
                + re.sub ('--with-system-[^ ]*', '', OpenOffice.configure_options (self))
                .replace ('--disable-crypt-link', '--enable-crypt-link')
                + ' --with-system-db '
                + ' --with-system-expat '
                + ' --with-system-icu '
                + ' --with-system-libxml '
                + ' --with-system-python '
                + ' --with-system-zlib '
                + ' --with-x=no')
    def configure (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s', soft=True)
        tools.AutoBuild.configure (self)
        # OO.o's configure script manages to ignore CFLAGS/LDFLAGS but
        # will happily add -L/usr/lib nonsense.
        def add_CFLAGS_LDFLAGS_already (logger, file):
            loggedos.file_sub (logger, [
                    ('-L(NONE|no_x_libraries|/usr/lib)', self.expand ('-L%(system_prefix)s/lib')),
                    ('-I(NONE|no_x_includes|/usr/include)', self.expand ('-I%(system_prefix)s/include')),
                    ('(LD_LIBRARY_PATH=.*)', self.expand (r'\1:%(system_prefix)s/lib'))
                    ], file)
        self.map_locate (add_CFLAGS_LDFLAGS_already, '%(builddir)s', '*Env.Set.sh')
    def wrap_executables (self):
        # using rpath, and also openoffice has data files in bin/,
        # such as types.rdb.
        pass

Openoffice = OpenOffice
Openoffice__mingw = OpenOffice__mingw
Openoffice__tools = OpenOffice__tools
