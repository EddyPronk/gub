import copy
import glob
import os
import re
import shutil
import misc

## gub specific.
from settings import Settings
import gub
import download
import cvs
import targetpackage

def file_is_newer (f1, f2):
	return (not os.path.exists (f2)
		or os.stat (f1).st_mtime >  os.stat (f2).st_mtime)

class Fondu (targetpackage.Target_package):
	pass

class Fondu__darwin (Fondu):
	def patch(self):
		Fondu.patch (self)
		self.file_sub ([('/System/Library/',
				 '%(system_root)s/System/Library/')],
			       '%(srcdir)s/Makefile.in')
		
class Libtool (targetpackage.Target_package):
	pass

class Python (targetpackage.Target_package):
	def set_download (self, mirror, format='gz', downloader=None):
		targetpackage.Target_package.set_download (self, mirror, format, downloader)
		self.url = re.sub ('python-', 'Python-' , self.url)

	def patch (self):
		targetpackage.Target_package.patch (self)
		self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-1.patch')
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-configure.in-posix.patch')

	def python_version (self):
		return '.'.join (self.ball_version.split ('.')[0:2])

	def get_substitution_dict (self, env = {}):
		dict = targetpackage.Target_package.get_substitution_dict (self, env)
		dict['python_version'] = self.python_version ()
		return dict

	# FIXME: ugh cross compile + mingw patch; move to cross-Python?
	def configure (self):
		self.system ('''cd %(srcdir)s && autoconf''')
		self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
		targetpackage.Target_package.configure (self)

#	def configure_command (self):
#		return "MACHDEP=linux2 " + targetpackage.Target_package.configure_command (self)

	def compile_command (self):
		##
		## UGH.: darwin Python vs python (case insensitive FS)
		c = targetpackage.Target_package.compile_command (self)
		c += ' BUILDPYTHON=python-bin '
		return c

	def install_command (self):
		##
		## UGH.: darwin Python vs python (case insensitive FS)
		c = targetpackage.Target_package.install_command (self)
		c += ' BUILDPYTHON=python-bin '
		return c
	
class Python__mingw (Python):
	def __init__ (self, settings):
		Python.__init__ (self, settings)
		self.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_root)s/usr/include' % self.settings.__dict__

	# FIXME: first is cross compile + mingw patch, backported to
	# 2.4.2 and combined in one patch; move to cross-Python?
	def patch (self):
		Python.patch (self)
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-winsock2.patch
''')

	def config_cache_overrides (self, str):
		# Ok, I give up.  The python build system wins.  Once
		# someone manages to get -lwsock32 on the
		# sharedmodules link command line, *after*
		# timesmodule.o, this can go away.
		return re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
			       str)

	def install (self):
		Python.install (self)
		for i in glob.glob ('%(install_root)s/usr/lib/python%(python_version)s/lib-dynload/*.so*' \
				    % self.get_substitution_dict ()):
			dll = re.sub ('\.so*', '.dll', i)
			self.system ('mv %(i)s %(dll)s', locals ())
		self.system ('''
cp %(install_root)s/usr/lib/python%(python_version)s/lib-dynload/* %(install_root)s/usr/bin
''')
		self.system ('''
chmod 755 %(install_root)s/usr/bin/*
''')

class Python__freebsd (Python):
	# FIXME: ugh cross compile + mingw patch; move to cross-Python?
	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-1.patch
''')

	# FIXME: ugh cross compile + mingw patch; move to cross-Python?
	def configure (self):
		self.system ('''cd %(srcdir)s && autoconf''')
		self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
		targetpackage.Target_package.configure (self)

class Gmp (targetpackage.Target_package):
	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()
		# automake's Makefile.in's too old for new libtool,
		# but autoupdating breaks even more.  This nice
		# hack seems to work.
		self.file_sub ([('#! /bin/sh', '#! /bin/sh\ntagname=CXX')],
			       '%(builddir)s/libtool')
		
class Gmp__darwin (Gmp):
	def patch (self):

		## powerpc/darwin cross barfs on all C++ includes from
		## a C linkage file.
		## don't know why. Let's patch C++ completely from GMP.

		self.file_sub ([('__GMP_DECLSPEC_XX std::[oi]stream& operator[<>][^;]+;$', ''),
				('#include <iosfwd>', ''),
				('<cstddef>','<stddef.h>')
				],
			       '%(srcdir)s/gmp-h.in')
		Gmp.patch (self)

class Gmp__mingw (Gmp):
	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gmp-4.1.4-1.patch
''')

	def xconfigure (self):
		targetpackage.Target_package.configure (self)
		self.file_sub ([('#! /bin/sh', '#! /bin/sh\ntagname=CXX')],
			       '%(builddir)s/libtool')

	def install (self):
		Gmp.install (self)
		self.system ('''
mv %(install_root)s/usr/lib/*dll %(install_root)s/usr/bin || true
''')
		
class Guile (targetpackage.Target_package):
	# FIXME: C&P.
	def guile_version (self):
		return '.'.join (self.ball_version.split ('.')[0:2])

	def configure_command (self):
		return (targetpackage.Target_package.configure_command (self)
			+ misc.join_lines ('''
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
'''))

	def configure (self):
		targetpackage.Target_package.configure (self)
		self.update_libtool ()

	def install (self):
		targetpackage.Target_package.install (self)
		## can't assume that /usr/bin/guile is the right one.
		version = self.read_pipe ('''\
GUILE_LOAD_PATH=%(install_prefix)s/share/guile/* guile -e main -s  %(install_prefix)s/bin/guile-config --version 2>&1\
''').split ()[-1]
		self.system ('mkdir -p %(install_prefix)s/cross/bin/')

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
			   '%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config')
		os.chmod ('%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config' % self.get_substitution_dict (), 0755)

class Guile__mingw (Guile):
	def __init__ (self, settings):
		Guile.__init__ (self, settings)
		self.target_gcc_flags = '-mms-bitfields'

	def xpatch (self):
		## FIXME
		self.system ('''
cd %(srcdir)s && patch -p1 < %(lilywinbuilddir)s/patch/guile-1.7.2-3.patch
''')

# FIXME: ugh, C&P to Guile__freebsd, put in cross-Guile?
	def configure_command (self):
		# watch out for whitespace
		builddir = self.builddir ()
		srcdir = self.srcdir ()
		return (Guile.configure_command (self)
		       + misc.join_lines ('''
PATH_SEPARATOR=";"
LDFLAGS=-L%(system_root)s/usr/lib
CC_FOR_BUILD="
C_INCLUDE_PATH=
CPPFLAGS=
LIBRARY_PATH=
LDFLAGS=
cc
-I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
'''))

	def config_cache_overrides (self, str):
		return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_root)s/usr/lib"}
'''

	def configure (self):
		if 0: # using patch
			targetpackage.Target_package.autoupdate (self)
			self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''',
					 '\\1')],
				       '%(srcdir)s/configure')
			os.chmod ('%(srcdir)s/configure' % self.get_substitution_dict (), 0755)
		Guile.configure (self)

		self.file_sub ([
			('^\(allow_undefined_flag=.*\)unsupported', '\\1'),
			('-mwindows', ''),
			],
			       '%(builddir)s/libtool')
		self.file_sub ([
			('^\(allow_undefined_flag=.*\)unsupported', '\\1'),
			('-mwindows', ''),
			],
			       '%(builddir)s/guile-readline/libtool')

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

class Guile__freebsd (Guile):
	def configure_command (self):
		# watch out for whitespace
		builddir = self.builddir ()
		srcdir = self.srcdir ()
# FIXME: ugh, C&P from Guile__mingw, put in cross-Guile?
##PATH_SEPARATOR=";"
		return (Guile.configure_command (self)
		       + misc.join_lines ('''\
CC_FOR_BUILD="
C_INCLUDE_PATH=
CPPFLAGS=
LIBRARY_PATH=
cc
-I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
'''))


class Guile__darwin (Guile):
	def install (self):
		Guile.install (self)
		pat = self.expand ('%(install_root)s/usr/lib/libguile-srfi*.dylib')
		for f in glob.glob (pat):
			directory = os.path.split (f)[0]
			src = os.path.basename (f)
			dst = os.path.splitext (os.path.basename (f))[0] + '.so'

			self.system ('cd %(directory)s && ln -s %(src)s %(dst)s', locals())

class LilyPond (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)

		# FIXME: should add to C_INCLUDE_PATH
		builddir = self.builddir ()
		self.target_gcc_flags = (settings.target_gcc_flags
					 + ' -I%(builddir)s' % locals ())

	def configure_command (self):
		## FIXME: pickup $target-guile-config
		return (targetpackage.Target_package.configure_command (self)
			+ misc.join_lines ('''
--enable-relocation
--disable-documentation
--with-python-include=%(system_root)s/usr/include/python%(python_version)s
'''))

	def configure (self):
		self.autoupdate ()
	

	def do_configure (self):
		if not os.path.exists (self.expand ('%(builddir)s/FlexLexer.h')):
			flex = self.read_pipe ('which flex')
			flex_include_dir = os.path.split (flex)[0] + "/../include"
			gub.Package.system (self, '''
mkdir -p %(builddir)s
cp %(flex_include_dir)s/FlexLexer.h %(builddir)s/
''', locals ())
		targetpackage.Target_package.configure (self)

	# FIXME: shared for all CVS packages
	def srcdir (self):
		return '%(allsrcdir)s/%(name)s-%(version)s'

#	# FIXME: shared for all CVS packages
	def builddir (self):
		return '%(targetdir)s/build/%(name)s-%(version)s'

	def compile (self):
		d = self.get_substitution_dict ()
		if (file_is_newer ('%(srcdir)s/config.make.in' % d,
				   '%(builddir)s/config.make' % d)
		    or file_is_newer ('%(srcdir)s/GNUmakefile.in' % d,
				      '%(builddir)s/GNUmakefile' % d)
		    or file_is_newer ('%(srcdir)s/config.hh.in' % d,
				      '%(builddir)s/config.make' % d)
		    or file_is_newer ('%(srcdir)s/configure' % d,
				      '%(builddir)s/config.make' % d)):
			self.do_configure ()
			
		targetpackage.Target_package.compile (self)

	def compile_command (self):
		s = targetpackage.Target_package.compile_command (self)
		if self.settings.lilypond_branch == 'lilypond_2_6':
			# ugh, lilypond-2.6 has broken srcdir build system
			# and gub is leaking all kind of vars.
			s = 'unset builddir srcdir topdir;' + s
		return s
		
        def name_version (self):
		# whugh
		if os.path.exists (self.srcdir ()):
			d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
			return 'lilypond-%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
		return targetpackage.Target_package.name_version (self)

	def install (self):
		targetpackage.Target_package.install (self)
		d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
		v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
		self.system ("cd %(install_root)s/usr/share/lilypond && rm -f current && ln -sf %(v)s current",
			     locals ())

        def gub_name (self):
		nv = self.name_version ()
		b = self.build ()
		p = self.settings.platform
		return '%(nv)s-%(b)s.%(p)s.gub' % locals ()

	def autoupdate (self, autodir=0):
		autodir = self.srcdir ()

		if (file_is_newer (self.expand ('%(autodir)s/configure.in', locals ()),
				   self.expand ('%(builddir)s/config.make',locals ()))
		    or file_is_newer (self.expand ('%(autodir)s/stepmake/aclocal.m4', locals ()),
				      self.expand ('%(autodir)s/configure', locals ()))):
			self.system ('''
			cd %(autodir)s && bash autogen.sh --noconfigure
			''', locals ())
			self.do_configure ()

class LilyPond__mingw (LilyPond):
        def patch (self):
		# FIXME: for our gcc-3.4.5 cross compiler in the mingw
		# environment, THIS is a magic word.
		self.file_sub ([('THIS', 'SELF')],
			       '%(srcdir)s/lily/parser.yy')

	def do_configure (self):
		LilyPond.do_configure (self)
		# Configure (compile) without -mwindows for console
		self.target_gcc_flags = '-mms-bitfields'
		self.config_cache ()
		cmd = self.configure_command () \
		      + ' --enable-config=console'
		self.system ('''cd %(builddir)s && %(cmd)s''',
			     locals ())
		# Do not override flags while running make lateron
		self.target_gcc_flags = ''

	def compile_command (self):
		python_lib = "%(system_root)s/usr/bin/libpython%(python_version)s.dll"
		return LilyPond.compile_command (self) \
		       + misc.join_lines ('''
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
				    % self.get_substitution_dict ()):
			s = self.read_pipe ('file %(i)s' % locals ())
			if s.find ('guile') >= 0:
				self.system ('mv %(i)s %(i)s.scm', locals ())
			elif  s.find ('python') >= 0:
				self.system ('mv %(i)s %(i)s.py', locals ())

		for i in self.read_pipe ('''
find %(install_root)s -name "*.ly"
''').split ():
			s = open (i).read ()
			open (i, 'w').write (re.sub ('\r*\n', '\r\n', s))

class LilyPond__cygwin (LilyPond__mingw):
	pass

class LilyPond__linux (LilyPond):
	def configure_command (self):
		return LilyPond.configure_command (self) + misc.join_lines ('''
--enable-static-gxx
''')
#--with-framework-dir=../%(framework_dir)s/usr

	def install (self):
		LilyPond.install (self)
		# handle framework dir in relocate.cc?
		# self.wrap_framework_program ('lilypond')
		for i in (
			'abc2ly',
			'convert-ly',
			'etf2ly',
			'lilypond-book',
			'lilypond-invoke-editor',
			'midi2ly',
			'mup2ly',
			'musicxml2ly'
			):
			self.wrap_interpreter (i, 'python')
		self.wrap_interpreter (i, 'guile')

	def wrap_framework_program (self, name):
		return
	
		wrapper = name
		program = '.%(name)s-wrapped' % locals ()
		self.system ('''
cd %(install_root)s/usr/bin && mv %(wrapper)s %(program)s
''',
			     locals ())
		self.dump ('''#! /bin/sh
# Not using Python/Guile, as those also need a relocation wrapper
FRAMEWORK_DIR="${FRAMEWORK_DIR-/%(framework_dir)s}"
if [ ! -d "$FRAMEWORK_DIR" ]; then
    if expr "$0" : '/' > /dev/null 2>&1; then
        bindir=$(cd $(dirname $0); pwd)
    elif [ "$(basename $0)" != "$0" ]; then
        bindir=$PWD/$(dirname $0)
    else
        (IFS=:; for d in $PATH; do
	    if [ -x $d/%(program)s ]; then
	        bindir=$d
	        break
	    fi
	done)
	bindir=/usr/bin
    fi
    prefix=$(dirname $bindir)
    FRAMEWORK_DIR="$prefix/%(framework_dir)s"
fi
FONTCONFIG_FILE=$FRAMEWORK_DIR/usr/etc/fonts/fonts.conf \\
GUILE_LOAD_PATH=$FRAMEWORK_DIR/usr/share/guile/%(guile_version)s:$GUILE_LOAD_PATH \\
GS_FONTPATH=$FRAMEWORK_DIR/usr/share/ghostscript/%(ghostscript_version)s/fonts:$GS_FONTPATH \\
GS_LIB=$FRAMEWORK_DIR/usr/share/ghostscript/%(ghostscript_version)s/lib:$GS_LIB \\
USING_RPATH_LD_LIBRARY_PATH=$FRAMEWORK_DIR/usr/lib:$LD_LIBRARY_PATH \\
LD_LIBRARY_PATH= \\
LILYPONDPREFIX=$prefix/share/lilypond/%(version)s/ \\
PANGO_PREFIX=${PANGO_PREFIX-$FRAMEWORK_DIR/usr} \\
PANGO_RC_FILE=${PANGO_RC_FILE-$FRAMEWORK_DIR/usr/etc/pango/pangorc} \\
PANGO_SO_EXTENSION=.so \\
PATH=$FRAMEWORK_DIR/usr/bin:$PATH \\
PYTHONPATH=$FRAMEWORK_DIR/../python:$PYTHONPATH \\
PYTHONPATH=$FRAMEWORK_DIR/usr/lib/python%(python_version)s:$PYTHONPATH \\
$prefix/bin/%(program)s "$@"
'''
,
		'%(install_root)s/usr/bin/%(name)s',
		env=locals ())
		os.chmod (self.expand ('%(install_root)s/usr/bin/%(name)s',
				       locals ()), 0755)

	def wrap_interpreter (self, name, interpreter):
		return
	
		wrapper = name
		program = '.%(name)s-wrapped' % locals ()
		self.system ('''
cd %(install_root)s/usr/bin && mv %(wrapper)s %(program)s
''',
			     locals ())
		self.dump ('''#! /bin/sh
FRAMEWORK_DIR="${FRAMEWORK_DIR-/%(framework_dir)s}"
if [ ! -d "$FRAMEWORK_DIR" ]; then
    if expr "$0" : '/' > /dev/null 2>&1; then
        bindir=$(cd $(dirname $0); pwd)
    elif [ "$(basename $0)" != "$0" ]; then
        bindir=$PWD/$(dirname $0)
    else
        (IFS=:; for d in $PATH; do
	    if [ -x $d/%(program)s ]; then
	        bindir=$d
	        break
	    fi
	done)
	bindir=/usr/bin
    fi
    prefix=$(dirname $bindir)
    FRAMEWORK_DIR="$prefix/%(framework_dir)s"
fi
GUILE_LOAD_PATH=$FRAMEWORK_DIR/usr/share/guile/%(guile_version)s:$GUILE_LOAD_PATH \\
LD_LIBRARY_PATH=$FRAMEWORK_DIR/usr/lib:$LD_LIBRARY_PATH \\
LILYPONDPREFIX=$prefix/share/lilypond/%(bundle_version)s/ \\
PATH=$FRAMEWORK_DIR/usr/bin:$PATH \\
PYTHONPATH=$FRAMEWORK_DIR/../python:$PYTHONPATH \\
PYTHONPATH=$FRAMEWORK_DIR/usr/lib/python%(python_version)s:$PYTHONPATH \\
%(interpreter)s $bindir/%(program)s "$@"
'''
,
		'%(install_root)s/usr/bin/%(name)s',
		env=locals ())
		os.chmod (self.expand ('%(install_root)s/usr/bin/%(name)s',
				       locals ()), 0755)

class LilyPond__darwin (LilyPond):
	def __init__ (self, settings):
		LilyPond.__init__ (self, settings)
		## debug aid.

	def configure_command (self):
		cmd = LilyPond.configure_command (self)

		pydir = ('%(system_root)s/System/Library/Frameworks/Python.framework/Versions/%(python_version)s'
			 + '/include/python%(python_version)s')

		cmd += ' --with-python-include=' + pydir
		cmd += ' --enable-static-gxx '
		
		return cmd

	def do_configure (self):
		LilyPond.do_configure (self)

		make = self.expand ('%(builddir)s/config.make')

		if re.search ("GUILE_ELLIPSIS", open (make).read ()):
			return
		self.file_sub ([('CONFIG_CXXFLAGS = ',
				 'CONFIG_CXXFLAGS = -DGUILE_ELLIPSIS=... '),
#				(' -O2 ', '')
## ugh. this will break if other progs use -g too
				(' -g ', ' ')
				],
			       '%(builddir)s/config.make')


class Gettext (targetpackage.Target_package):
	def configure_command (self):

		return (targetpackage.Target_package.configure_command (self)
			+ ' --disable-csharp')

	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()



class Gettext__freebsd (Gettext):
	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/gettext-0.14.1-getopt.patch
''')

class Gettext__mingw (Gettext):
	def config_cache_overrides (self, str):
		return (re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
			       str)
			+ '''
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
''')
	def install (self):

		## compile of gettext triggers configure in between.  (hgwurgh.)
		self.update_libtool()
		Gettext.install (self)

class Gettext__darwin (Gettext):
	def xconfigure_command (self):
		## not necessary for 0.14.1
		return re.sub (' --config-cache', '',
			       Gettext.configure_command (self))

class Libiconv (targetpackage.Target_package):
	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()
	def install (self):
		targetpackage.Target_package.install (self)
		self.system ('rm %(install_root)s/usr/lib/charset.alias')
		
class Glib (targetpackage.Target_package):
	def config_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()
		
	def install (self):
		targetpackage.Target_package.install (self)
		self.system ('rm %(install_root)s/usr/lib/charset.alias',
			     ignore_error=True)
		

class Glib__darwin (Glib):
	def patch (self):
		targetpackage.Target_package.patch(self)
		self.file_sub ([('<malloc.h>', '<sys/malloc.h>')],
			       '%(srcdir)s/glib/gslice.c')
		
	def configure (self):
		Glib.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')

class Glib__freebsd (Glib):
	def patch (self):
		Glib.patch(self)
		self.file_sub ([('<malloc.h>', '<stdlib.h>'),
				
				##ugh.
				('#ifdef G_OS_WIN32',
				 '#define _SC_PAGESIZE		47\n'
				 + '#ifdef G_OS_WIN32\n'
				 )
				],
			       '%(srcdir)s/glib/gslice.c')

class Pango (targetpackage.Target_package):
	def configure_command (self):
		return targetpackage.Target_package.configure_command (self) \
		       + misc.join_lines ('''
--without-x
--without-cairo
''')

	def configure (self):
		targetpackage.Target_package.configure (self)		
		self.update_libtool ()
	def patch (self):
		targetpackage.Target_package.patch (self)
		self.system ('cd %(srcdir)s && patch --force -p1 < %(patchdir)s/pango-env-sub')

		## ugh, already fixed in Pango CVS.
		f = open (self.expand ('%(srcdir)s/pango/pango.def'), 'a')
		f.write ('	pango_matrix_get_font_scale_factor\n')

	def fix_modules (self):
		etc = self.expand ('%(install_root)s/usr/etc/pango')
		for a in glob.glob (etc + '/*'):
			self.file_sub ([('/usr/', '$PANGO_PREFIX/')],
				       a)

		open (etc + '/pangorc', 'w').write (
		'''[Pango]
ModuleFiles = "$PANGO_PREFIX/etc/pango/pango.modules"
ModulesPath = "$PANGO_PREFIX/lib/pango/1.4.0/modules"
''')
		shutil.copy2 (self.expand ('%(patchdir)s/pango.modules'),
			      etc)

class Pango__mingw (Pango):
	def install (self):
		targetpackage.Target_package.install (self)
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
		os.chmod ('%(srcdir)s/configure' % self.get_substitution_dict (), 0755)

	def install (self):
		Pango.install (self)
		self.fix_modules ()

class Pango__darwin (Pango):
	def configure (self):
		Pango.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')

	def install (self):
		targetpackage.Target_package.install (self)		
		self.fix_modules ()

class Freetype (targetpackage.Target_package):
	def configure (self):
#		self.autoupdate (autodir=os.path.join (self.srcdir (),
#						       'builds/unix'))

		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		targetpackage.Target_package.configure (self)

		# # FIXME: libtool too old for cross compile
		self.update_libtool ()

		self.file_sub ([('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX')], '%(builddir)s/Makefile')



class Freetype__mingw (Freetype):
	def configure (self):
		Freetype.configure(self)
		self.dump ('''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''',
			   '%(builddir)s/Makefile',
			   mode='a')


class Fontconfig (targetpackage.Target_package):
	def configure_command (self):
		# FIXME: system dir vs packaging install

		## UGH  - this breaks  on Darwin!
		return targetpackage.Target_package.configure_command (self) \
		      + misc.join_lines ('''
--with-freetype-config="%(system_root)s/usr/bin/freetype-config
--prefix=%(system_root)s/usr
"''')
#--urg-broken-if-set-exec-prefix=%(system_root)s/usr

	def configure (self):
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env={'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(system_root)s/usr \
'''})
#--urg-broken-if-set-exec-prefix=%(system_root)s/usr \
		targetpackage.Target_package.configure (self)

		# # FIXME: libtool too old for cross compile
		self.update_libtool ()

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
		       + misc.join_lines ('''
--with-default-fonts=@WINDIR@\\fonts\\
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts
''')

class Fontconfig__darwin (Fontconfig):
	def configure_command (self):
		cmd = Fontconfig.configure_command (self)
		cmd += ' --with-add-fonts=/Library/Fonts,/System/Library/Fonts '
		return cmd

	def configure (self):
		Fontconfig.configure (self)
		self.file_sub ([('-Wl,[^ ]+ ', '')],
			       '%(builddir)s/src/Makefile')

	def install (self):
		Fontconfig.install (self)

		conf_file = open (self.expand ('%(install_root)s/usr/etc/fonts/local.conf'), 'w')
		conf_file.write ('<cache>~/.lilypond-font.cache-1</cache>')


class Fontconfig__linux (Fontconfig):
	def configure (self):
		Fontconfig.configure (self)
		self.file_sub ([
			('^sys_lib_search_path_spec="/lib/* ',
			 'sys_lib_search_path_spec="%(system_root)s/usr/lib /lib '),
			# FIXME: typo: dl_search (only dlsearch exists).
			# comment-out for now
			#('^sys_lib_dl_search_path_spec="/lib/* ',
			# 'sys_lib_dl_search_path_spec="%(system_root)s/usr/lib /lib ')
			],
			       '%(builddir)s/libtool')

class Expat (targetpackage.Target_package):
	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()

	def makeflags (self):
		return misc.join_lines ('''
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H"
EXEEXT=
RUN_FC_CACHE_TEST=false
''')
	def compile_command (self):
		return targetpackage.Target_package.compile_command (self) \
		       + self.makeflags ()

	def install_command (self):
		return targetpackage.Target_package.broken_install_command (self) \
		       + self.makeflags ()

class Zlib (targetpackage.Target_package):
	def patch (self):
		self.shadow_tree ('%(srcdir)s', '%(builddir)s')
		targetpackage.Target_package.patch (self)
		self.file_sub ([("='/bin/true'", "='true'")],
			       '%(srcdir)s/configure')
	def configure (self):
		zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.2'
		if self.settings.platform.startswith ('mingw'):
			zlib_is_broken = 'target=mingw'
		self.system ('''
sed -i~ 's/mgwz/libz/' %(srcdir)s/configure
cd %(builddir)s && %(zlib_is_broken)s AR="%(AR)s r" %(srcdir)s/configure --shared
''', locals ())

	def install_command (self):
		return targetpackage.Target_package.broken_install_command (self)

class Regex (targetpackage.Target_package):
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

class LilyPad (targetpackage.Target_package):
	def makeflags (self):
		# FIXME: better fix Makefile
		return misc.join_lines ('''
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
		return targetpackage.Target_package.compile_command (self) \
		       + self.makeflags ()

	def install_command (self):
		return targetpackage.Target_package.broken_install_command (self) \
		       + self.makeflags ()

class Ghostscript (targetpackage.Target_package):
	def srcdir (self):
		return re.sub ('-source', '', targetpackage.Target_package.srcdir (self))

	def builddir (self):
		return re.sub ('-source', '', targetpackage.Target_package.builddir (self))

	def name (self):
		return 'ghostscript'

	# FIXME: C&P.
	def ghostscript_version (self):
		return '.'.join (self.ball_version.split ('.')[0:2])

	def patch (self):
		self.system ("cd %(srcdir)s && patch -p2 < %(patchdir)s/gs-ttf.patch")
		self.file_sub ([(r'mkdir -p \$\(bindir\)', 'mkdir -p $(DESTDIR)$(bindir)'),
				(r'mkdir -p \$\(datadir\)', 'mkdir -p $(DESTDIR)$(datadir)'),
				(r'mkdir -p \$\(scriptdir\)', 'mkdir -p $(DESTDIR)$(scriptdir)'),
				(r'\$\(INSTALL_PROGRAM\) \$\(GS_XE\) \$\(bindir\)/\$\(GS\)',
				 r'$(INSTALL_PROGRAM) $(GS_XE) $(DESTDIR)$(bindir)/$(GS)'),
				(r'(\$\(INSTALL_PROGRAM\).*) \$\(scriptdir\)',
				 r'\1  $(DESTDIR)$(scriptdir)'),
				],
			       '%(srcdir)s/src/unixinst.mak')

	def fixup_arch (self):
		substs = []
		arch = self.settings.target_architecture

		cache_size = 1024*1024
		big_endian = 0
		can_shift = 1
		
		if arch.find ('powerpc') >= 0:
			big_endian = 1
			can_shift = 1
			cache_size = 2097152
		elif re.search ('i[0-9]86', arch):
			big_endian = 0
			can_shift = 0
			cache_size = 1048576
			
		substs = [('#define ARCH_CAN_SHIFT_FULL_LONG .',
			   '#define ARCH_CAN_SHIFT_FULL_LONG %d' % can_shift),
			  ('#define ARCH_CACHE1_SIZE [0-9]+',
			   '#define ARCH_CACHE1_SIZE %d' % cache_size),
			  ('#define ARCH_IS_BIG_ENDIAN [0-9]',
			   '#define ARCH_IS_BIG_ENDIAN %d' % big_endian)]
		
		self.file_sub (substs, '%(builddir)s/obj/arch.h')

	def compile (self):
		self.system ('''
cd %(builddir)s && (mkdir obj || true)
cd %(builddir)s && make CC=cc CCAUX=cc C_INCLUDE_PATH= CFLAGS= CPPFLAGS= GCFLAGS= LIBRARY_PATH= obj/genconf obj/echogs obj/genarch obj/arch.h
''')
		self.fixup_arch ()
		targetpackage.Target_package.compile (self)
		# URG
		self.system ('''
cp -pv %(builddir)s/lib/gs_init.ps %(srcdir)s/lib/gs_init.ps
''')

	def configure_command (self):
		return (targetpackage.Target_package.configure_command (self)
			+ misc.join_lines ('''
--with-drivers=FILES
--without-x
--disable-cups
--without-ijs
--without-omni
'''))

	def configure (self):
		targetpackage.Target_package.configure (self)
		self.file_sub ([
			('-Dmalloc=rpl_malloc', ''),
			('GLSRCDIR=./src', 'GLSRCDIR=%(srcdir)s/src'),
			('PSSRCDIR=./src', 'PSSRCDIR=%(srcdir)s/src'),
			('PSLIBDIR=./lib', 'PSLIBDIR=%(srcdir)s/lib'),
			('ICCSRCDIR=icclib', 'ICCSRCDIR=%(srcdir)s/icclib'),
			# ESP-specific: addonsdir, omit zillion of
			# warnings (any important ones may be noticed
			# easier).
			('ADDONSDIR=./addons', 'ADDONSDIR=%(srcdir)s/addons'),
			(' -Wmissing-prototypes ', ' '),
			(' -Wstrict-prototypes ', ' '),
			(' -Wmissing-declarations ', ' '),
			],
			       '%(builddir)s/Makefile')

	def install_command (self):
		return (targetpackage.Target_package.install_command (self)
			+ ' install_prefix=%(install_root)s'
			+ ' mandir=%(install_root)s/usr/man/ ')

class Ghostscript__mingw (Ghostscript):
	def __init__ (self, settings):
		Ghostscript.__init__ (self, settings)
		# FIXME: should add to CPPFLAGS...
		self.target_gcc_flags = '-mms-bitfields -D_Windows -D__WINDOWS__'

	def patch (self):
		Ghostscript.patch (self)
		self.system ("cd %(srcdir)s/ && patch -p0 < %(patchdir)s/espgs-8.15-mingw-bluntaxe")
		self.system ("cd %(srcdir)s/ && patch -p1 < %(patchdir)s/ghostscript-8.15-cygwin.patch")
		self.system ("cd %(srcdir)s/ && patch -p1 < %(patchdir)s/ghostscript-8.15-make.patch")

	def configure (self):
		Ghostscript.configure (self)
		self.file_sub ([('^(EXTRALIBS *=.*)', '\\1 -lwinspool -lcomdlg32 -lz')],
			       '%(builddir)s/Makefile')

		self.file_sub ([('^unix__=.*', misc.join_lines ('''unix__=
$(GLOBJ)gp_mswin.$(OBJ)
$(GLOBJ)gp_wgetv.$(OBJ)
$(GLOBJ)gp_stdia.$(OBJ)
$(GLOBJ)gsdll.$(OBJ)
$(GLOBJ)gp_ntfs.$(OBJ)
$(GLOBJ)gp_win32.$(OBJ)
'''))],
			       '%(srcdir)s/src/unix-aux.mak')
		self.file_sub ([('^(LIB0s=.*)', misc.join_lines ('''\\1
$(GLOBJ)gp_mswin.$(OBJ)
$(GLOBJ)gp_wgetv.$(OBJ)
$(GLOBJ)gp_stdia.$(OBJ)
$(GLOBJ)gsdll.$(OBJ)
$(GLOBJ)gp_ntfs.$(OBJ)
$(GLOBJ)gp_win32.$(OBJ)
'''))],
			       '%(srcdir)s/src/lib.mak')

		self.dump ('''
GLCCWIN=$(CC) $(CFLAGS) -I$(GLOBJDIR)
PSCCWIN=$(CC) $(CFLAGS) -I$(GLOBJDIR)
include $(GLSRCDIR)/win32.mak
include $(GLSRCDIR)/gsdll.mak
include $(GLSRCDIR)/winplat.mak
include $(GLSRCDIR)/pcwin.mak
''',
			   '%(builddir)s/Makefile',
			   mode='a')

	def install (self):
		Ghostscript.install (self)
		if self.settings.lilypond_branch != 'lilypond_2_6':
			return
		gs_prefix = '/usr/share/ghostscript/%(ghostscript_version)s'
		fonts = ['c059013l', 'c059016l', 'c059033l', 'c059036l']
		for i in self.read_pipe ('locate %s.pfb' % fonts[0]).split ('\n'):
			dir = os.path.dirname (i)
			if os.path.exists (dir + '/' + fonts[0] + '.afm'):
				break
		fonts_string = ','.join (fonts)
		self.system ('''
mkdir -p %(install_root)s/%(gs_prefix)s/fonts
cp %(dir)s/{%(fonts_string)s}{.afm,.pfb} %(install_root)s/%(gs_prefix)s/fonts
fc-cache %(install_root)s/%(gs_prefix)s/fonts
''', locals ())

class Libjpeg (targetpackage.Target_package):

	def name (self):
		return 'libjpeg'

	def srcdir (self):
		return re.sub (r'src\.v', '-', targetpackage.Target_package.srcdir(self))

	def configure_command (self):
		return re.sub ('--config-cache', '--cache-file=config.cache',
			       targetpackage.Target_package.configure_command (self))
	

	def update_libtool (self):
		self.system ('''
cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(target_architecture)s'''
			     , locals ())
		
		targetpackage.Target_package.update_libtool (self)

	def configure (self):
		guess = self.expand ('%(system_root)s/usr/share/libtool/config.guess')
		sub = self.expand ('%(system_root)s/usr/share/libtool/config.sub')
		for file in sub,guess:
			if os.path.exists (file):
				self.system ('cp -pv %(file)s %(srcdir)s',  locals ())

		targetpackage.Target_package.configure (self)
		self.update_libtool ()
		self.file_sub (
			[
			(r'(\(INSTALL_[A-Z]+\).*) (\$[^ ]+)$',
			 r'\1 $(DESTDIR)\2'),
			 ],
			'%(builddir)s/Makefile')

	def install_command (self):
		return misc.join_lines ('''
mkdir -p %(install_root)s/usr/include %(install_root)s/usr/lib
&& make DESTDIR=%(install_root)s install-headers install-lib
''')

class Libjpeg__darwin (Libjpeg):
	def update_libtool (self):
		arch = 'powerpc-apple'
		self.system ('''
cd %(builddir)s && %(srcdir)s/ltconfig --srcdir %(srcdir)s %(srcdir)s/ltmain.sh %(arch)s
''', locals ())
		targetpackage.Target_package.update_libtool (self)

class Libjpeg__mingw (Libjpeg):
	def configure (self):
		Libjpeg.configure (self)
		# libtool will not build dll if -no-undefined flag is
		# not present
		self.file_sub ([('-version-info',
				 '-no-undefined -version-info')],
			   '%(builddir)s/Makefile')

class Libjpeg__linux (Libjpeg):
	def compile (self):
		Libjpeg.compile (self)
		self.file_sub ([('^#define (HAVE_STDLIB_H) *', '''#ifdef \\1
#define \\1
#endif''')],
			       '%(builddir)s/jconfig.h')

class Libpng (targetpackage.Target_package):
	def name (self):
		return 'libpng'

	def patch (self):
		self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
				 r'\1${DESTDIR}@PKGCONFIGDIR@')],
			       '%(srcdir)s/Makefile.in')
		self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
				 r'\1${DESTDIR}@PKGCONFIGDIR@')],
			       '%(srcdir)s/Makefile.am')

	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()

	def compile_command (self):

		## need to call twice, first one triggers spurious Automake stuff.		
		return 'cd %(builddir)s && (make  || make)'
class Libpng__mingw (Libpng):
	def configure (self):
		# libtool will not build dll if -no-undefined flag is
		# not present
		self.file_sub ([('-version-info',
				 '-no-undefined -version-info')],
			   '%(srcdir)s/Makefile.am')
		self.autoupdate ()
		Libpng.configure (self)

class OSX_Lilypad (gub.Null_package):
	pass

class Libgnugetopt (targetpackage.Target_package):
	def patch (self):
		self.dump ('''
prefix = /usr
libdir = $(prefix)/lib
includedir = $(prefix)/include
install: all
	install -d $(DESTDIR)/$(libdir)/
	install -m 644 libgnugetopt.so.1 $(DESTDIR)/$(libdir)/
	install -d $(DESTDIR)/$(includedir)/
	install -m 644 getopt.h $(DESTDIR)/$(includedir)/
''',
			   '%(srcdir)s/Makefile', mode='a')

	def configure (self):
		self.shadow_tree ('%(srcdir)s', '%(builddir)s')

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
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2',
					 depends=['darwin-sdk']
					 ),
		Freetype (settings).with (version='2.1.10', mirror=download.nongnu_savannah,
					  format='bz2',
					  depends=['darwin-sdk']),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2',
				       depends=['darwin-sdk']),
		Fontconfig__darwin (settings).with (version='2.3.2', mirror=download.fontconfig,
						    depends=['expat', 'freetype']),
		Glib__darwin (settings).with (version='2.9.1', mirror=download.gnome_213, format='bz2',
					      depends=['darwin-sdk', 'gettext']),
		Pango__darwin (settings).with (version='1.11.1', mirror=download.gnome_213, format='bz2',
					       depends = ['glib', 'fontconfig', 'freetype']
					       ),
		Gmp__darwin (settings).with (version='4.1.4',depends=['darwin-sdk']),
		Fondu__darwin (settings).with (version="051010", mirror=download.hw),
		## 1.7.3  is actually CVS repackaged.
#		Guile (settings).with (version='1.7.3', mirror=download.gnu, format='gz'),
		Guile__darwin (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2',
					       depends=['gmp','darwin-sdk']
					       ),
		Libjpeg__darwin (settings).with (version='v6b', mirror=download.jpeg),
		Libpng (settings).with (version='1.2.8', mirror=download.libpng),
		Ghostscript (settings).with (version="8.15.1", mirror=download.cups,
						     format='bz2', depends=['libjpeg', 'libpng']),
		LilyPond__darwin (settings).with (version=settings.lilypond_branch, mirror=cvs.gnu, track_development=True,
						  depends=['pango', 'guile', 'gettext', 'ghostscript', 'fondu', 'osx-lilypad']
						  ),
		OSX_Lilypad (settings).with (version="0.0", mirror=download.hw, depends=[]),
	),
	'mingw': [
		Regex (settings).with (version='2.3.90-1', mirror=download.lp, format='bz2',
				       depends=['mingw-runtime']),
		LilyPad (settings).with (version='0.0.7-1', mirror=download.lp, format='bz2',
					 depends=['mingw-runtime', 'w32api']),
		Libtool (settings).with (version='1.5.20', depends=['mingw-runtime']),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2',
				      depends=['mingw-runtime']),
		Gettext__mingw (settings).with (version='0.14.5-1', mirror=download.lp, format='bz2',
						depends=['mingw-runtime', 'libtool']),
		Libiconv (settings).with (version='1.9.2',
					  depends=['mingw-runtime', 'gettext']),
		Freetype__mingw (settings).with (version='2.1.10', mirror=download.freetype,
					  depends=['mingw-runtime', 'libtool', 'zlib']),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig__mingw (settings).with (version='2.3.2', mirror=download.fontconfig,
						   depends=['mingw-runtime', 'expat', 'freetype', 'libtool']),
		Gmp__mingw (settings).with (version='4.1.4',
					    depends=['mingw-runtime', 'libtool']),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile__mingw (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2',
					      depends=['mingw-runtime', 'gettext', 'gmp', 'libtool', 'regex']),
		Glib (settings).with (version='2.9.1', mirror=download.gnome_213, format='bz2',
				      depends=['mingw-runtime', 'gettext', 'libiconv']),
		Pango__mingw (settings).with (version='1.11.1', mirror=download.gnome_213, format='bz2',
					      depends=['mingw-runtime', 'freetype', 'fontconfig', 'glib', 'libiconv']),
		Python__mingw (settings).with (version='2.4.2', mirror=download.python, format='bz2',
					       depends=['mingw-runtime']),
		Libjpeg__mingw (settings).with (version='v6b', mirror=download.jpeg,
						depends=['mingw-runtime']),
		Libpng__mingw (settings).with (version='1.2.8', mirror=download.libpng,
					       depends=['mingw-runtime', 'zlib']),
		Ghostscript__mingw (settings).with (version="8.15.1", mirror=download.cups, format='bz2',
						    depends=['mingw-runtime', 'libiconv', 'libjpeg',
							     'libpng','zlib']),
		LilyPond__mingw (settings).with (version=settings.lilypond_branch, mirror=cvs.gnu,
						 depends=['mingw-runtime', 'fontconfig', 'gettext',
							  'guile', 'pango', 'python', 'ghostscript', 'cygwin'],
						 track_development=True),
	],
	'linux': [
		Libtool (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2',
					 depends=['libtool']),
		Freetype__mingw (settings).with (version='2.1.10', mirror=download.nongnu_savannah,
					  depends=['libtool', 'zlib']),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2',
				       depends=['libtool']),
		Fontconfig__linux (settings).with (version='2.3.2', mirror=download.fontconfig,
						   depends=['expat', 'freetype', 'libtool']),
		Gmp (settings).with (version='4.1.4',
				     depends=['libtool']),
		# FIXME: we're actually using 1.7.2-cvs+, 1.7.2 needs too much work
		Guile__linux (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2',
					      depends=['gettext', 'gmp', 'libtool']),
		Glib (settings).with (version='2.9.1', mirror=download.gnome_213, format='bz2',
				      depends=['libtool']),
		Pango__linux (settings).with (version='1.11.1', mirror=download.gnome_213, format='bz2',
					      depends=['freetype', 'fontconfig', 'glib', 'libtool']),
		Python (settings).with (version='2.4.2', mirror=download.python, format='bz2'),
		Libjpeg__linux (settings).with (version='v6b', mirror=download.jpeg),
		Libpng (settings).with (version='1.2.8', mirror=download.libpng,
					depends=['zlib']),
		Ghostscript (settings).with (version="8.15.1", mirror=download.cups, format='bz2',
					     depends=['libjpeg', 'libpng', 'zlib']),
		LilyPond__linux (settings).with (version=settings.lilypond_branch, mirror=cvs.gnu,
						 depends=['fontconfig', 'gettext', 'guile',
							  'ghostscript', 'pango', 'python'],
						 track_development=True),
	],
	'freebsd': [
		Libiconv (settings).with (version='1.9.2',
					  depends=['gettext', 'libtool']),
		Libgnugetopt (settings).with (version='1.3', format='bz2', mirror=download.freebsd_ports,
					      depends=[]),
		Glib__freebsd (settings).with (version='2.9.1', mirror=download.gnome_213, format='bz2',
				      depends=['libtool']),
		Gettext__freebsd (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2',
						  depends=['libtool', 'libgnugetopt']),
		Guile__freebsd (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2',
						depends=['gettext', 'gmp', 'libtool',]),
		Python__freebsd (settings).with (version='2.4.2', mirror=download.python, format='bz2',
					       depends=[]),
	],
	'local': [],
	'debian': [
		LilyPond__linux (settings).with (version=settings.lilypond_branch, mirror=cvs.gnu,
						 builddeps=['libfontconfig1-dev', 'guile-1.6-dev', 'libpango1.0-dev', 'python-dev'],
						 track_development=True),
		],
	'cygwin': [
		LilyPond__cygwin (settings).with (version=settings.lilypond_branch, mirror=cvs.gnu,
						  depends=['python'],
						  builddeps=['gcc', 'gettext-devel', 'guile-devel', 'pango-devel'],
						  track_development=True),
		]
	}

	packs = packages[settings.platform]

	## UGH UGH  platform dependent.
	# FreeBSD almost uses linux packages...
	if settings.platform.startswith ('freebsd'):
		linux_packs = packages['linux']

		have_already = [p.name() for p in packs]
		for i in linux_packs:
			#URG
			if i.name () in have_already:
				continue
			
                        if not i.name () in ('binutils', 'gcc'):
				i.name_dependencies += ['freebsd-runtime']
			if i.name () in ('ghostscript', 'glib', 'pango'):
				i.name_dependencies += ['libiconv']
			packs += [i]

	for p in packs:
		if p.name () == 'lilypond':
			p._downloader = p.cvs


	try:
		settings.python_version = [p for p in packs
					   if isinstance (p, Python)][0].python_version ()
	except IndexError:
		if settings.platform == 'cygwin':
			settings.python_version = '2.4'
		elif settings.platform == 'darwin':
			settings.python_version = '2.3'
		elif settings.platform == 'debian':
			settings.python_version = '2.3'
	try:
		settings.guile_version = [p for p in packs
			if isinstance (p, Guile)][0].guile_version ()
	except IndexError:
		if settings.platform == 'debian':
			settings.guile_version = '1.6'
	try:
		settings.ghostscript_version = [p for p in packs
			if isinstance (p, Ghostscript)][0].ghostscript_version ()
	except IndexError:
		if settings.platform == 'cygwin':
			settings.ghostscript_version = '8.15'
		elif settings.platform == 'debian':
			settings.ghostscript_version = '8.15'
	return packs
