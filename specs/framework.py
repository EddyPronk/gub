import copy
import glob
import os
import re

## gub specific.
from driver import Settings
import gub
import download
import installer
import cvs


# FIXME: cannot put in cross.py, that's imported in gub before Cross_package
# is defined
class Binutils (gub.Cross_package):
	pass

class Gcc (gub.Cross_package):
	def patch (self):
		self.file_sub ([('/usr/bin/libtool', '%(tooldir)s/bin/%(target_architecture)s-libtool')],
			       '%(srcdir)s/gcc/config/darwin.h')

	def configure_command (self):
		cmd = gub.Cross_package.configure_command (self)
		# FIXME: using --prefix=%(tooldir)s makes this
		# uninstallable as a normal system package in
		# /usr/i686-mingw/
		# Probably --prefix=/usr is fine too
		cmd += '''
--prefix=%(tooldir)s
--program-prefix=%(target_architecture)s-
--with-as=%(tooldir)s/bin/%(target_architecture)s-as
--with-ld=%(tooldir)s/bin/%(target_architecture)s-ld
--enable-static
--enable-shared
--enable-libstdcxx-debug
--enable-languages=c,c++ ''' % self.settings.__dict__

		return gub.join_lines (cmd)

	def install (self):
		gub.Cross_package.install (self)
		self.system ('''
cd %(tooldir)s/lib && ln -fs libgcc_s.1.so libgcc_s.so
''')

class Libtool (gub.Target_package):
	pass

class Libtool__mingw (Libtool):
	def xstrip (self):
		self.strip_bin ()

class Python (gub.Target_package):
	def set_download (self, mirror, format='gz', downloader=None):
		gub.Target_package.set_download (self, mirror, format, downloader)
		self.url = re.sub ('python-', 'Python-' , self.url)

	def python_version (self):
		return '.'.join (self.version.split ('.')[0:])

	def package_dict (self, env = {}):
		dict = gub.Target_package.package_dict (self, env)
		dict['python_version'] = self.python_version ()
		return dict
	
	def untar (self):
		gub.Target_package.untar (self)
		Srcdir = re.sub ('python', 'Python', self.srcdir ())
		self.system ('mv %(Srcdir)s %(srcdir)s', locals ())

class Python__mingw (Python):
	def __init__ (self, settings):
		Python.__init__ (self, copy.deepcopy (settings))
		self.settings.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_root)s/usr/include' % self.settings.__dict__

	def python_version (self):
		#URG
		return '2.4'

	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < %(lilywinbuilddir)s/patch/python-2.4.2-1.patch
''')

	def configure (self):
		self.system ('''cd %(srcdir)s && autoconf''')
		self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
		gub.Target_package.configure (self)

	def install (self):
		Python.install (self)
		for i in glob.glob ('%(install_root)s/usr/lib/python%(python_version)s/lib-dynload/*.so*' \
				    % self.package_dict ()):
			dll = re.sub ('\.so*', '.dll', i)
			self.system ('mv %(i)s %(dll)s', locals ())
		self.system ('''
cp %(install_root)s/usr/lib/python%(python_version)s/lib-dynload/* %(install_root)s/usr/bin
''')
		self.system ('''
chmod 755 %(install_root)s/usr/bin/*
''')


class Gmp (gub.Target_package):
	pass

class Gmp__darwin (Gmp):
	def patch (self):

		## GCC 4.0.2 cross barfs on this,
		## don't know why.
		self.file_sub ([('__GMP_DECLSPEC_XX std::[oi]stream& operator[<>][^;]+;$',
				 '')],
			       self.srcdir () + '/gmp-h.in')
		Gmp.patch (self)

class Gmp__mingw (Gmp):
	def install (self):
		gub.Target_package.install (self)
		self.system ('''
mkdir -p %(install_prefix)s/bin
mv %(install_prefix)s/lib/lib*.dll %(install_prefix)s/bin/
cp %(builddir)s/.libs/libgmp.dll.a %(install_prefix)s/lib/
''')

	def xstrip (self):
		self.strip_bin ()

class Guile (gub.Target_package):

	## Ugh. C&P.
	def guile_version (self):
		return '.'.join (self.version.split ('.')[0:])
	
	def configure_command (self):
		return (gub.Target_package.configure_command (self) 
			+ gub.join_lines ('''
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
'''))

	def install (self):
		gub.Target_package.install (self)
		version = self.read_pipe ('''\
GUILE_LOAD_PATH=%(install_prefix)s/share/guile/* %(install_prefix)s/bin/guile-config --version 2>&1\
''').split ()[-1]
		self.dump ('''\
#!/bin/sh
[ "$1" == "--version" ] && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
#[ "$1" == "compile" ] && echo "-I $%(system_root)s/usr/include"
#[ "$1" == "link" ] && echo "-L%(system_root)s/usr/lib -lguile -lgmp"
prefix=$(dirname $(dirname $0))
[ "$1" == "compile" ] && echo "-I$prefix/include"
[ "$1" == "link" ] && echo "-L$prefix/lib -lguile -lgmp"
exit 0
''',
			   '%(install_prefix)s/bin/%(target_architecture)s-guile-config')
		os.chmod ('%(install_prefix)s/bin/%(target_architecture)s-guile-config' % self.package_dict (), 0755)

class Guile__mingw (Guile):
	def __init__ (self, settings):
		Guile.__init__ (self, copy.deepcopy (settings))
		self.settings.target_gcc_flags = '-mms-bitfields'

	def xpatch (self):
		## FIXME
		self.system ('''
cd %(srcdir)s && patch -p1 < %(lilywinbuilddir)s/patch/guile-1.7.2-3.patch
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
			self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''',
					 '\\1')],
				       '%(srcdir)s/configure')
			os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)
		gub.Target_package.configure (self)
		self.file_sub ([('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1')],
			       '%(builddir)s/libtool')
		self.file_sub ([('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1')],
			       '%(builddir)s/guile-readline/libtool')
		self.system ('''cp %(lilywinbuilddir)s/bin/%(system_toolprefix)slibtool %(builddir)s/libtool''')
		self.system ('''cp %(lilywinbuilddir)s/bin/%(system_toolprefix)slibtool %(builddir)s/guile-readline/libtool''')

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

	def gubinstall_root (self):
		return '%(gubinstall_root)s/usr'

class LilyPond__mingw (LilyPond):
	def __init__ (self, settings):
		LilyPond.__init__ (self, copy.deepcopy (settings))
		# FIXME: should add to CPPFLAGS...
		self.settings.target_gcc_flags = '-mms-bitfields'

		#UGH
		builddir = self.builddir ()
		self.settings.target_gcc_flags += ' -I%(builddir)s' \
						  % locals ()

        def patch (self):
		# FIXME: for our gcc-3.4.5 cross compiler in the mingw
		# environment, THIS is a magic word.
		self.file_sub ([('THIS', 'SELF')],
			       '%(srcdir)s/lily/parser.yy')

        def configure_command (self):
		return LilyPond.configure_command (self) \
		       + gub.join_lines ('''
--without-kpathsea
--enable-relocation
--with-python-include=%(system_root)s/usr/include/python%(python_version)s
--disable-optimising
''')

	def configure (self):
		gub.Package.system (self, '''
mkdir -p %(builddir)s
cp /usr/include/FlexLexer.h %(builddir)s
''')
		gub.Target_package.configure (self)
		self.config_cache ()
		cmd = self.configure_command () \
		      + ' --enable-config=console'
		self.system ('''cd %(builddir)s && %(cmd)s''',
			     locals ())

	def compile_command (self):
		python_lib = "%(system_root)s/usr/bin/libpython%(python_version)s.dll"
		return LilyPond.compile_command (self) \
		       + gub.join_lines ('''
LDFLAGS=%(python_lib)s
HELP2MAN_GROFFS=
'''% locals ())

	def compile (self):
		LilyPond.compile (self)
		gub.Package.system (self, '''
mkdir -p %(builddir)s/mf/out-console
cp -pv %(builddir)s/mf/out/* %(builddir)s/mf/out-console
''')
		cmd = LilyPond__mingw.compile_command (self)
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
install -m755 %(builddir)s/lily/out/lilypond %(install_prefix)s/bin/lilypond-windows
install -m755 %(builddir)s/lily/out-console/lilypond %(install_prefix)s/bin/lilypond
cp %(install_root)s/usr/lib/lilypond/*/python/* %(install_root)s/usr/bin
cp %(install_root)s/usr/share/lilypond/*/python/* %(install_root)s/usr/bin
''')
		for i in glob.glob ('%(install_root)s/usr/bin/*' \
				    % self.package_dict ()):
			s = self.read_pipe ('file %(i)s' % locals ())
			if s.find ('guile') >= 0:
				self.system ('mv %(i)s %(i)s.scm', locals ())
			elif  s.find ('python') >= 0:
				self.system ('mv %(i)s %(i)s.py', locals ())

class LilyPond__linux (LilyPond):
	def configure_command (self):
		return LilyPond.configure_command (self) \
		       + ' --enable-static-gxx'
	def compile_command (self):
		# FIXME: when not x-building, help2man runs guile without
		# setting the proper LD_LIBRARY_PATH.
		return 'export LD_LIBRARY_PATH=%(system_root)s/usr/lib:$LD_LIBRARY_PATH;' \
		       + LilyPond.compile_command (self)

	def install_gub (self):
		gub.Target_package.install_gub (self)
		self.system ('''
cd %(gubinstall_root)s/usr/bin && mv lilypond lilypond-bin
''')
		framework_root = gub.Package.gubinstall_root (self)
		self.dump ('''
#! /bin/sh
# Do not use Python, as python itself might need a relocation wrapper
GUILE_LOAD_PATH=%(framework_root)s/share/guile/*:$GUILE_LOAD_PATH \
GS_FONTPATH=%(framework_root)s/share/ghostscript/8.15/fonts:$GS_FONTPATH \
GS_LIB=%(framework_root)s/share/ghostscript/8.15/lib:$GS_LIB \
GS_FONTPATH=%(framework_root)s/share/gs/fonts:$GS_FONTPATH \
GS_LIB=%(framework_root)s/share/gs/lib:$GS_LIB \
PANGO_RC_FILE=${PANGO_RC_FILE-%(framework_root)s/usr/etc/pango/pangorc} \
PYTHONPATH=%(framework_root)s/../python:$PYTHONPATH \
PYTHONPATH=%(framework_root)s/lib/python%(python_version)s:$PYTHONPATH \
%(gubinstall_root)s/usr/bin/lilypond-bin "$@"
'''
,
		'%(gubinstall_root)s/usr/bin/lilypond',
		env=locals ())
		os.chmod ('%(gubinstall_root)s/usr/bin/lilypond' \
			 % self.package_dict (), 0755)

class LilyPond__darwin (LilyPond):
	def configure_command (self):
		cmd = LilyPond.configure_command (self)

		framedir = '%(system_root)s/System/Library/Frameworks/Python.framework/Versions/%(python_version)s'
		cmd += ' --with-python-include=' + framedir + '/include/python%(python_version)s'
		return cmd

	def configure (self):
		LilyPond.configure (self)
		self.file_sub ([('CONFIG_CXXFLAGS = ',
				 'CONFIG_CXXFLAGS = -DGUILE_ELLIPSIS=...')],
			       self.builddir ()+ '/config.make')

	def compile_command (self):
		return LilyPond.compile_command (self) \
		       + gub.join_lines (''' HELP2MAN_GROFFS=''')

class Gettext (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'

class Gettext__mingw (Gettext):
	# using gcc-3.4.5
	def xx__init__ (self, settings):
		Gettext.__init__ (self, copy.deepcopy (settings))
		# gettext-0.14.1-1 does not compile with gcc-4.0.2
		self.settings.tool_prefix = self.settings.system_toolprefix

	def mingw_org_untar (self):
		Gettext.untar (self)
		broken_untar_dir = re.sub ('-200.*', '',
					   '%(srcdir)s' % self.package_dict ())

		self.system ('''
mv %(broken_untar_dir)s %(srcdir)s
''', locals ())

	def xxpatch (self):
		Gettext.autoupdate (self)

	def config_cache_overrides (self, str):
		return re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
			       str) \
			       + '''
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
'''

	def xxconfigure_command (self):
		return Gettext.configure_command (self) \
		       + ' --disable-glocale'


class Gettext__darwin (Gettext):
	def configure_command (self):
		return re.sub (' --config-cache', '',
			       Gettext.configure_command (self))

class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def config_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

class Glib__darwin (Glib):
	def configure (self):
		Glib.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')

class Pango (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + gub.join_lines ('''
--without-x
--without-cairo
''')

class Pango__mingw (Pango):
	def install (self):
		gub.Target_package.install (self)
		self.system ('mkdir -p %(install_root)s/usr/etc/pango')
		self.dump ('''[Pango]
ModulesPath = "@INSTDIR@\\usr\\lib\\pango\\1.4.0\\modules"
ModuleFiles = "@INSTDIR@\\usr\\etc\\pango\\pango.modules"
#[PangoX]
#AliasFiles = "@INSTDIR@\\usr\\etc\\pango\\pango.modules\\pangox.aliases"
''',
			   '%(install_root)s/usr/etc/pango/pangorc.in')

		# pango.modules can be generated if we have the linux
		# installer built

# cd target/linux/installer/usr/lib/lilypond/noel/root
# PANGO_RC_FILE=$(pwd)/etc/pango/pangorc bin/pango-querymodules > etc/pango/pango.modules
		self.system ('cp %(nsisdir)s/pango.modules.in %(install_root)s/usr/etc/pango/pango.modules.in')

class Pango__linux (Pango):
	def untar (self):
		Pango.untar (self)
		# FIXME: --without-cairo switch is removed in 1.10.1,
		# pango only compiles without cairo if cairo is not
		# installed linkably on the build system.  UGH.
		self.file_sub ([('(have_cairo[_a-z0-9]*)=true', '\\1=false'),
				('(cairo[_a-z0-9]*)=yes', '\\1=no')],
			       '%(srcdir)s/configure')
		os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)

class Pango__darwin (Pango):
	def configure (self):
		Pango.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')


class Freetype (gub.Target_package):
	def configure (self):
#		self.autoupdate (autodir=os.path.join (self.srcdir (),
#						       'builds/unix'))

		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		gub.Target_package.configure (self)

		self.file_sub ([('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX')], '%(builddir)s/Makefile')

		self.dump ('''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''',
			   '%(builddir)s/Makefile',
			   mode='a')

	def install (self):
		gub.Package.system (self, gub.join_lines ('''
cd %(srcdir)s && ./configure
--disable-static
--enable-shared
--prefix=/usr
--sysconfdir=/usr/etc
--includedir=/usr/include
--libdir=/usr/lib
'''))
		gub.Package.install (self)

class Freetype__mingw (Freetype):
	def xstrip (self):
		self.strip_bin ()

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
			self.dump ('''
#define sleep(x) _sleep (x)
''',
				   '%(builddir)s/config.h',
				   mode='a')
		# help fontconfig cross compiling a bit, all CC/LD
		# flags are wrong, set to the target's root

		cflags = '-I%(srcdir)s -I%(srcdir)s/src ' \
			 + self.read_pipe ('freetype-config --cflags')[:-1]
		libs = self.read_pipe ('freetype-config --libs')[:-1]
		for i in ('fc-case', 'fc-lang', 'fc-glyphname'):
			self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES=
''', locals ())

		self.file_sub ([('DOCSRC *=.*', 'DOCSRC=')],
			       '%(builddir)s/Makefile')

class Fontconfig__mingw (Fontconfig):
	def configure_command (self):
		return Fontconfig.configure_command (self) \
		       + gub.join_lines ('''
--with-default-fonts=@WINDIR@\\fonts\\
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts
''')

class Fontconfig__darwin (Fontconfig):
	def configure (self):
		Fontconfig.configure (self)
		self.file_sub ([('-Wl,[^ ]+ ', '')],
			       '%(builddir)s/src/Makefile')

class Fondu (gub.Target_package):
	def install (self):
		self.system ("cp %(srcdir)s/showfond %(srcdir)s/fondu %(install_prefix)s/bin/")

	def set_download (self, mirror,
			  format='tgz', downloader=None):
		gub.Target_package.set_download (self, mirror, format, downloader)
		self.url = re.sub ("fondu-", "fondu_src-" , self.url)
		self.url = re.sub ("tar.gz", "tgz" , self.url)

	def configure (self):
		self.system ("mkdir -p %(builddir)s && cp %(srcdir)s/Makefile.Mac %(builddir)s")
		gub.Target_package.configure (self)

		self.file_sub ([('CC = cc', 'CC = %(target_architecture)s-gcc\nVPATH=%(srcdir)s\n'),
				('CORE = .*', '')],
			       '%(builddir)s/Makefile')

	def basename (self):
		## ugr.
		return 'fondu'

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
		return gub.Target_package.broken_install_command (self) \
		       + self.makeflags ()

class Expat__mingw (Expat):
	def xstrip (self):
		self.strip_bin ()

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
def get_packages (settings):
	packages = {
	'darwin': (
#		Gettext__darwin (settings).with (version='0.10.40'),
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2'),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
#		Expat (settings).with (version='1.95.8', mirror=download.sourceforge, format='gz'),
		Glib__darwin (settings).with (version='2.8.4', mirror=download.gtk),
		Fontconfig__darwin (settings).with (version='2.3.2', mirror=download.fontconfig),
		Pango__darwin (settings).with (version='1.10.1', mirror=download.gtk),
#		Fondu (settings).with (version="051010", mirror=download.sourceforge_homepage, format='gz')
		Gmp__darwin (settings).with (version='4.1.4'),

		## 1.7.3  is actually CVS repackaged.
#		Guile (settings).with (version='1.7.3', mirror=download.gnu, format='gz'),
		Guile (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
		LilyPond__darwin (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	'mingw': (
		Libtool__mingw (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
#		Gettext__mingw (settings).with (version='0.11.5-2003.02.01-1-src', mirror=download.mingw, format='bz2'),
#		Gettext__mingw (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2'),
		Gettext__mingw (settings).with (version='0.14.5-1', mirror=download.lp, format='bz2'),
#		Gettext__mingw (settings).with (version='0.14.5'),
#		Gettext__mingw (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
		Libiconv (settings).with (version='1.9.2'),
		Freetype__mingw (settings).with (version='2.1.7', mirror=download.freetype),
		Expat__mingw (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig__mingw (settings).with (version='2.3.2', mirror=download.fontconfig),
		Gmp__mingw (settings).with (version='4.1.4'),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile__mingw (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Pango__mingw (settings).with (version='1.10.1', mirror=download.gtk),
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


	packs = packages[settings.platform]
	
	## FIXME: changes settings.
	try:
		settings.python_version = [p for p in packs if isinstance (p, Python)][0].python_version ()
	except IndexError:
		# UGH darwin has no python package.
		settings.python_version = '2.3'
	
	settings.guile_version = [p for p in packs if isinstance (p, Guile)][0].guile_version ()

	return packs

def get_installers (settings):
	installers = {
		'darwin' : [installer.Bundle (settings)],
		'linux' : [
		installer.Tgz (settings),
		installer.Deb (settings),
		installer.Rpm (settings),
		installer.Autopackage (settings),
		],
		'mingw' : [installer.Nsis (settings)],
		}
	
	return installers[settings.platform]

