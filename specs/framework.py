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
		
	def patch (self):
		if self.settings.platform.startswith ('mingw'):
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/python-2.4.2-1.patch
''')

	def configure (self):
		if self.settings.platform.startswith ('mingw'):
			self.system ('''cd %(srcdir)s && autoconf''')
			self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
			self.settings.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_root)s/usr/include' % self.package_dict ()
		gub.Target_package.configure (self)

	def install_command (self):
		return gub.Target_package.install_command (self) \
		       + gub.join_lines ('''
INCLUDEDIR=%(install_prefix)s/include
MANDIR=%(install_prefix)s/share/man
''')

class Gmp (gub.Target_package):
	def xxconfigure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force --copy''')
		self.system ('''cd %(srcdir)s && ./missing --run aclocal''')
		self.system ('''cd %(srcdir)s && ./missing --run autoconf''')
		self.system ('''cd %(srcdir)s && ./missing --run automake''')
		self.file_sub ('ac_cv_c_bigendian=unknown',
			       'ac_cv_c_bigendian=${ac_cv_c_bigendian-unknown}',
			       '%(srcdir)s/configure')
		self.file_sub ("-Wl,-e,'\$dll_entry'", '',
			       '%(srcdir)s/configure')

		os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)
		gub.Target_package.configure (self)

	def xpatch (self):
		if self.settings.platform.startswith ('mingw'):
	                ## FIXME, seems we don't need this?
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/gmp-4.1.4-1.patch
''')

	def install (self):
		gub.Target_package.install (self)
		if self.settings.platform.startswith ('mingw'):
			# minimal libtool fixups
			self.system ('''
mkdir -p %(install_prefix)s/bin
mv %(install_prefix)s/lib/lib*.dll %(install_prefix)s/bin/
cp %(builddir)s/.libs/libgmp.dll.a %(install_prefix)s/lib/
''')

class Guile (gub.Target_package):
	def xpatch (self):
		if self.settings.platform.startswith ('mingw'):
	                ## FIXME
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/guile-1.7.2-3.patch
''')

	def configure_command (self):
		cmd = ''
		if self.settings.platform.startswith ('mingw'):
			# watch out for whitespace
			builddir = self.builddir ()
			srcdir = self.srcdir ()
			if 0: # using patch
				cmd = gub.join_lines ('''\
AS=%(target_architecture)s-as
PATH_SEPARATOR=";"
CC_FOR_BUILD="cc -I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
''')
		cmd += gub.Target_package.configure_command (self) \
		      + gub.join_lines ('''
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
''')
		return cmd

	def config_cache_overrides (self, str):
		if self.settings.platform.startswith ('mingw'):
			str += '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_root)s/usr/lib"}
'''
		return str

	def configure (self):
		if 0: # using patch
			gub.Target_package.autoupdate (self)
			self.file_sub ('''^#(LIBOBJS=".*fileblocks.*)''', '\\1',
				       '%(srcdir)s/configure')
			os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)
		if self.settings.platform.startswith ('mingw'):
			self.settings.target_gcc_flags = '-mms-bitfields'
		gub.Target_package.configure (self)
		if self.settings.platform.startswith ('mingw'):
			self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/libtool')
			self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/guile-readline/libtool')
			self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/libtool''')
			self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/guile-readline/libtool''')

	def xxcompile (self):
		if self.settings.platform.startswith ('mingw'):
			self.settings.target_gcc_flags = '-mms-bitfields'
		gub.Target_package.compile (self)

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


class LilyPond (gub.Target_package):
	def configure (self):
		self.autoupdate ()
		gub.Target_package.configure (self)

	def configure_command (self):
		## FIXME: pickup $target-guile-config
		cmd = 'PATH=%(system_root)s/usr/bin:$PATH '

		cmd += gub.Target_package.configure_command (self)
		cmd += ' --disable-documentation'
		if self.settings.platform.startswith ('mingw'):
			cmd += gub.join_lines ('''
--without-kpathsea
--enable-relocation
--with-python-include=%(system_root)s/usr/include/python2.4
--disable-optimising
''')
		return cmd

	def configure (self):
		# FIXME: should add to CPPFLAGS...
		self.settings.target_gcc_flags += ' -I%(builddir)s' \
						  % self.package_dict ()
		gub.Package.system (self, '''
mkdir -p %(builddir)s
cp /usr/include/FlexLexer.h %(builddir)s
''')
		gub.Target_package.configure (self)
		if self.settings.platform.startswith ('mingw'):
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
		cmd = gub.Target_package.compile_command (self)
		if self.settings.platform.startswith ('mingw'):
			python_lib = "%(system_root)s/usr/bin/libpython2.4.dll"
			return cmd + gub.join_lines ('''
LDFLAGS=%(python_lib)s
HELP2MAN_GROFFS=
'''% locals ())

	def compile (self):
		gub.Target_package.compile (self)
		if self.settings.platform.startswith ('mingw'):
			gub.Package.system (self, '''
mkdir -p %(builddir)s/mf/out-console
cp -pv %(builddir)s/mf/out/* mf/out-console
''')
			cmd = gub.Target_pacykage.compile_command (self)
			cmd += ' conf=console'
			self.system ('''cd %(builddir)s && %(cmd)s''',
				     locals ())

	def install_command (self):
		return gub.Target_package.install_command (self) \
		       + gub.join_lines ('''
HELP2MAN_GROFFS=
'''% locals ())
	
	def install (self):
		gub.Target_package.install (self)
		if self.settings.platform.startswith ('mingw'):
			self.system ('''
install -m755 %(builddir)/lily/out/lilypond %(install_prefix)/bin/lilypond-windows
install -m755 %(builddir)/lily/out-console/lilypond %(install_prefix)/bin/lilypond
''')

class Gettext (gub.Target_package):
	def config_cache_overrides (self, str):
		if self.settings.platform == 'mingw':
			str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		if 0:
			# this for mingw-3.7 only, but mingw-3.8 does not link
			# guile.exe
			str += '''
# gettext does not include winsock2.h -- do not feel like patching right now
# but in mingw only if winsock2.h
ac_cv_func_select=${ac_cv_func_select=no}
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
'''
		return str

	def configure_command (self):
		cmd = gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'

		if self.settings.platform == 'mac':
			cmd = re.sub ('--config-cache ', '', cmd)
		return cmd

	def configure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force --copy''')
		gub.Target_package.configure (self)

class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def config_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
	

class Darwin_glib (Glib):
	def configure (self):
		Glib.configure (self)
		self.file_sub ('nmedit', '%(target_architecture)s-nmedit',
			       self.builddir () + '/libtool')
	def file_name (self):
		if self.url:
			return re.sub ('.*/([^/]+)', '\\1', self.url)
		else:
			return 'glib'


class Pango (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + gub.join_lines ('''
--without-x
--without-cairo
''')

	def xxconfigure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force --copy''')
#woe!
#libtool: link: CURRENT `1001' is not a nonnegative integer
#libtool: link: `1001:0:1001' is not valid version information
		gub.Target_package.configure (self)
		if self.settings.platform.startswith ('mingw'):
			self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/libtool''')
			for i in ['%(builddir)s/Makefile' \
				  % self.package_dict ()] \
			    + glob.glob ('%(builddir)s/*/Makefile' \
					 % self.package_dict ()) \
			    + glob.glob ('%(builddir)s/*/*/Makefile' \
					 % self.package_dict ()):
				self.file_sub ('^LIBTOOL *=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX', i)

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
		gub.Package.system (self, '''
cd %(srcdir)s && ./configure --disable-static --enable-shared
''')
		gub.Package.install (self)


class Fontconfig (gub.Target_package):
	def configure_command (self):
		# FIXME: system dir vs packaging install
		cmd = gub.Target_package.configure_command (self) \
		      + gub.join_lines ('''
--with-freetype-config="/usr/bin/freetype-config
--prefix=%(system_root)s/usr
--exec-prefix=%(system_root)s/usr
"''')

		if self.settings.platform.startswith ('mingw'):
			 cmd += gub.join_lines ('''
--with-default-fonts=@WINDIR@\\fonts\\
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts
''')

		return cmd

	def configure (self):
##		self.autoupdate ()
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env = {'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(install_prefix)s \
--exec-prefix=%(install_prefix)s \
'''})
		gub.Target_package.configure (self)
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

# latest vanilla packages
#Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
#Expat (settings).with (version='1.95.8', mirror=download.sf),
#Gettext (settings).with (version='0.14.5'),
#Guile (settings).with (version='1.7.2', mirror=download.alpha, format='gz'),

def get_packages (settings, platform):
	packages = {
	'mac': (
		Gettext (settings).with (version='0.10.40'),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
		Expat (settings).with (version='1.95.8', mirror=download.sourceforge, format='gz'),
		Darwin_glib (settings).with (version='2.8.4', mirror=download.gtk),
		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
	),
	'mingw': (
		Libtool (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2'),
		Libiconv (settings).with (version='1.9.2'),
		Freetype (settings).with (version='2.1.7', mirror=download.freetype),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
		Gmp (settings).with (version='4.1.4'),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Pango (settings).with (version='1.10.1', mirror=download.gtk),
		Python (settings).with (version='2.4.2', mirror=download.python, format='bz2'),
		LilyPond (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	}

	if platform == 'linux':
		return filter (lambda x: x.name () != 'libiconv', packages['mingw'])
	
	return packages[platform]
