# own
import cpm
import cross
import cvs
import download
import glob
import buildnumber


# sys
import pickle
import os
import re
import string
import subprocess
import sys
import time

from context import *

def grok_sh_variables (file):
	dict = {}
	for i in open (file).readlines ():
		m = re.search ('^(\w+)\s*=\s*(\w*)', i)
		if m:
			k = m.group (1)
			s = m.group (2)
			dict[k] = s
	return dict

def split_version (s):
	m = re.match ('^(([0-9].*)-([0-9]+))$', s)
	if m:
		return m.group (2), m.group (3)
	return s, '0'

def join_lines (str):
	return re.sub ('\n', ' ', str)

class Package (Os_context_wrapper):
	def __init__ (self, settings):
		Os_context_wrapper.__init__(self, settings)

		self.verbose = settings.verbose()
		self.settings = settings
		self.url = ''
		self._downloader = self.wget
		self._build = 0

		# set to true for CVS releases 
		self.track_development = False


	# fixme: rename download.py to mirrors.py
	def do_download (self):
		self._downloader()
		

	def skip (self):
		pass

	def wget (self):
		dir = self.settings.downloaddir
		url = self.expand (self.url)
		name = self.expand (dir + '/' + self.file_name ())
		if not os.path.exists (name):
			self.system ('''
cd %(dir)s && wget %(url)s
''', locals ())

	def cvs (self):
		dir = self.settings.allsrcdir
		url = self.expand (self.url)
		if not os.path.exists (os.path.join (dir, self.name ())):
			self.system ('''
cd %(dir)s && cvs -d %(url)s -q co -r %(version)s %(name)s
''', locals ())
		else:
# Hmm, let's save local changes?			
#cd %(dir)s/%(name)s && cvs update -dCAP -r %(version)s
			self.system ('''
cd %(dir)s/%(name)s && cvs -q update -dAP -r %(version)s
''', locals ())
		self.untar = self.skip

	@subst_method
	def build (self):
		return '%d' % self._build

	@subst_method
	def name (self):
		file = self.__class__.__name__.lower ()
		file = re.sub ('__.*', '', file)
		file = re.sub ('_', '-', file)
		return file


	@subst_method
	def file_name(self):
		file = re.sub ('.*/([^/]+)', '\\1', self.url)
		file = file.lower ()
		return file

	@subst_method
	def basename (self):
                f = self.file_name ()
                f = re.sub ('.tgz', '', f)
                f = re.sub ('-src\.tar.*', '', f)
                f = re.sub ('\.tar.*', '', f)
                return f
	
	@subst_method
	def full_version (self):
		return string.join ([self.version (), self.build ()], '-')

	@subst_method
	def version (self):
		return split_version (self.ball_version)[0]

	@subst_method
	def name_version (self):
		return '%s-%s' % (self.name (), self.version ())

	@subst_method
	def srcdir (self):
		return self.settings.allsrcdir + '/' + self.basename ()

	@subst_method
	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	@subst_method
	def install_root (self):
		return self.settings.installdir + "/" + self.name () + '-root'

	@subst_method
	def install_prefix (self):
		return self.install_root () + '/usr'

	@subst_method
        def install_command (self):
                return 'make install'

	@subst_method
	def configure_command (self):
		return '%(srcdir)s/configure --prefix=%(install_prefix)s'

	@subst_method
	def compile_command (self):
		return 'make'

	@subst_method
        def gub_name (self):
		return '%(name)s-%(version)s-%(build)s.%(platform)s.gub'

	def get_builds  (self):
		return builds
	
	def set_current_build (self):
		bs = self.get_builds ()
		bs.sort()
		if bs:
			self._build = bs[-1] + 1
		else:
			self._build = 1

	def stamp_file (self):
		return self.expand ('%(statusdir)s/%(name)s-%(version)s-%(build)s')

	def is_done (self, stage, stage_number):
		f = self.stamp_file ()
		if os.path.exists (f):
			return pickle.load (open (f)) >= stage_number
		return False

	def set_done (self, stage, stage_number):
		pickle.dump (stage_number, open (self.stamp_file (),'w'))

	def autoupdate (self, autodir=0):
		if not autodir:
			autodir = self.srcdir ()
		if os.path.isdir (os.path.join (self.srcdir (), 'ltdl')):
			self.system ('''
rm -rf %(autodir)s/libltdl
cd %(autodir)s && libtoolize --force --copy --automake --ltdl
''', locals ())
		else:
			self.system ('''
cd %(autodir)s && libtoolize --force --copy --automake
''', locals ())
		if os.path.exists (os.path.join (autodir, 'bootstrap')):
			self.system ('''
cd %(autodir)s && ./bootstrap
''', locals ())
		elif os.path.exists (os.path.join (autodir, 'autogen.sh')):
			self.system ('''
cd %(autodir)s && bash autogen.sh --noconfigure
''', locals ())
		else:
			self.system ('''
cd %(autodir)s && aclocal
cd %(autodir)s && autoheader
cd %(autodir)s && autoconf
''', locals ())
			if os.path.exists (os.path.join (self.srcdir (), 'Makefile.am')):
				self.system ('''
cd %(srcdir)s && automake --add-missing
''', locals ())

	def config_cache_overrides (self, str):
		return str

	def config_cache_settings (self):
		return self.config_cache_overrides (self, '')

	def config_cache (self):
		str = self.config_cache_settings ()
		if str:
			self.system ('mkdir -p %(builddir)s')
			cache_file = '%(builddir)s/config.cache'
			self.dump (self.config_cache_settings (), cache_file)
			os.chmod (self.expand (cache_file), 0755)

	def configure (self):
		self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

	def install (self):
		self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
''')
		self.libtool_la_fixups ()

	def libtool_la_fixups (self):
		dll_name = 'lib'
		for i in glob.glob ('%(install_prefix)s/lib/*.la' \
				    % self.get_substitution_dict ()):
			base = os.path.basename (i)[3:-3]
			self.file_sub ([
				(''' *-L *[^"' ][^"' ]*''', ''),
				('''( |=|')(/[^ ]*usr/lib/lib)([^ ']*)\.(a|la|so)[^ ']*''', '\\1-l\\3'),
				('^old_library=.*',
				"""old_library='lib%(base)s.a'"""),
				],
				i, env=locals ())
                        if self.settings.platform.startswith ('mingw'):
			         self.file_sub ([('library_names=.*',
						"library_names='lib%(base)s.dll.a'")],
						i, env=locals ())
			#  ' " ''' '

			# FIXME: avoid using libs from /usr/lib when
			# building linux package.

			# Actually, this check should be something like
			# if build_arch == target_arch:
			# rather than if linux:

			# Move this to xpm.py, and only do this after
			# installing?  But how does xpm know whether
			# we do a native install, as system install
			# or an installer install.
                        if self.settings.platform.startswith ('linux'):
				self.file_sub ([
				('^libdir=.*',
				"""libdir='%(system_root)s/usr/lib'"""),
				],
					       i, env=locals ())


	## Platform check sucks. Let's move this into the installer  classes.


	def compile (self):
		self.system ('cd %(builddir)s && %(compile_command)s')

	def patch (self):
		if not os.path.exists ('%(srcdir)s/configure' \
				       % self.get_substitution_dict ()):
			self.autoupdate ()

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(install_root)s -zcf %(gub_uploads)s/%(gub_name)s .
''')

	def clean (self):
		stamp = self.stamp_file ()
		self.system ('rm -rf  %(stamp)s %(install_root)s', locals ())
		if self.track_development:
			return

		self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

	def untar (self):
		if self.track_development:
			return
		
		tarball = self.expand("%(downloaddir)s/%(file_name)s")
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		flags = download.untar_flags (tarball)
		
		# clean up
		self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
tar %(flags)s %(tarball)s -C %(allsrcdir)s
''',
			     locals ())

	def with (self, version='HEAD', mirror=download.gnu,
		  format='gz', download=wget, depends=[],
		  track_development=False
		  ):
		self.format = format
		self.ball_version = version
		ball_version = version
		self.name_dependencies = depends
		self.track_development = track_development
		self.url = mirror

		## don't do substitution. We want to postpone
		## generating the dict until we're sure it doesn't change. 

		return self

class Cross_package (Package):
	"""Package for cross compilers/linkers etc.
	"""

	def configure_command (self):
		return (Package.configure_command (self)
			+ join_lines ('''
--target=%(target_architecture)s
--with-sysroot=%(system_root)s/
'''))

        def xgub_name (self):
		## makes build number handling more complicated.
		return '%(name)s-%(version)s-%(build)s.%(build_architecture)s-%(target_architecture)s.gub'

	def install_command (self):
		# FIXME: to install this, must revert any prefix=tooldir stuff
		return join_lines ('''make prefix=/usr DESTDIR=%(install_root)s install''')

	def package (self):
		# naive tarball packages for now
		# cross packages must not have ./usr because of tooldir
		self.system ('''
tar -C %(install_root)s/usr -zcf %(gub_uploads)s/%(gub_name)s .
''')

class Target_package (Package):
	def configure_command (self):
		return join_lines ('''%(srcdir)s/configure
--config-cache
--enable-shared
--disable-static
--build=%(build_architecture)s
--host=%(target_architecture)s
--target=%(target_architecture)s
--prefix=/usr
--sysconfdir=/usr/etc
--includedir=/usr/include
--libdir=/usr/lib
''')

	def broken_install_command (self):
		"""For packages that do not honor DESTDIR.
		"""

		# FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
		# so, must also ./configure that way
		return join_lines ('''make install
bindir=%(install_prefix)s/bin
aclocaldir=%(install_prefix)s/share/aclocal
datadir=%(install_prefix)s/share
exec_prefix=%(install_prefix)s
gcc_tooldir=%(install_prefix)s
includedir=%(install_prefix)s/include
infodir=%(install_prefix)s/share/info
libdir=%(install_prefix)s/lib
libexecdir=%(install_prefix)s/lib
mandir=%(install_prefix)s/share/man
prefix=%(install_prefix)s
sysconfdir=%(install_prefix)s/etc
tooldir=%(install_prefix)s
''')

	def install_command (self):
		return join_lines ('''make DESTDIR=%(install_root)s install''')

	def config_cache_settings (self):
		return self.config_cache_overrides (
			cross.cross_config_cache['all']
			+ cross.cross_config_cache[self.settings.platform])

	def configure (self):
		self.config_cache ()
		Package.configure (self)

	## FIXME: this should move elsewhere , as it's not
	## package specific 
	def target_dict (self, env={}):
		dict = {
			'AR': '%(tool_prefix)sar',
			'CC': '%(tool_prefix)sgcc %(target_gcc_flags)s',
#			'CPPFLAGS': '-I%(system_root)s/usr/include',
			'C_INCLUDE_PATH':' %(system_root)s/usr/include',
			'CXX':'%(tool_prefix)sg++ %(target_gcc_flags)s',

			'FREETYPE_CONFIG': '''%(system_root)s/usr/bin/freetype-config \
--prefix=%(system_root)s/usr \
''',
#--urg-broken-if-set-exec-prefix=%(system_root)s/usr \
			'LD': '%(tool_prefix)sld',
			'NM': '%(tool_prefix)snm',
			'PKG_CONFIG_PATH': '%(system_root)s/usr/lib/pkgconfig',
			'PKG_CONFIG': '''/usr/bin/pkg-config \
--define-variable prefix=%(system_root)s/usr \
--define-variable includedir=%(system_root)s/usr/include \
--define-variable libdir=%(system_root)s/usr/lib \
''',
			'RANLIB': '%(tool_prefix)sranlib',
			'SED': 'sed', # libtool (expat mingw) fixup
			}
		dict.update (env)
		return dict

	def dump (self, str, name, mode='w', env={}):
		dict = self.target_dict (env)
		return Package.dump (self, str, name, mode=mode, env=dict)

	def file_sub (self, re_pairs, name, to_name=None, env={}):
		dict = self.target_dict (env)

		s = Package.file_sub (self, re_pairs, name, to_name=to_name, env=dict)
		return s

	def read_pipe (self, cmd, env={}, ignore_error=False):
		dict = self.target_dict (env)
		return Package.read_pipe (self, cmd, env=dict, ignore_error=ignore_error)

	def system (self, cmd, env={}, ignore_error=False):
		dict = self.target_dict (env)
		Package.system (self, cmd, env=dict, ignore_error=ignore_error)

class Binary_package (Package):
	def untar (self):
		self.system ('rm -rf %(srcdir)s %(builddir)s %(install_root)s')
		self.system ('mkdir -p %(srcdir)s/root')
		tarball = self.expand ('%(downloaddir)s/%(file_name)s')
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		flags = download.untar_flags (tarball)
		
		self.system ('tar %(flags)s %(tarball)s -C %(srcdir)s/root', locals ())

	def configure (self):
		pass

	def patch (self):
		pass

	def compile (self):
		pass

	def install (self):
		self.system ('mkdir -p %(install_root)s')
		self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s -xvf-')


class Null_package (Package):
	"""Placeholder for downloads """
	def compile (self):
		pass
	def configure (self):
		pass
	def install (self):
		pass
	def untar (self):
		pass
	def patch (self):
		pass
	def package (self):
		self.system ("tar -czf %(gub_uploads)s/%(gub_name)s --files-from=/dev/null")
		
class Sdk_package (Null_package):
	def untar (self):
		Package.untar (self)
	def package (self):
		self.system ('tar -C %(srcdir)s/ -czf %(gub_uploads)s/%(gub_name)s .')

class Change_target_dict:
	def __init__ (self, package, override):
		self._target_dict_method = package.target_dict
		self._add_dict = override
		
	def target_dict (self, env={}):
		d = self._target_dict_method (env)
		d.update (self._add_dict)
		return d

def change_target_dict (package, addict):
	"""Override the target_dict() method of PACKAGE."""
	try:
		package.target_dict = Change_target_dict(package, addict).target_dict
	except AttributeError:
		pass
