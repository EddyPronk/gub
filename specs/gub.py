import cpm
import cross
import cvs
import download
import glob

import os
import re
import subprocess
import sys
import time



log_file = None

def now ():
	return time.asctime (time.localtime ())

def start_log (settings):
	global log_file
	log_file = open ('build-%s.log' % settings.target_architecture, 'a')
	log_file.write ('\n\n * Starting build: %s\n' %  now ())

def log_command (str):
	sys.stderr.write (str)
	if log_file:
		log_file.write (str)
		log_file.flush ()

def system_one (cmd, env, ignore_error):
	log_command ('invoking %s\n' % cmd)
	
	proc = subprocess.Popen (cmd, shell=True, env=env,
				 stderr=subprocess.STDOUT)
	stat = proc.wait ()

	if stat and not ignore_error:
		m = 'Command barfed: %s\n' % cmd
		log_command (m)
		raise m

	return 0

def join_lines (str):
	return re.sub ('\n', ' ', str)

def system (cmd, env={}, ignore_error=False, verbose=False):
	"""Run multiple lines as multiple commands.
	"""

	call_env = os.environ.copy ()
	call_env.update (env)

	if verbose:
		for (k, v) in env.items ():
			sys.stderr.write ('%s=%s\n' % (k, v))

	for i in cmd.split ('\n'):
		if i:
			system_one (i, call_env, ignore_error)

	return 0

def dump (str, name, mode='w'):
	f = open (name, mode)
	f.write (str)
	f.close ()

def file_sub (re_pairs, name, to_name=None):
	log_command ('substituting: %s' %
		     ''.join (map (lambda x: "'%s' -> '%s'\n" % x,
				     re_pairs)))
	
	s = open (name).read ()
	t = s
	for frm, to in re_pairs:
		t = re.sub (re.compile (frm, re.MULTILINE), to, t)
	if s != t or (to_name and name != to_name):
		if not to_name:
			system ('mv %(name)s %(name)s~' % locals ())
			to_name = name
		h = open (to_name, 'w')
		h.write (t)
		h.close ()

def read_pipe (cmd, ignore_error=False):
	log_command ('Reading pipe: %s\n' % cmd)
	
	pipe = os.popen (cmd, 'r')
	output = pipe.read ()
	status = pipe.close ()
	# successful pipe close returns None
	if not ignore_error and status:
		raise 'read_pipe failed'
	return output





class Package:
	system_gpm = cpm.Gpm ('ugh')
	def __init__ (self, settings):
		if self.system_gpm.root == 'ugh':
			self.system_gpm.__init__ (settings.system_root)
			self.system_gpm.setup ()
			self.system_gpm.installed ()
		self.settings = settings
		self.url = ''
		self.download = self.wget

	def package_dict (self, env={}):
		dict = self.settings.get_substitution_dict ()
		for (k, v) in self.__dict__.items():
			if type (v) <> type (''):
				continue
			dict[k] = v

		dict.update({
			'build': self.build (),
			'builddir': self.builddir (),
			'compile_command': self.compile_command (),
			'configure_command': self.configure_command (),
			'gub_name': self.gub_name (),
			'install_command': self.install_command (),
			'install_prefix': self.install_prefix (),
			'install_root': self.install_root (),
			'name': self.name (),
			'srcdir': self.srcdir (),
			'version': self.version (),
			})

		dict.update (env)
		for (k, v) in dict.items ():
			del dict[k]
			if type (v) == type (''):
				try:
					v = v % dict
					dict[k] = v
				except KeyError:
					pass

		return dict

	def dump (self, str, name, mode='w', env={}):
		dict = self.package_dict (env)
		return dump (str % dict, name % dict, mode=mode)

	def file_sub (self, re_pairs, name, to_name=None, env={}):
		dict = self.package_dict (env)
		x = []
		for frm, to in re_pairs:
			x += [(frm % dict, to % dict)]
		if to_name:
			to_name = to_name % dict
		return file_sub (x, name % dict, to_name)

	def read_pipe (self, cmd, env={}, ignore_error=False):
		dict = self.package_dict (env)
		return read_pipe (cmd % dict, ignore_error=ignore_error)

	def system (self, cmd, env={}, ignore_error=False):
		dict = self.package_dict (env)
		system (cmd % dict, env=dict, ignore_error=ignore_error,
			verbose=self.settings.verbose)

	def skip (self):
		pass

	def wget (self):
		dir = self.settings.downloaddir
		if not os.path.exists (dir + '/' + self.file_name ()):
			self.system ('''
cd %(dir)s && wget %(url)s
''', locals ())

	def cvs (self):
		dir = self.settings.allsrcdir
		if not os.path.exists (os.path.join (dir, self.name ())):
			self.system ('''
cd %(dir)s && cvs -d %(url)s -q co -r %(version)s %(name)s
''', locals ())
		else:
# Hmm, let's save local changes?			
#cd %(dir)s/%(name)s && cvs update -dCAP -r %(version)s
			self.system ('''
cd %(dir)s/%(name)s && cvs -q update  -dAP -r %(version)s
''', locals ())
		self.untar = self.skip

	def file_name (self):
		## hmm. we could use Class._name as a data member.
		##
		if self.url:
			file = re.sub ('.*/([^/]+)', '\\1', self.url)
			file = file.lower ()
		else:
			file = self.__class__.__name__.lower ()
			file = re.sub ('__.*', '', file)
			file = re.sub ('_', '-', file)
		return file

	def basename (self):
		f = self.file_name ()
		f = re.sub ('.tgz', '', f)
		f = re.sub ('-src\.tar.*', '', f)
		f = re.sub ('\.tar.*', '', f)
		return f

	def name (self):
		s = self.basename ()
		s = re.sub ('-[0-9][^-]+(-[0-9]+)?$', '', s)
		return s

	def version (self):
		return cpm.split_version (self.ball_version)[0]

	def build (self):
		return cpm.split_version (self.ball_version)[-1]

	def srcdir (self):
		return self.settings.allsrcdir + '/' + self.basename ()

	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	def install_root (self):
		return self.settings.installdir + "/" + self.name () + '-root'

	def install_prefix (self):
		return self.install_root () + '/usr'

	def done (self, stage):
		return ('%(statusdir)s/%(name)s-%(version)s-%(build)s-%(stage)s'
			% self.package_dict (locals ()))
	
	def is_done (self, stage):
		return os.path.exists (self.done (stage))

	def set_done (self, stage):
		open (self.done (stage), 'w').write ('')

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

	def configure_command (self):
		return '%(srcdir)s/configure --prefix=%(install_prefix)s'

	def configure (self):
		if self.system_gpm.installed ().has_key (self.name ()):
			self.system_gpm.uninstall (self.name ())
		self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

	def install_command (self):
		return 'make install'

	def install (self):
		self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
''')
		self.libtool_la_fixups ()

	def libtool_la_fixups (self):
		dll_name = 'lib'
		for i in glob.glob ('%(install_prefix)s/lib/*.la' \
				    % self.package_dict ()):
			base = os.path.basename (i)[3:-3]
			self.file_sub ([
				(''' *-L *[^"' ][^"' ]*''', ''),
				('''( |=|')(/[^ ]*usr/lib/lib)([^ ']*)\.(a|la|so)[^ ']*''', '\\1-l\\3'),
				('^old_library=.*',
				"""old_library='lib%(base)s.a'""")],
				       i, env=locals ())
                        if self.settings.platform.startswith ('mingw'):
			         self.file_sub ([('library_names=.*',
						"library_names='lib%(base)s.dll.a'")],
						i, env=locals ())
			#  ' " ''' '


	## Platform check sucks. Let's move this into the installer  classes.

	def compile_command (self):
		return 'make'

	def compile (self):
		self.system ('cd %(builddir)s && %(compile_command)s')

	def patch (self):
		if not os.path.exists ('%(srcdir)s/configure' \
				       % self.package_dict ()):
			self.autoupdate ()

        def gub_name (self):
		return '%(name)s-%(version)s-%(build)s.%(platform)s.gub'

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(install_root)s -zcf %(gub_uploads)s/%(gub_name)s .
''')

	def _install_gub (self, root):
		self.system ('''
mkdir -p %(root)s
tar -C %(root)s -zxf %(gub_uploads)s/%(gub_name)s
''', locals ())

	def install_gub (self):
		self._install_gub (self.settings.installer_root)

	def sysinstall (self):
		self.system_gpm.install (self.name (),
					 '%(gub_uploads)s/%(gub_name)s' \
					 % self.package_dict (),
					 depends=self.depends)
		self.system_gpm.write_setup_ini ('%(uploads)s/setup.ini' \
						% self.package_dict ())
		self.system ('''
cp -pv %(uploads)s/setup.ini %(system_root)s/etc/setup/
''')

	def untar (self):
		tarball = self.settings.downloaddir + '/' + self.file_name ()
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		flags = download.untar_flags (tarball)
		# clean up
		self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
tar %(flags)s %(tarball)s -C %(allsrcdir)s
''',
			     locals ())

	def set_download (self, mirror=download.gnu, format='gz', download=wget):
		"""Setup URLs and functions for downloading.

		This should not spawn any commands.
		"""

		d = self.package_dict ()
		d.update (locals ())
		self.url = mirror () % d
		self.download = lambda : download (self)

	def with (self, version='HEAD', mirror=download.gnu, format='gz', download=wget, depends=[]):
		self.ball_version = version
		self.set_download (mirror, format, download)
		self.depends = depends
		return self

class Cross_package (Package):
	"""Package for cross compilers/linkers etc.
	"""

	def configure_command (self):
		return Package.configure_command (self) \
		       + join_lines ('''
--target=%(target_architecture)s
--with-sysroot=%(system_root)s/
''')

        def gub_name (self):
		return '%(name)s-%(version)s-%(build)s.%(build_architecture)s-%(target_architecture)s.gub'

	def install_command (self):
		# FIXME: to install this, must revert any prefix=tooldir stuff
		return join_lines ('''make prefix=/usr DESTDIR=%(install_root)s install''')

	def install_gub (self):
		pass

	def sysinstall (self):
		self._install_gub (self.settings.tooldir)

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

	def config_cache_overrides (self, str):
		return str

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

	def config_cache (self):
		self.system ('mkdir -p %(builddir)s')
		cache_fn = self.builddir () + '/config.cache'
		cache = open (cache_fn, 'w')
		str = (cross.cross_config_cache['all']
		       + cross.cross_config_cache[self.settings.platform])
		str = self.config_cache_overrides (str)
		cache.write (str)
		cache.close ()
		os.chmod (cache_fn, 0755)

	def configure (self):
		self.config_cache ()
		Package.configure (self)

	def target_dict (self, env={}):
		dict = {
			'AR': '%(tool_prefix)sar',
			'CC': '%(tool_prefix)sgcc %(target_gcc_flags)s',
			'CPPFLAGS': '-I%(system_root)s/usr/include',
			'CXX':'%(tool_prefix)sg++ %(target_gcc_flags)s',
			'DLLTOOL' : '%(tool_prefix)sdlltool',
			'DLLWRAP' : '%(tool_prefix)sdllwrap',
			'LD': '%(tool_prefix)sld',
#			'LDFLAGS': '-L%(system_root)s/usr/lib',
# FIXME: for zlib, try adding bin
			'LDFLAGS': '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin',
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
		if self.settings.__dict__.has_key ('gcc'):
			dict['CC'] = self.settings.gcc
		if self.settings.__dict__.has_key ('gxx'):
			dict['CXX'] = self.settings.gxx
		if self.settings.__dict__.has_key ('ld'):
			dict['LD'] = self.settings.ld

		dict.update (env)
		return dict

	def dump (self, str, name, mode='w', env={}):
		dict = self.target_dict (env)
		return Package.dump (self, str, name, mode=mode, env=dict)

	def file_sub (self, re_pairs, name, to_name=None, env={}):
		dict = self.target_dict (env)
		return Package.file_sub (self, re_pairs, name, to_name=to_name, env=dict)

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
		tarball = self.settings.downloaddir + '/' + self.file_name ()
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		flags = download.untar_flags (tarball)
		cmd = 'tar %(flags)s %(tarball)s -C %(srcdir)s/root'
		self.system (cmd, locals ())

	def configure (self):
		pass

	def patch (self):
		pass

	def compile (self):
		pass

	def install (self):
		self.system ('mkdir -p %(install_root)s')
		self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s -xvf-')

