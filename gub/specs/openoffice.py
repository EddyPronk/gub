from gub import context
from gub import misc
from gub import targetbuild

class Openoffice (targetbuild.TargetBuild):
#    source = 'svn://gsvn.gnome.org/svn/ooo-build&branch=trunk&revision=14327'
    source = 'svn://svn.gnome.org/svn/ooo-build&branch=trunk'
    patches = ['openoffice-srcdir-build.patch']
    upstream_patches = ['openoffice-config_office-cross.patch', 'openoffice-config_office-gnu-make.patch', 'openoffice-config_office-mingw.patch']
#    upstream_patches = ['openoffice-config_office-cross.patch', 'openoffice-config_office-mingw.patch']
    def get_build_dependencies (self):
        return ['boost-devel', 'curl', 'db-devel', 'expat', 'fontconfig-devel', 'libjpeg-devel', 'libpng-devel', 'python', 'saxon-java', 'xerces-c', 'zlib-devel']
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

'''))
    def make_unpack (self):
        # FIXME: python detection is utterly broken, should use python-config
        self.system ('cd %(builddir)s && make unpack')
        self.system ('cd %(builddir)s && make patch.apply')
    def apply_upstream_patch (self, name, strip_component=0):
        patch_strip_component = str (strip_component)
        self.system ('''
cd %(builddir)s/build/%(cvs_tag)s && patch -p%(patch_strip_component)s < %(patchdir)s/%(name)s
''', locals ())
    def patch_upstream (self):
        self.system ('cp -p %(builddir)s/build/%(cvs_tag)s/config_office/acinclude.m4.pristine %(builddir)s/build/%(cvs_tag)s/config_office/acinclude.m4 || cp -p %(builddir)s/build/%(cvs_tag)s/config_office/acinclude.m4 %(builddir)s/build/%(cvs_tag)s/config_office/acinclude.m4.pristine ')
        self.system ('cp -p %(builddir)s/build/%(cvs_tag)s/config_office/configure.in.pristine %(builddir)s/build/%(cvs_tag)s/config_office/configure.in || cp -p %(builddir)s/build/%(cvs_tag)s/config_office/configure.in %(builddir)s/build/%(cvs_tag)s/config_office/configure.in.pristine')
        map (self.apply_upstream_patch, self.__class__.upstream_patches)
        # FIXME: neutralize silly GNU make check
        # self.system ('''sed -i -e "s@' 3[.]81'@'gpuhleez, we are not even building mozilla'@" %(builddir)s/build/%(cvs_tag)s/config_office/configure.in')
        # configure blindly adds /usr includes, even when not necessary
        self.system ('sed -i -e "s@=/usr/include@=%(system_prefix)s/include@" %(builddir)s/build/%(cvs_tag)s/config_office/configure.in')
        # configure.in uses AC_CHECK_FILE, which simply assert-fails
        # when cross compiling slated for removal in ~2000
        # http://www.mail-archive.com/autoconf@gnu.org/msg02857.html
        self.system ('sed -i -e "s@AC_CHECK_FILE(@AC_CHECK_FILE_CROSS(@" %(builddir)s/build/%(cvs_tag)s/config_office/configure.in')

class Openoffice__mingw (Openoffice):
    def configure_command (self):
        return (Openoffice.configure_command (self)
                .replace ('--with-system-xrender-headers', '')
                + ' --disable-xrender-link'
                + ' --with-distro=Win32')
