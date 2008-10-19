from gub import misc
from gub import targetbuild

class Openoffice (targetbuild.TargetBuild):
#    source = 'svn://svn.gnome.org/svn/ooo-build&branch=trunk&revision=14327'
    source = 'svn://svn.gnome.org/svn/ooo-build&branch=trunk'
    patches = ['openoffice-srcdir-build.patch']
    patches = ['openoffice-srcdir-build.patch']
    def get_build_dependencies (self):
        return ['boost-devel', 'curl', 'db-devel', 'expat', 'fontconfig-devel', 'libjpeg-devel', 'libpng-devel', 'python', 'saxon-java', 'xerces-c', 'zlib-devel']
    def stages (self):
        return misc.list_insert_before (targetbuild.TargetBuild.stages (self),
                                        'compile',
                                        ['dot_download'])
    def dot_download (self):
        self.system ('mkdir -p %(downloads)s/openoffice-src')
        self.system ('cd %(builddir)s && ln %(downloads)s/openoffice-src/* src || :')
        self.system ('cd %(builddir)s && ./download')
        self.system ('cd %(builddir)s && ln src/* %(downloads)s/openoffice-src || :')
    def autoupdate (self):
        # Why is build.py:Build:patch() not doing this?
        map (self.apply_patch, self.__class__.patches)
        self.system ('cd %(srcdir)s && NOCONFIGURE=1 ./autogen.sh --noconfigure')
    def config_cache_overrides (self, str):
        return str + '''
ac_cv_file__usr_share_java_saxon9_jar=${ac_cv_file__usr_share_java_saxon9_jar=yes}
ac_cv_file__usr_share_java_saxon_jar=${ac_cv_file__usr_share_java_saxon_jar=yes}
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

    def configure (self):
        targetbuild.TargetBuild.configure (self)
        # FIXME: python detection is utterly broken, should use python-config
        self.system ('cd %(builddir)s && make unpack')
        self.dump ('''
        ## ------------------------------------- ##
## Checking for the existence of files.  ##
## ------------------------------------- ##

# AC_CHECK_FILE_CROSS(FILE, [ACTION-IF-FOUND], [ACTION-IF-NOT-FOUND])
# -------------------------------------------------------------
#
# Check for the existence of FILE; remove assertion on not cross-compiliing
AC_DEFUN([AC_CHECK_FILE_CROSS],
[
AS_VAR_PUSHDEF([ac_File], [ac_cv_file_$1])dnl
AC_CACHE_CHECK([for $1], [ac_File],
if test -r "$1"; then
  AS_VAR_SET([ac_File], [yes])
else
  AS_VAR_SET([ac_File], [no])
fi)
AS_IF([test AS_VAR_GET([ac_File]) = yes], [$2], [$3])[]dnl
AS_VAR_POPDEF([ac_File])dnl
])# AC_CHECK_FILE_CROSS
''', '%(builddir)s/build/ooo300-m9/config_office/acinclude.m4', mode='a')

        # FIXME: neutralize silly GNU make check
        self.system ('sed -i -e "s@ 3[.]81@gpuhleez, we are not even building mozilla@" %(builddir)s/build/*/config_office/configure.in')
        self.system ('sed -i -e s@PYTHON_CFLAGS=.*@PYTHON_CFLAGS="-I%(system_prefix)s/include/python2.4@" %(builddir)s/build/*/config_office/configure.in')
        # FIXME: db configure blindly adds /usr includes, even when not necessary
        self.system ('sed -i -e "s@=/usr/include@=%(system_prefix)s/include@" %(builddir)s/build/*/config_office/configure.in')
        # FIXME: db configure uses TRY_RUN without alternative
        self.system ('sed -i -e "s@for v in 1 2 3 4 5 6[^;]*;@DB_VERSION_MINOR=7; for v in;@" %(builddir)s/build/*/config_office/configure.in')
        self.system ('sed -i -e "s@AC_CHECK_FILE(@AC_CHECK_FILE_CROSS(@" %(builddir)s/build/*/config_office/configure.in')

class Openoffice__mingw (Openoffice):
    def configure_command (self):
        return (Openoffice.configure_command (self)
                + ' --with-distro=Win32')
