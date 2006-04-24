import glob
import os
import re
import shutil

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
		self.autoupdate ()

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
		self.system ('mkdir -p %(install_root)s/usr/etc/relocate/')

		majmin_version = '.'.join (self.expand ('%(version)s').split ('.')[0:2])
		
		self.dump ("prependdir GUILE_LOAD_PATH=$INSTALLER_ROOT/usr/share/guile/%(majmin_version)s\n",
			   '%(install_root)s/usr/etc/relocate/guile.reloc',
			   env=locals())
		
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

	
   
class Guile__darwin__x86 (Guile__darwin):
	def configure (self):
		Guile__darwin.configure (self)
		self.file_sub ([('guile-readline', '')],
			       '%(builddir)s/Makefile')
		
		
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

		# FIXME: Must disable when building guile for lilypond,
		# must enable for building guile (installer) for cygwin,
		# so cannot simply use cmdline --split switch.
		self.sover = '17'
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

	def copy_readmes (self):
		self.system ('''
mkdir -p %(install_root)s/usr/share/doc/%(name)s
''')
		for i in glob.glob ('%(srcdir)s/[A-Z]*'
				    % self.get_substitution_dict ()):
			if (os.path.isfile (i)
			    and not i.startswith ('Makefile')
			    and not i.startswith ('GNUmakefile')):
				shutil.copy2 (i, '%(install_root)s/usr/share/doc/%(name)s' % self.get_substitution_dict ())

	def patch (self):
		pass

	def install (self):
		Guile.install (self)
		self.dump_readme_and_hints ()
		self.copy_readmes ()
		# Hmm, is this really necessary?
		cygwin_patches = '%(srcdir)s/CYGWIN-PATCHES'
		self.system ('''
mkdir -p %(cygwin_patches)s
cp -pv %(install_root)s/etc/hints/* %(cygwin_patches)s
cp -pv %(install_root)s/usr/share/doc/Cygwin/* %(cygwin_patches)s
''',
			     locals ())

	# FIXME: ints and readmes from file, rather than inline python data.
	def dump_readme_and_hints (self):
		# FIXME: get depends from actual split_packages
		changelog = open (self.settings.sourcefiledir + '/guile.changelog').read ()
		self.system ('''
mkdir -p %(install_root)s/usr/share/doc/Cygwin
mkdir -p %(install_root)s/etc/hints
''')
		readme = open (self.settings.sourcefiledir + '/guile.README').read ()

		self.dump (readme,
			   '%(install_root)s/usr/share/doc/Cygwin/%(name)s-%(version)s-%(bundle_build)s.README',
			   env=locals ())


		fixdepends = {
			'guile': ['cygwin', 'libguile17', 'libncurses8', 'libreadline6'],
			'guile-devel': ['bash', 'cygwin', 'guile', 'libguile17'],
			'guile-doc':  ['texinfo'],
			'libguile17': ['cygwin', 'crypt', 'gmp', 'libintl3', 'libltdl3'],
			}
		##for name in [self.name ()] + self.split_packages:
		## FIXME split-names
		for name in ['guile', 'guile-devel', 'guile-doc', 'libguile' + self.sover]:
			depends = fixdepends[name]
			requires = ' '.join (depends)
			hint = self.expand (open (self.settings.sourcefiledir + '/' + name + '.hint').read (), locals ())
			self.dump (hint,
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
		self.set_mirror ()
		self.name_build_dependencies = ['gmp', 'libtool']
		self.name_dependencies = ['gmp']
