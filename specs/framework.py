import cvs
import download
import glob
import gub
import os
import re

class Libtool (gub.Target_package):
	pass

class Python (gub.Target_package):
	def set_download (self, mirror, format='gz', downloader=None):
		gub.Target_package.set_download (self, mirror, format, downloader)
		self.url = re.sub ("python-", "Python-" , self.url)

class Python__mingw (Python):
	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/python-2.4.2-1.patch
''')

	def configure (self):
		self.system ('''cd %(srcdir)s && autoconf''')
		self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
		self.settings.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_root)s/usr/include' % self.package_dict ()
		gub.Target_package.configure (self)

class Gmp (gub.Target_package):
	pass

class Gmp__mingw (Gmp):
	def install (self):
		gub.Target_package.install (self)
		self.system ('''
mkdir -p %(install_prefix)s/bin
mv %(install_prefix)s/lib/lib*.dll %(install_prefix)s/bin/
cp %(builddir)s/.libs/libgmp.dll.a %(install_prefix)s/lib/
''')

class Guile (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		      + gub.join_lines ('''
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
''')

	def install (self):
		gub.Target_package.install (self)
		version = self.read_pipe ('''\
GUILE_LOAD_PATH=%(install_prefix)s/share/guile/* %(install_prefix)s/bin/guile-config --version 2>&1\
''').split ()[-1]
		self.dump ('%(install_prefix)s/bin/%(target_architecture)s-guile-config', '''\
#!/bin/sh
[ "$1" == "--version" ] && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
#[ "$1" == "compile" ] && echo "-I $%(system_root)s/usr/include"
#[ "$1" == "link" ] && echo "-L%(system_root)s/usr/lib -lguile -lgmp"
prefix=$(dirname $(dirname $0))
[ "$1" == "compile" ] && echo "-I$prefix/include"
[ "$1" == "link" ] && echo "-L$prefix/lib -lguile -lgmp"
exit 0
''')
		os.chmod ('%(install_prefix)s/bin/%(target_architecture)s-guile-config' % self.package_dict (), 0755)

class Guile__mingw (Guile):
	def xpatch (self):
		## FIXME
		self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/guile-1.7.2-3.patch
''')

	def configure_command (self):
		# watch out for whitespace
		builddir = self.builddir ()
		srcdir = self.srcdir ()
		return Guile.configure_command (self) \
		       + gub.join_lines ('''\
AS=%(target_architecture)s-as
PATH_SEPARATOR=";"
CC_FOR_BUILD="cc -I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
''')

	def config_cache_overrides (self, str):
		return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_root)s/usr/lib"}
'''

	def configure (self):
		if 0: # using patch
			gub.Target_package.autoupdate (self)
			self.file_sub ('''^#(LIBOBJS=".*fileblocks.*)''', '\\1',
				       '%(srcdir)s/configure')
			os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)
		self.settings.target_gcc_flags = '-mms-bitfields'
		gub.Target_package.configure (self)
		self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/libtool')
		self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/guile-readline/libtool')
		self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/libtool''')
		self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/guile-readline/libtool''')

class Guile__linux (Guile):
	def compile_command (self):
		# FIXME: when not x-building, guile runs guile without
		# setting the proper LD_LIBRARY_PATH.
		return 'export LD_LIBRARY_PATH=%(builddir)s/libguile/.libs:$LD_LIBRARY_PATH;' \
		       + Guile.compile_command (self)

class LilyPond (gub.Target_package):
	def configure (self):
		self.autoupdate ()
		gub.Target_package.configure (self)

	def configure_command (self):
		## FIXME: pickup $target-guile-config
		cmd = 'PATH=%(system_root)s/usr/bin:$PATH '

		cmd += gub.Target_package.configure_command (self)
		cmd += ' --disable-documentation'
		return cmd

class LilyPond__mingw (LilyPond):
	def configure_command (self):
		return LilyPond.configure_command (self) \
		       + gub.join_lines ('''
--without-kpathsea
--enable-relocation
--with-python-include=%(system_root)s/usr/include/python2.4
--disable-optimising
''')
	def configure (self):
		# FIXME: should add to CPPFLAGS...
		self.settings.target_gcc_flags += ' -I%(builddir)s' \
						  % self.package_dict ()
		gub.Package.system (self, '''
mkdir -p %(builddir)s
cp /usr/include/FlexLexer.h %(builddir)s
''')
		gub.Target_package.configure (self)
		self.config_cache ()
		self.settings.target_gcc_flags = '-mms-bitfields'
		# FIXME: should add to CPPFLAGS...
		self.settings.target_gcc_flags += ' -I%(builddir)s' \
						  % self.package_dict ()
		cmd = self.configure_command () \
		      + ' --enable-config=console'
		self.system ('''cd %(builddir)s && %(cmd)s''',
			     locals ())

	def compile_command (self):
		python_lib = "%(system_root)s/usr/bin/libpython2.4.dll"
		return LilyPond.compile_command (self) \
		       + gub.join_lines ('''
LDFLAGS=%(python_lib)s
HELP2MAN_GROFFS=
'''% locals ())

	def compile (self):
		LilyPond.compile (self)
		gub.Package.system (self, '''
mkdir -p %(builddir)s/mf/out-console
cp -pv %(builddir)s/mf/out/* mf/out-console
''')
		cmd = LilyPond.compile_command (self)
		cmd += ' conf=console'
		self.system ('''cd %(builddir)s && %(cmd)s''',
			     locals ())

	def install_command (self):
		return LilyPond.install_command (self) \
		       + gub.join_lines ('''
HELP2MAN_GROFFS=
'''% locals ())

	def install (self):
		LilyPond.install (self)
		self.system ('''
install -m755 %(builddir)/lily/out/lilypond %(install_prefix)/bin/lilypond-windows
install -m755 %(builddir)/lily/out-console/lilypond %(install_prefix)/bin/lilypond
''')

class LilyPond__linux (LilyPond):
	def configure_command (self):
		return LilyPond.configure_command (self) \
		       + ' --enable-static-gxx'

class Gettext (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'

	def configure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force --copy''')
		gub.Target_package.configure (self)

class Gettext__mingw (Gettext):
	def config_cache_overrides (self, str):
		return re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
			       str)

class Gettext__mac (Gettext):
	def configure_command (self):
		return re.sub ('--config-cache ', '',
			       Gettext.configure_command (self))

class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def config_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

class Glib__mac (Glib):
	def configure (self):
		Glib.configure (self)
		self.file_sub ('nmedit', '%(target_architecture)s-nmedit',
			       self.builddir () + '/libtool')

class Pango (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + gub.join_lines ('''
--without-x
--without-cairo
''')

class Pango__linux (Pango):
	def untar (self):
		Pango.untar (self)
		# FIXME: --without-cairo switch is removed in 1.10.1,
		# pango only compiles without cairo if cairo is not
		# installed linkably on the build system.  UGH.
		self.file_sub ('(have_cairo[_a-z0-9]*)=true',
			       '\\1=false',
			       '%(srcdir)s/configure')
		self.file_sub ('(cairo[_a-z0-9]*)=yes',
			       '\\1=no',
			       '%(srcdir)s/configure')
		os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)

class Freetype (gub.Target_package):
	def configure (self):
#		self.autoupdate (autodir=os.path.join (self.srcdir (),
#						       'builds/unix'))

		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		gub.Target_package.configure (self)

		self.file_sub ('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX', '%(builddir)s/Makefile')

		self.dump ('%(builddir)s/Makefile', '''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''', mode='a')

	def install (self):
		gub.Package.system (self, gub.join_lines ('''
cd %(srcdir)s && ./configure
--disable-static
--enable-shared
--prefix=/usr
--sysconfdir=/etc
--includedir=/usr/include
--libdir=/usr/lib
'''))
		gub.Package.install (self)


class Fontconfig (gub.Target_package):
	def configure_command (self):
		# FIXME: system dir vs packaging install
		return gub.Target_package.configure_command (self) \
		      + gub.join_lines ('''
--with-freetype-config="/usr/bin/freetype-config
--prefix=%(system_root)s/usr
--exec-prefix=%(system_root)s/usr
"''')

	def configure (self):
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env = {'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(install_prefix)s \
--exec-prefix=%(install_prefix)s \
'''})
		gub.Target_package.configure (self)
		# FIXME: how to put in __mingw class without duplicating
		# configure ()
		if self.settings.platform.startswith ('mingw'):
			self.dump ('%(builddir)s/config.h', '''
#define sleep(x) _sleep (x)
''', mode='a')
		# help fontconfig cross compiling a bit, all CC/LD
		# flags are wrong, set to the target's root

		cflags = '-I%(srcdir)s -I%(srcdir)s/src ' \
			 + self.read_pipe ('freetype-config --cflags')[:-1]
		libs = self.read_pipe ('freetype-config --libs')[:-1]
		for i in ('fc-case', 'fc-lang', 'fc-glyphname'):
			self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES=
''', locals ())

class Fontconfig__mingw (Fontconfig):
	def configure_command (self):
		return Fontconfig.configure_command (self) \
		       + gub.join_lines ('''
--with-default-fonts=@WINDIR@\\fonts\\
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts
''')


class Expat (gub.Target_package):
	def makeflags (self):
		return gub.join_lines ('''
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H"
EXEEXT=
RUN_FC_CACHE_TEST=false
''')
	def compile_command (self):
		return gub.Target_package.compile_command (self) \
		       + self.makeflags ()
	def install_command (self):
		return gub.Target_package.install_command (self) \
		       + self.makeflags ()

class Zlib (gub.Target_package):
	def configure (self):
		zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.2'
		if self.settings.platform.startswith ('mingw'):
			zlib_is_broken = 'target=mingw'
		self.system ('''
sed -i~ 's/mgwz/libz/' %(srcdir)s/configure
shtool mkshadow %(srcdir)s %(builddir)s
cd %(builddir)s && %(zlib_is_broken)s AR="%(AR)s r" %(srcdir)s/configure --shared
''', locals ())

	def install_command (self):
		return gub.Target_package.broken_install_command (self)

# latest vanilla packages
#Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
#Expat (settings).with (version='1.95.8', mirror=download.sf),
#Gettext (settings).with (version='0.14.5'),
#Guile (settings).with (version='1.7.2', mirror=download.alpha, format='gz'),

# FIXME: these lists should be merged, somehow,
# linux and mingw use almost the same list (linux does not have libiconv),
# but some classes have __mingw or __linux overrides.
def get_packages (settings, platform):
	packages = {
	'mac': (
		Gettext__mac (settings).with (version='0.10.40'),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
		Expat (settings).with (version='1.95.8', mirror=download.sourceforge, format='gz'),
		Glib__mac (settings).with (version='2.8.4', mirror=download.gtk),
		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
	),
	'mingw': (
		Libtool (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
		Gettext__mingw (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2'),
		Libiconv (settings).with (version='1.9.2'),
		Freetype (settings).with (version='2.1.7', mirror=download.freetype),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig__mingw (settings).with (version='2.3.2', mirror=download.fontconfig),
		Gmp__mingw (settings).with (version='4.1.4'),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile__mingw (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Pango (settings).with (version='1.10.1', mirror=download.gtk),
		Python__mingw (settings).with (version='2.4.2', mirror=download.python, format='bz2'),
		LilyPond__mingw (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	'linux': (
		Libtool (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2'),
		Freetype (settings).with (version='2.1.7', mirror=download.freetype),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
		Gmp (settings).with (version='4.1.4'),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile__linux (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Pango__linux (settings).with (version='1.10.1', mirror=download.gtk),
		Python (settings).with (version='2.4.2', mirror=download.python, format='bz2'),
		LilyPond__linux (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	}

	return packages[platform]
