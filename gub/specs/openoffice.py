import operator
import os
import re
#
from gub import context
from gub import misc
from gub import targetbuild

'''
7 matches for "delivered successfully" in buffer: *shell*
   4642:Module 'solenv' delivered successfully. 0 files copied, 1 files unchanged
   4655:Module 'stlport' delivered successfully. 0 files copied, 8 files unchanged
   4995:Module 'soltools' delivered successfully. 7 files copied, 7 files unchanged
   5069:Module 'external' delivered successfully. 3 files copied, 27 files unchanged
   6288:Module 'libwpd' delivered successfully. 12 files copied, 0 files unchanged
   6397:Module 'xml2cmp' delivered successfully. 3 files copied, 2 files unchanged
   Module 'sal' delivered successfully. 109 files copied, 1 files unchanged
Module 'vos' delivered successfully. 30 files copied, 1 files unchanged
'''

class Openoffice (targetbuild.TargetBuild):
#    source = 'svn://gsvn.gnome.org/svn/ooo-build&branch=trunk&revision=14327'
    source = 'svn://svn.gnome.org/svn/ooo-build&branch=trunk'
    patches = ['openoffice-srcdir-build.patch']
#    upstream_patches = ['openoffice-config_office-cross.patch', 'openoffice-config_office-gnu-make.patch', 'openoffice-config_office-mingw.patch', 'openoffice-solenv-cross.patch', 'openoffice-solenv.patch', 'openoffice-sal-cross.patch', 'openoffice-soltools-cross.patch', 'openoffice-soltools-mingw.patch', 'openoffice-sal-mingw.patch', 'openoffice-external-mingwheaders.patch']
    upstream_patches = ['openoffice-config_office-cross.patch', 'openoffice-config_office-gnu-make.patch', 'openoffice-solenv-cross.patch', 'openoffice-solenv.patch', 'openoffice-sal-cross.patch', 'openoffice-soltools-cross.patch']
    def get_build_dependencies (self):
        # redland-devel
        return ['boost-devel', 'curl', 'cppunit-devel', 'db-devel', 'expat-devel', 'fontconfig-devel', 'libjpeg-devel', 'libpng-devel', 'python', 'saxon-java', 'xerces-c', 'zlib-devel']
    def stages (self):
        return misc.list_insert_before (targetbuild.TargetBuild.stages (self),
                                        'compile',
                                        ['dot_download', 'make_unpack', 'patch_upstream'])
    def dot_download (self):
        self.system ('mkdir -p %(downloads)s/openoffice-src')
        self.system ('cd %(builddir)s && ln %(downloads)s/openoffice-src/* src || :')
        self.system ('cd %(builddir)s && ./download')
        self.system ('cd %(builddir)s && ln src/* %(downloads)s/openoffice-src || :')
    @context.subst_method
    def cvs_tag (self):
        return 'ooo300-m9'
    @context.subst_method
    def upstream_dir (self):
        return '%(builddir)s/build/%(cvs_tag)s'
    @context.subst_method
    def OOO_TOOLS_DIR (self):
        # TODO: either make all ooo-tools (soltools: makedepend..., transex3: transex3 ...)
        # self-hosting or compile them as Openoffice__tools package...
        # Shortcut: use precompiled tools from user's system
        return os.environ['OOO_TOOLS_DIR']
    def autoupdate (self):
        # Why is build.py:Build:patch() not doing this?
        map (self.apply_patch, self.__class__.patches)
        self.system ('cd %(srcdir)s && NOCONFIGURE=1 ./autogen.sh --noconfigure')
    def config_cache_overrides (self, str):
        return str + '''
ac_cv_file__usr_share_java_saxon9_jar=${ac_cv_file__usr_share_java_saxon9_jar=yes}
ac_cv_file__usr_share_java_saxon_jar=${ac_cv_file__usr_share_java_saxon_jar=yes}
ac_cv_db_version_minor=${ac_cv_db_version_minor=7}
ac_cv_icu_version_minor=${ac_cv_icu_version_minor=3.81}
'''
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + misc.join_lines ('''
--with-vendor=\"GUB -- LilyPond.org\"
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
--with-system-icu
--with-system-jpeg
--with-system-libxslt
--with-system-neon
--with-system-odbc-headers
--with-system-portaudio
--with-system-sablot
--with-system-saxon
--with-system-sndfile
--with-system-xalan
--with-system-xerces
--with-system-xml-apis
--with-system-xrender-headers
--with-saxon-jar=%(system_prefix)s/share/java/saxon9.jar
--without-system-mozilla

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
            return map (file_name, ('\n' + string).split ('\n---')[1:])
        files_with_patches = map (files_in_patch, self.upstream_patches)
        return reduce (operator.__add__, files_with_patches)
    def upstream_patch_reset (self):
        upstream_dir = self.upstream_dir ()
        for f in self.upstream_patched_files ():
            self.system ('cp -p %(upstream_dir)s/%(f)s.pristine %(upstream_dir)s/%(f)s || cp -p %(upstream_dir)s/%(f)s %(upstream_dir)s/%(f)s.pristine' % locals ())
    def patch_upstream (self):
        self.upstream_patch_reset ()
        map (self.apply_upstream_patch, self.__class__.upstream_patches)

        # FIXME: neutralize silly GNU make check
        # self.system ('''sed -i -e "s@' 3[.]81'@'gpuhleez, we are not even building mozilla'@" %(upstream_dir)s/config_office/configure.in')

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

        self.system ('sed -i -e "s@[ \t]all@ i@g" %(upstream_dir)s/redland/prj/build.lst')

        # java go away
        self.system ('sed -i -e "s@[ \t]all@ i@g" %(upstream_dir)s/sandbox/prj/build.lst')


        # OO.o's included cppunit has build problems, but there's no --with-system-cppunit
        # self.system ('sed -i -e "s@[ \t]\(all\|n\)[ \t]@ i @g" %(upstream_dir)s/cppunit/prj/build.lst')

    def makeflags (self):
        return misc.join_lines ('''
CC_FOR_BUILD=cc
CXX_FOR_BUILD=c++
LDFLAGS_FOR_BUILD=
C_INCLUDE_PATH=
LIBRARY_PATH=
EXECPOST=
SOLAR_JAVA=TRUE
''')
##main configure barfs
##CPPFLAGS=
                
class Openoffice__mingw (Openoffice):
    Openoffice.upstream_patches += ['openoffice-config_office-mingw.patch', 'openoffice-soltools-mingw.patch', 'openoffice-sal-mingw.patch', 'openoffice-external-mingwheaders.patch']
    # external/mingwheaders seems a badly misguided effort.  It
    # patches header files and is thus strictly tied to a gcc version;
    # that can never build.  How can patching header files ever work,
    # when not patching the corresponding libraries?  Some patches
    # remove #ifdef checks that can be enabled by setting a #define.
    # Other patches only affect OO.o client code already inside
    # __MINGW32__ defines.  Why not fix OO.o makefiles and client
    # code?
    Openoffice.upstream_patches += ['openoffice-sal-mingw-c.patch']
    def get_build_dependencies (self):
        return Openoffice.get_build_dependencies (self) + ['libunicows-devel']
    def configure_command (self):
        return (Openoffice.configure_command (self)
                .replace ('--with-system-xrender-headers', '')
                + ' --disable-xrender-link'
                + ' --with-distro=Win32')
    def patch_upstream (self):
        Openoffice.patch_upstream (self)
        # avoid juggling of names for windows-nt
        self.system ('sed -i -e "s@WINNT@WNT@" %(upstream_dir)s/config_office/configure.in')

        self.system ('chmod +x %(upstream_dir)s/solenv/bin/addsym-mingw.sh')
        
        self.system ('cp -f %(upstream_dir)s/sal/osl/w32/MAKEFILE.MK %(upstream_dir)s/sal/osl/w32/makefile.mk')

        self.dump ('''\
#! /bin/sh
set -e
in=$(eval echo '$'$#)
dir=$(dirname $in)
/usr/bin/wrc "$@"
if test "$dir" != "."; then
    mv $(basename $in .rc).res $dir
fi
''',
             '%(upstream_dir)s/solenv/bin/wrc',
                   permissions=0755)

        self.system ('cp -pv %(sourcefiledir)s/sehandler.h %(upstream_dir)s/solver/300/wntgcci.pro/inc')
