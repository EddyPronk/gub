import copy
import glob
import os
import re

## gub specific.
from settings import Settings
import gub
import download
import installer
import cvs


def file_is_newer (f1, f2):
	return (not os.path.exists (f2)
		or os.stat (f1).st_mtime >  os.stat (f2).st_mtime)


class Darwin_sdk (gub.Sdk_package):
	def patch (self):
		pat = self.srcdir() + '/usr/lib/*.la'
		for a in glob.glob (pat):
			self.file_sub ([(r' (/usr/lib/.*\.la)', r'%(system_root)s\1')], a)


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

class Python (gub.Target_package):
	def set_download (self, mirror, format='gz', downloader=None):
		gub.Target_package.set_download (self, mirror, format, downloader)
		self.url = re.sub ('python-', 'Python-' , self.url)

	def python_version (self):
		return '.'.join (self.ball_version.split ('.')[0:2])

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

	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-1.patch
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

		## powerpc/darwin cross barfs on all C++ includes from
		## a C linkage file.
		## don't know why. Let's patch C++ completely from GMP.
		
		self.file_sub ([('__GMP_DECLSPEC_XX std::[oi]stream& operator[<>][^;]+;$', ''),
				('#include <iosfwd>', ''),
				('<cstddef>','<stddef.h>')
				],
			       self.srcdir () + '/gmp-h.in')
		Gmp.patch (self)

class Gmp__mingw (Gmp):
	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gmp-4.1.4-1.patch
''')

	def configure (self):
		Gmp.configure (self)
		self.system ('''cp %(system_root)s/usr/bin/libtool %(builddir)s/libtool''')
		self.file_sub ([('#! /bin/sh', '#! /bin/sh\ntagname=CXX')],
			       '%(builddir)s/libtool')

class Guile (gub.Target_package):

	## Ugh. C&P.
	def guile_version (self):
		return '.'.join (self.ball_version.split ('.')[0:])
	
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
		
		self.system ('''cp %(system_root)s/usr/bin/libtool %(builddir)s/libtool''')
		self.system ('''cp %(system_root)s/usr/bin/libtool %(builddir)s/guile-readline/libtool''')

	def install (self):
		Guile.install (self)
		# dlopen-able .la files go in BIN dir, BIN OR LIB package
		self.system ('''mv %(install_root)s/usr/lib/lib*[0-9].la %(install_root)s/usr/bin''')

class Guile__linux (Guile):
	def compile_command (self):
		# FIXME: when not x-building, guile runs guile without
		# setting the proper LD_LIBRARY_PATH.
		return 'export LD_LIBRARY_PATH=%(builddir)s/libguile/.libs:$LD_LIBRARY_PATH;' \
		       + Guile.compile_command (self)

class Guile__darwin (Guile):
	def install (self):
		Guile.install (self)
		pat = self.expand_string ('%(install_root)s/usr/lib/libguile-srfi*.dylib')
		for f in glob.glob (pat):
			directory = os.path.split (f)[0]
			src = os.path.basename (f)
			dst = os.path.splitext (os.path.basename (f))[0] + '.so'
			
			self.system ('cd %(directory)s && ln -s %(src)s %(dst)s', locals())

class LilyPond (gub.Target_package):
	def configure (self):
		self.autoupdate ()
		gub.Target_package.configure (self)


	def compile (self):
		if (file_is_newer (self.srcdir () + '/config.make.in',
				   self.builddir () + '/config.make') 
		    or file_is_newer (self.srcdir () + '/GNUmakefile.in',
				      self.builddir () + '/GNUmakefile') 
		    or file_is_newer (self.srcdir () + '/config.hh.in',
				      self.builddir () + '/config.make')
		    or file_is_newer (self.srcdir () + '/configure',
				      self.builddir () + '/config.make')):
			self.configure ()

		gub.Target_package.compile (self)
	def configure_command (self):
		## FIXME: pickup $target-guile-config
		return ('PATH=%(system_root)s/usr/bin:$PATH '
			+ gub.Target_package.configure_command (self)
			+ ' --disable-documentation')

        def name_version (self):
		# whugh
		if os.path.exists (self.srcdir ()):
			d = gub.grok_sh_variables (self.srcdir () + '/VERSION')
			return 'lilypond-%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
		return gub.Target_package.name_version (self)

        def gub_name (self):
		nv = self.name_version ()
		b = self.build ()
		p = self.settings.platform
		return '%(nv)s-%(b)s.%(p)s.gub' % locals ()

	def autoupdate (self, autodir=0):
		autodir = self.srcdir ()

		if (file_is_newer (autodir + '/configure.in',
				   self.builddir () + '/config.make') 
		    or file_is_newer (autodir + '/stepmake/aclocal.m4',
				      self.builddir () + '/config.make')):


			self.system ('''
			cd %(autodir)s && bash autogen.sh --noconfigure
			''', locals ())


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
		self.autoupdate ()
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

	def install (self):
		LilyPond.install (self)
		self.system ('''

rm -f %(install_prefix)s/bin/lilypond-windows
install -m755 %(builddir)s/lily/out/lilypond %(install_prefix)s/bin/lilypond-windows.exe
rm -f %(install_prefix)s/bin/lilypond
install -m755 %(builddir)s/lily/out-console/lilypond %(install_prefix)s/bin/lilypond.exe
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


	
	def xinstall_gub (self):
		gub.Target_package.install_gub (self)
		self.system ('''
cd %(installer_root)s/usr/bin && mv lilypond lilypond-bin
''')
		framework_root = gub.Package.installer_root (self)
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
%(installer_root)s/usr/bin/lilypond-bin "$@"
'''
,
		'%(installer_root)s/usr/bin/lilypond',
		env=locals ())
		os.chmod ('%(installer_root)s/usr/bin/lilypond' \
			 % self.package_dict (), 0755)

class LilyPond__darwin (LilyPond):
	def __init__ (self, settings):
		LilyPond.__init__ (self, settings)
		## debug aid.

	def configure_command (self):
		cmd = LilyPond.configure_command (self)

		framedir = '%(system_root)s/System/Library/Frameworks/Python.framework/Versions/%(python_version)s'
		cmd += ' --with-python-include=' + framedir + '/include/python%(python_version)s'

		## binaries are huge.
		cmd += ' --disable-optimising '
		return cmd

	def configure (self):
		LilyPond.configure (self)

		make = self.builddir ()+ '/config.make'
		if re.search ("GUILE_ELLIPSIS", open (make).read ()):
			return
		self.file_sub ([('CONFIG_CXXFLAGS = ',
				 'CONFIG_CXXFLAGS = -DGUILE_ELLIPSIS=... '),
				(' -O2 ', '')				
#				(' -g ', '')
				],
			       self.builddir ()+ '/config.make')
		
	def untar (self):
		pass
	
class Gettext (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'

class Gettext__mingw (Gettext):
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
	def xconfigure_command (self):
		## not necessary for 0.14.1
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

	def patch (self):
		self.system ('cd %(srcdir)s && patch --force -p1  < %(patchdir)s/pango-env-sub')

		
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


	def install (self):
		gub.Target_package.install (self)

		etc = self.install_root () + '/usr/etc/pango'
		for a in glob.glob (etc + '/*'):
			self.file_sub ([('/usr/', '$PANGO_PREFIX/')],
				       a)

		open (etc + '/pangorc', 'w').write (
		'''[Pango]
ModuleFiles = "$PANGO_PREFIX/etc/pango/pango.modules"
ModulesPath = "$PANGO_PREFIX/lib/pango/1.4.0/modules"
''')
		shutil.copy2 (self.settings.patchdir + '/pango.modules' ,
			      etc)
		
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
	
class Mingw_runtime (gub.Binary_package):
	def untar (self):
		gub.Binary_package.untar (self)
		self.system ('mkdir -p %(srcdir)s/root/usr')
		self.system ('cd %(srcdir)s/root && mv * usr',
			     ignore_error=True)


class Cygwin (gub.Binary_package):
	"Only need the cygcheck.exe binary."
	
	def untar (self):
		gub.Binary_package.untar (self)

		file = '%s/root/usr/bin/cygcheck.exe' % self.srcdir ()
		cygcheck = open (file).read ()
		self.system ('rm -rf %(srcdir)s/root')
		self.system ('mkdir -p %(srcdir)s/root/usr/bin/')
		open (file, 'w').write (cygcheck)

	def basename (self):
		f = gub.Binary_package.basename (self)
		f = re.sub ('-1$', '', f)
		return f

class W32api (gub.Binary_package):
	def untar (self):
		gub.Binary_package.untar (self)
		self.system ('mkdir -p %(srcdir)s/root/usr')
		self.system ('cd %(srcdir)s/root && mv * usr',
			     ignore_error=True)

class Regex (gub.Target_package):
	pass

class Gs (gub.Binary_package):
	def untar (self):
		gub.Binary_package.untar (self)
		self.system ('cd %(srcdir)s && mv root/gs-%(ball_version)s/* .')

	def install (self):
		gs_prefix = '/usr/share/gs'
		self.system ('''
mkdir -p %(install_root)s/usr
tar -C %(srcdir)s -cf- bin | tar -C %(install_root)s/usr -xvf-
mkdir -p %(install_root)s/%(gs_prefix)s
tar -C %(srcdir)s -cf- fonts lib Resource | tar -C %(install_root)s/%(gs_prefix)s -xvf-
fc-cache %(install_root)s/%(gs_prefix)s/fonts
mkdir -p %(install_root)s/usr/share/doc/gs/html
tar -C %(srcdir)s/doc -cf- --exclude='[A-Z]*[A-Z]' . | tar -C %(install_root)s/usr/share/doc/gs/html -xvf-
tar -C %(srcdir)s/doc -cf- --exclude='*.htm*' . | tar -C %(install_root)s/usr/share/doc/gs/html -xvf-
''',
			     env=locals ())

class LilyPad (gub.Target_package):
	def makeflags (self):
		# FIXME: better fix Makefile
		return gub.join_lines ('''
ALL_OBJS='$(OBJS)'
WRC=/usr/bin/wrc
CPPFLAGS=-I%(system_root)s/usr/include
RC='$(WRC) $(CPPFLAGS)'
LIBWINE=
LIBPORT=
MKINSTALLDIRS=%(srcdir)s/mkinstalldirs
INSTALL_PROGRAM=%(srcdir)s/install-sh
''')
		
	def compile_command (self):
		return gub.Target_package.compile_command (self) \
		       + self.makeflags ()

	def install_command (self):
		return gub.Target_package.broken_install_command (self) \
		       + self.makeflags ()


class Ghostscript (gub.Target_package):
	def srcdir (self):
		return re.sub ('-source', '', gub.Target_package.srcdir(self))
	def untar (self):
		gub.Target_package.untar (self)
		self.system ("cd %(targetdir)s/build && rm -f espgs-%(version)s-source && ln -s %(srcdir)s espgs-%(version)s-source ")
		
	def name (self):
		return 'ghostscript'
	def patch (self):
		self.file_sub ([(r'mkdir -p \$\(bindir\)', 'mkdir -p $(DESTDIR)$(bindir)'),
				(r'mkdir -p \$\(datadir\)', 'mkdir -p $(DESTDIR)$(datadir)'),
				(r'mkdir -p \$\(scriptdir\)', 'mkdir -p $(DESTDIR)$(scriptdir)'),
				(r'\$\(INSTALL_PROGRAM\) \$\(GS_XE\) \$\(bindir\)/\$\(GS\)',
				 r'$(INSTALL_PROGRAM) $(GS_XE) $(DESTDIR)$(bindir)/$(GS)'),
				(r'(\$\(INSTALL_PROGRAM\).*) \$\(scriptdir\)',
				 r'\1  $(DESTDIR)$(scriptdir)'),
				],
			       self.srcdir () + '/src/unixinst.mak')

	def compile (self):
		cmd = 'cd %(builddir)s && (mkdir obj || true) && make CC=gcc CFLAGS= CPPFLAGS= GCFLAGS= obj/genconf obj/echogs obj/genarch obj/arch.h'
		self.system (cmd)
		self.fixup_arch ()
		gub.Target_package.compile (self)

	def configure_command (self):
		cmd = gub.Target_package.configure_command (self)
		cmd += ' --with-drivers=FILES --without-x --disable-cups '
		return cmd

	def configure (self):
		gub.Target_package.configure (self)
		self.file_sub ([('-Dmalloc=rpl_malloc', '')],
			       self.builddir () + '/Makefile')

class Ghostscript__darwin (Ghostscript): 
	def fixup_arch (self):
		self.file_sub ([('#define ARCH_CAN_SHIFT_FULL_LONG 0', '#define ARCH_CAN_SHIFT_FULL_LONG 1'),
				('#define ARCH_CACHE1_SIZE 1048576', '#define ARCH_CACHE1_SIZE 2097152'),
				('#define ARCH_IS_BIG_ENDIAN 0', '#define ARCH_IS_BIG_ENDIAN 1')],
			       self.builddir () + '/obj/arch.h') 
		
class Libjpeg (gub.Target_package):
	def name(self):
		return 'libjpeg'
	def srcdir (self):
		return re.sub (r'src\.v', '-', gub.Target_package.srcdir(self))
	def configure_command (self):
		return re.sub ('--config-cache', '',
			       gub.Target_package.configure_command (self))
	def configure (self):
		gub.Target_package.configure (self)

		arch = 'powerpc-apple' ## fixme. 
		self.system ('''cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(arch)s''' , locals ())

		self.file_sub (
			[(r'(\(INSTALL_[A-Z]+\).*) (\$[^ ]+)$', r'\1 $(DESTDIR)\2')],
			self.builddir () + '/Makefile')

	def install_command (self):
		return ("mkdir -p  %(install_root)s/usr/include  %(install_root)s/usr/lib && make DESTDIR=%(install_root)s install-headers install-lib ")
	
class Libpng (gub.Target_package):
	def name (self):
		return 'libpng'
	def patch (self):
		self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@', r'\1${DESTDIR}@PKGCONFIGDIR@')],
			       self.srcdir () + '/Makefile.in')

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
		Darwin_sdk (settings).with (version='0.0', mirror=download.hw,
					    format='gz'),
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2',
					 depends=['darwin-sdk']
					 ),
		Freetype (settings).with (version='2.1.10', mirror=download.nongnu_savannah,
					  format='bz2',
					  depends=['darwin-sdk']),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2',
				       depends=['darwin-sdk']),
		Glib__darwin (settings).with (version='2.8.4', mirror=download.gtk,
					      depends=['darwin-sdk', 'gettext']),
		Fontconfig__darwin (settings).with (version='2.3.2', mirror=download.fontconfig,
						    depends=['expat', 'freetype']),
		Pango__darwin (settings).with (version='1.10.1', mirror=download.gtk,
					       depends = ['glib', 'fontconfig', 'freetype']
					       ),
		Gmp__darwin (settings).with (version='4.1.4',depends=['darwin-sdk']),

		## 1.7.3  is actually CVS repackaged.
#		Guile (settings).with (version='1.7.3', mirror=download.gnu, format='gz'),
		Guile__darwin (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2',
				       depends=['gmp','darwin-sdk']
				       ),
		Libjpeg (settings).with (version='v6b', mirror=download.jpeg),
		Libpng (settings).with (version='1.2.8', mirror=download.libpng),
		Ghostscript__darwin (settings).with (version="8.15.1", mirror=download.cups, format='bz2', depends=['libjpeg', 'libpng']),
		LilyPond__darwin (settings).with (mirror=cvs.gnu, download=gub.Package.cvs,
						  track_development=True,
						  depends=['pango', 'guile']
						  ),
	),
	'mingw': (
		Mingw_runtime (settings).with (version='3.9', mirror=download.mingw),
		Libtool (settings).with (version='1.5.20',
					 depends=['mingw-runtime']
					 ),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2',
				      depends=['mingw-runtime']
				      ),
		Gettext__mingw (settings).with (version='0.14.5-1', mirror=download.lp, format='bz2',
						depends=['mingw-runtime']
						),
		Libiconv (settings).with (version='1.9.2', depends=['gettext']),
		Freetype (settings).with (version='2.1.7', mirror=download.freetype, depends=['libtool', 'zlib']),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig__mingw (settings).with (version='2.3.2', mirror=download.fontconfig,
						   depends=['expat', 'freetype', 'libtool']),
		Gmp__mingw (settings).with (version='4.1.4',
					    depends=['mingw-runtime']
					    ),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile__mingw (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2', depends=['gettext', 'gmp', 'libtool', 'regex']),
		Glib (settings).with (version='2.8.4', mirror=download.gtk, depends=['gettext', 'libiconv']),
		Pango__mingw (settings).with (version='1.10.1', mirror=download.gtk, depends=['freetype', 'fontconfig', 'glib', 'libiconv']),
		Python__mingw (settings).with (version='2.4.2', mirror=download.python, format='bz2',
					       depends=['mingw-runtime']
					       ),
		Cygwin (settings).with (version='1.5.18-1', mirror=download.cygwin, format='bz2', depends=['mingw-runtime']), 
		Gs (settings).with (version='8.15-1', mirror=download.lp, format='bz2', depends=['mingw-runtime']),
		W32api (settings).with (version='3.5', mirror=download.mingw),
		Regex (settings).with (version='2.3.90-1', mirror=download.lp, format='bz2', depends=['mingw-runtime']),
		LilyPad (settings).with (version='0.0.7-1', mirror=download.lp, format='bz2', depends=['w32api']),
		LilyPond__mingw (settings).with (mirror=cvs.gnu, download=gub.Package.cvs,
						 depends=['gettext', 'guile', 'pango', 'python'],
						 track_development=True),
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
		LilyPond__linux (settings).with (mirror=cvs.gnu, download=gub.Package.cvs,
						 track_development=True),
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
		'darwin' : [installer.Darwin_bundle (settings)],
		'linux' : [
		installer.Tgz (settings),
		installer.Deb (settings),
		installer.Rpm (settings),
		installer.Autopackage (settings),
		],
		'mingw' : [installer.Nsis (settings)],
	}
	
	return installers[settings.platform]
