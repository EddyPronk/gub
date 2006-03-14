import glob
import os
import re

import download
import misc
import targetpackage
from toolpackage import Tool_package


class Guile (targetpackage.Target_package):
	def set_mirror(self):
		self.with (version='1.8.0',
			   mirror=download.gnu, format='gz',
			   depends=['gettext', 'gmp', 'libtool'])
		
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.set_mirror ()

	# FIXME: C&P.
	def guile_version (self):
		return '.'.join (self.ball_version.split ('.')[0:2])

	def patch (self):
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/guile-reloc.patch')
		self.autoupdate()

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
	def compile (self):

		## Ugh : broken dependencies barf with make -jX
		self.system ('cd %(builddir)s/libguile && make scmconfig.h ')
		targetpackage.Target_package.compile (self)

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
		# Configure (compile) without -mwindows for console
		self.target_gcc_flags = '-mms-bitfields'
		self.name_dependencies.append ('regex')

# FIXME: ugh, C&P to Guile__freebsd, put in cross-Guile?
	def configure_command (self):
		# watch out for whitespace
		builddir = self.builddir ()
		srcdir = self.srcdir ()


# don't set PATH_SEPARATOR; it will fuckup tool searching for the
# build platform.

		return (Guile.configure_command (self)
		       + misc.join_lines ('''
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

		if 1:
			self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''',
					 '\\1')],
				       '%(srcdir)s/configure')


		Guile.configure (self)



		## probably not necessary, but just be sure.
		for l in self.locate_files ('%(builddir)s', "Makefile"):
			self.file_sub ([
				('PATH_SEPARATOR = .', 'PATH_SEPARATOR = ;'),
				], '%(builddir)s/' + l)

		self.file_sub ([
			#('^(allow_undefined_flag=.*)unsupported', '\\1'),
			('-mwindows', ''),
			],
			       '%(builddir)s/libtool')
		self.file_sub ([
			#('^(allow_undefined_flag=.*)unsupported', '\\1'),
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
		return ('export LD_LIBRARY_PATH=%(builddir)s/libguile/.libs:$LD_LIBRARY_PATH;'
			+ Guile.compile_command (self))

class Guile__freebsd (Guile):
	def config_cache_settings (self):
		return Guile.config_cache_settings (self) + '\nac_cv_type_socklen_t=yes'

	def configure_command (self):
		# watch out for whitespace
		builddir = self.builddir ()
		srcdir = self.srcdir ()
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

class Guile__cygwin (Guile):
	def __init__ (self, settings):
		Guile.__init__ (self, settings)

		# Cygwin's libintl.la uses libiconv.la from libiconv
		# (which uses libiconv2, but libintl depends on that).
		# So, Cygwin's guile build depends on libiconv.
		self.with (version='1.8.0',
			   mirror=download.gnu, format='gz',
			   depends=['gettext', 'gmp', 'libtool'],
			   builddeps=['libiconv'])

		# FIXME: WIP.  splitting works, xpm can't handle split
		# packages yet, xpm will try to load FOO.py for
		# every split package FOO, eg: libguile17.py.

		# Disable for now.
		#self.sover = '17'
		#self.split_packages = ['devel', 'doc', 'lib']

	def config_cache_overrides (self, str):
		return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_root)s/usr/lib"}
'''

	def configure (self):
		if 1:
			self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''',
					 '\\1')],
				       '%(srcdir)s/configure')

		Guile.configure (self)

		## probably not necessary, but just be sure.
		for i in self.locate_files ('%(builddir)s', "Makefile"):
			self.file_sub ([
				('PATH_SEPARATOR = .', 'PATH_SEPARATOR = ;'),
				], '%(builddir)s/' + i)

		self.file_sub ([
			('^(allow_undefined_flag=.*)unsupported', '\\1'),
			],
			       '%(builddir)s/libtool')
		self.file_sub ([
			('^(allow_undefined_flag=.*)unsupported', '\\1'),
			],
			       '%(builddir)s/guile-readline/libtool')

	def install (self):
		Guile.install (self)
		self.dump_readme_and_hints ()

	def dump_readme_and_hints (self):
		# FIXME: get depends from actual split_packages
		changelog = open (self.settings.specdir + '/guile.changelog').read ()
		self.system ('''
mkdir -p %(install_root)s/usr/share/doc/Cygwin
mkdir -p %(install_root)s/etc/hints
''')

		self.dump ('''\
Guile
------------------------------------------
The GNU extension language and Scheme interpreter.

Runtime requirements (these or newer):
  crypt-1.1-1
  cygwin-1.5.18
  gmp-4.1.4
  libguile17-1.8.0-0
  libintl-0.10.38
  libltdl3-1.5.20

Build requirements (these or newer):
  autoconf-2.53a-1
  autoconf-devel-2.53a-1
  automake-1.6.1-3
  automake-devel-1.6.1-3
  binutils-20050610-1
  cygwin-1.5.18
  gcc-3.4.4-1
  gmp-4.1.4
  libtool-devel-1.5.20-1

Canonical homepage:
  http://www.gnu.org/software/guile

Canonical download:
  ftp://alpha.gnu.org/pub/gnu/guile  # development releases
  ftp://ftp.gnu.org/pub/gnu/guile    # stable releases

License:
  LGPL

Language:
  C, Scheme

------------------------------------

Build Instructions:

  # Download GUB

    darcs get http://lilypond.org/people/hanwen/gub
    cd gub

  # Build guile for cygwin

    ./gub-builder.py -p cygwin build guile

  # Package guile for cygwin

   ./gub-builder.py -p cygwin package-installer guile

This will create:
   uploads/cygwin/release/guile-%(version)s-%(bundle_build)s-src.tar.bz2
   uploads/cygwin/release/guile-%(version)s-%(bundle_build)s.tar.bz2
   uploads/cygwin/release/guile-doc/guile-doc-%(version)s-%(bundle_build)s.tar.bz2
   uploads/cygwin/release/guile-devel/guile-devel-%(version)s-%(bundle_build)s.tar.bz2
   uploads/cygwin/release/libguile%(sover)s/libguile%(sover)s-%(version)s-%(bundle_build)s.tar.bz2

To find out the files included in the binary distribution, you can use
"cygcheck -l bash", or browse the listing for the appropriate version
at <http://cygwin.com/packages/>.

------------------

Port notes:

%(changelog)s

  These packages were built on GNU/Linux using GUB.

Cygwin port maintained by: Jan Nieuwenhuizen  <janneke@gnu.org>
Please address all questions to the Cygwin mailing list at <cygwin@cygwin.com>
''',
# "
			   '%(install_root)s/usr/share/doc/Cygwin/%(name)s-%(version)s-%(bundle_build)s.README',
			   env=locals ())

		name = 'guile'
		depends = ['cygwin', 'libguile12', 'libguile17', 'libncurses8', 'libreadline6']
		requires = ' '.join (depends)
		self.dump ('''\
curr: %(version)s-%(bundle_build)s
prev: 1.6.7-3
sdesc: "The GNU extension language and Scheme interpreter (executable)"
category: interpreters
# Strictly, guile does not depend on readline and curses, but if you
# want the guile executable, you probably want readline editing.  -- jcn
requires: %(requires)s
ldesc: "The GNU extension language and Scheme interpreter (executable)
Guile, the GNU Ubiquitous Intelligent Language for Extension, is a scheme
implementation designed for real world programming, supporting a
rich Unix interface, a module system, and undergoing rapid development.

`guile' is a scheme interpreter that can execute scheme scripts (with a
#! line at the top of the file), or run as an inferior scheme
process inside Emacs."
''',
# "`
			   '%(install_root)s/etc/hints/%(name)s.hint',
			   env=locals ())

		name = 'guile-devel'
		depends = ['bash', 'cygwin', 'guile', 'libguile12', 'libguile17']
		requires = ' '.join (depends)
		self.dump ('''\
curr: %(version)s-%(bundle_build)s
prev: 1.6.7-3
sdesc: "Development headers and static libraries for Guile."
category: devel libs
requires: %(requires)s
external-source: guile
ldesc: "Development headers and static libraries for Guile.
`libguile.h' etc. C headers, aclocal macros, the `guile-snarf' and
`guile-config' utilities, and static `libguile.a' libraries for Guile,
the GNU Ubiquitous Intelligent Language for Extension."

''',
# "`
			   '%(install_root)s/etc/hints/%(name)s.hint',
			   env=locals ())

		name = 'guile-doc'
		depends = ['texinfo']
		requires = ' '.join (depends)
		self.dump ('''\
curr: %(version)s-%(bundle_build)s
prev: 1.6.7-3
sdesc: "The GNU extension language and Scheme interpreter (documentation)"
category: doc
requires: %(requires)s
external-source: guile
ldesc: "The GNU extension language and Scheme interpreter (documentation)
This package contains the documentation for guile, including both
a reference manual (via `info guile'), and a tutorial (via `info
guile-tut')."

''',
# "`
			   '%(install_root)s/etc/hints/%(name)s.hint',
			   env=locals ())

		name = 'libguile17'
		depends = ['cygwin', 'crypt', 'gmp', 'libintl3', 'libltdl3']
		requires = ' '.join (depends)
		self.dump ('''\
curr: %(version)s-%(bundle_build)s
#prev: 1.6.7-3
sdesc: "The GNU extension language and Scheme interpreter (runtime libraries)"
category: libs
requires: %(requires)s
external-source: guile
ldesc: "The GNU extension language and Scheme interpreter (runtime libraries)
Guile shared object libraries and the ice-9 scheme module.  Guile is
the GNU Ubiquitous Intelligent Language for Extension."

''',
# "
			   '%(install_root)s/etc/hints/%(name)s.hint',
			   env=locals ())

class Guile__local (Tool_package, Guile):
	def configure (self):
		Tool_package.configure (self)
		self.update_libtool ()
	def install (self):
		Tool_package.install (self)

		## don't want local GUILE headers to interfere with compile.
		self.system ("rm -rf %(install_root)s/usr/include/ %(install_root)s/usr/bin/guile-config ")

	def __init__ (self, settings):
		Tool_package.__init__ (self, settings)
		self.set_mirror()
		self.name_build_dependencies = ['gmp', 'libtool']
		self.name_dependencies = ['gmp']
