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

def start_log ():
	global log_file
	log_file = open ('build.log', 'w+')
	log_file.write ('\n\n *** Starting build: %s\n' %  now ())
	
def log_command (str):
	sys.stderr.write (str)
	if log_file:
		log_file.write (str)
		log_file.flush ()
	
def system_one (cmd, ignore_error, env):
	log_command ('invoking %s\n' % cmd)
	
	proc = subprocess.Popen (cmd, shell=True, env=env)
	stat = proc.wait ()
	
	if stat and not ignore_error:
		log_command ('Command barfed: %s\n' % cmd )
		sys.exit (1)

	return 0 

def join_lines (str):
	return re.sub ('\n', ' ', str)

def system (cmd, ignore_error = False, verbose=False, env={}):
	"Run multiple lines as multiple commands."
	
	call_env = os.environ.copy ()
	call_env.update (env)

	if verbose:
		for (k, v) in env.items ():
			sys.stderr.write ('%s=%s\n' % (k, v))

	for i in cmd.split ('\n'):
		if i:
			system_one (i, ignore_error, call_env)

	return 0

def dump (name, str, mode='w'):
	f = open (name, mode)
	f.write (str)
	f.close ()

def file_sub (frm, to, name):
	s = open (name).read ()
	t = re.sub (re.compile (frm, re.MULTILINE), to, s)
	if s != t:
		system ('mv %s %s~' % (name, name))
		h = open (name, 'w')
		h.write (t)
		h.close ()

def read_pipe (cmd):
	pipe = os.popen (cmd, 'r')
	output = pipe.read ()
	status = pipe.close ()
	# successful pipe close returns 'None'
	if status:
		raise 'read_pipe failed'
	return output

class Package:
	def __init__ (self, settings):
		self.settings = settings
		self.url = ''
		self.download = self.wget
		
	def package_dict (self, env={}):
		dict = {
			'build_architecture': self.settings.build_architecture,
			'garbagedir': self.settings.garbagedir,
			'gtk_version': self.settings.gtk_version,
			'platform': self.settings.platform,
			'system_root': self.settings.system_root,
			'target_architecture': self.settings.target_architecture,
			'tooldir': self.settings.tooldir,
			'tool_prefix': self.settings.tool_prefix,
			'target_gcc_flags': self.settings.target_gcc_flags,

			'name': self.name (),
			'version': self.version,
			'url': self.url,
			'builddir': self.builddir (),
			'compile_command': self.compile_command (),
			'configure_command': self.configure_command (),
			'install_command': self.install_command (),
			'install_root': self.install_root (),
			'install_prefix': self.install_prefix (),
			'srcdir': self.srcdir (),
			'sourcesdir': self.settings.srcdir,
			'uploaddir': self.settings.uploaddir,

			'installer_root': self.settings.installer_root,
			'packagedir': self.settings.packagedir,

			}
		
		dict.update (env)
		for (k, v) in dict.items ():
			if type (v) == type (''):
				v = v % dict
				dict[k] = v
			else:
				del dict[k]

		return dict 

	def dump (self, name, str, mode='w', env={}):
		dict = self.package_dict (env)
		return dump (name % dict, str % dict, mode=mode)

	def file_sub (self, frm, to, name, env={}):
		dict = self.package_dict (env)
		return file_sub (frm % dict, to % dict, name % dict)

	def read_pipe (self, cmd, env={}):
		dict = self.package_dict (env)
		return read_pipe (cmd % dict)
	
	def system (self, cmd, env={}):
		dict = self.package_dict (env)
		system (cmd % dict, ignore_error=False,
			verbose = self.settings.verbose, env=dict)

	def skip (self):
		pass
		      
	def wget (self):
		dir = self.settings.downloaddir
		if not os.path.exists (dir + '/' + self.file_name ()):
			self.system ('''
cd %(dir)s && wget %(url)s
''', locals ())

	def cvs (self):
		dir = self.settings.srcdir
		if not os.path.exists (os.path.join (dir, self.name ())):
			self.system ('''
cd %(dir)s && cvs -d %(url)s co -r %(version)s %(name)s
''', locals ())
		else:
			self.system ('''
cd %(dir)s/%(name)s && cvs update -dCAP -r %(version)s
''', locals ())
 
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
	
	def srcdir (self):
		return self.settings.srcdir + '/' + self.basename ()

	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	def install_root (self):
		return self.settings.installdir + "/" + self.name () + '-root'

	def install_prefix (self):
		return self.install_root () + '/usr'

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
	
	def done (self, stage):
		return '%s/%s-%s' % (self.settings.statusdir, self.name (), stage)
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
		self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

	def install_command (self):
		return 'make install'
	
	def install (self):
		self.system ('cd %(builddir)s && %(install_command)s')
		self.libtool_la_fixups ()

	def libtool_la_fixups (self):
		dll_name = 'lib'
		for i in glob.glob ('%(install_prefix)s/lib/*.la' \
				    % self.package_dict ()):
			base = os.path.basename (i)[3:-3]
			self.file_sub (''' *-L *[^"' ][^"' ]*''', '', i)
			self.file_sub ('''( |=|')(/[^ ]*usr/lib/lib)([^ ']*)\.(a|la|so)[^ ']*''', '\\1-l\\3', i)
			#  ' " ''' '
			# we don't have sover
#			self.file_sub ('^dlname=.*',
#				       """dlname='../bin/%(dll_prefix)%(base)s-%(sover)s.dll'""",
#				       i, locals ())
			self.file_sub ('^old_library=.*',
				       """old_library='lib%(base)s.a'""",
				       i, locals ())
                        if self.settings.platform.startswith ('mingw'):
			         self.file_sub ('library_names=.*',
						"library_names='lib%(base)s.dll.a'",
						i, locals ())

	def compile_command (self):
		return 'make'

	def compile (self):
		self.system ('cd %(builddir)s && %(compile_command)s')

	def patch (self):
		pass
	
	def package (self):
		pass

	def sysinstall (self):
		pass

	def untar (self):
		tarball = self.settings.downloaddir + '/' + self.file_name ()

		if not os.path.exists (tarball):
			return

		flags = download.untar_flags (tarball)

		# clean up
		self.system ("rm -rf %(srcdir)s %(builddir)s %(install_root)s")
		cmd = 'tar %(flags)s %(tarball)s -C %(sourcesdir)s'
		self.system (cmd, locals ())

	def set_download (self, mirror=download.gnu, format='gz', download=wget):
		"Setup URLs and functions for downloading. This should not spawn any commands."
		
		d = self.package_dict ()
		d.update (locals ())
		self.url = mirror () % d
		self.download = lambda : download (self)

	def with (self, version='HEAD', mirror=download.gnu, format='gz', download=wget):
		self.version = version
		self.set_download (mirror, format, download)
		return self

class Cross_package (Package):
	"Package for cross compilers/linkers etc."

	def configure_command (self):
		cmd = Package.configure_command (self)
		cmd += ''' --target=%(target_architecture)s
--with-sysroot=%(system_root)s/usr'''
		return join_lines (cmd)
	
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
--sysconfdir=/etc
--includedir=/usr/include
--libdir=/usr/lib
''')

	def config_cache_overrides (self, str):
		return str

	def broken_install_command (self):
		"For packages that don't honor DESTDIR."

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
sysconfdir=%(install_root)s/etc
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

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(install_prefix)s -zcf %(uploaddir)s/%(name)s-%(version)s.%(platform)s.gub .
''')

	def install_gub (self, root):
		self.system ('''
mkdir -p %(root)s
tar -C %(root)s -zxf %(uploaddir)s/%(name)s-%(version)s.%(platform)s.gub
''', locals ())

	def sysinstall (self):
		install_gub ('%(system_root)s/usr' % package_dict ())

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

	def dump (self, name, str, mode='w', env={}):
		dict = self.target_dict (env)
		return Package.dump (self, name, str, mode=mode, env=dict)

	def file_sub (self, frm, to, name, env={}):
		dict = self.target_dict (env)
		return Package.file_sub (self, frm, to, name, env=dict)

	def read_pipe (self, cmd, env={}):
		dict = self.target_dict (env)
		return Package.read_pipe (self, cmd, env=dict)
	
	def system (self, cmd, env={}):
		dict = self.target_dict (env)
		Package.system (self, cmd, env=dict)


class Binary_package (Package):
	def untar (self):
		self.system ("rm -rf %(srcdir)s %(builddir)s %(install_root)s")
		# FIXME: /root is typically holds ./bin, ./lib, include,
		# so is typically not _ROOT, but _PREFIX
		self.system ('mkdir -p %(srcdir)s/root')
		tarball = self.settings.downloaddir + '/' + self.file_name ()
		if not os.path.exists (tarball):
			return
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
		# FIXME: .GUB packaging only in TARGET_PACKAGE, skipping
		# installing in install_root, use expensive direct
		# make install %(system_root)s/usr
		self.system ('mkdir -p %(system_root)s/usr')
		self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(system_root)s/usr -xvf-')


# FIXME: Want to share package_dict () and system () with Package,
# add yet another base class?
###class Installer (Package):
class Installer (Cross_package):
	pass

        def version (self):
		return '0.0.0'
	
        def name (self):
		return 'lilypond'
	

class Bundle (Installer):
	pass

class Nsis (Installer):
	pass

class Alien (Installer):
	def create (self):

		## dit werkt nog niet, maar ik moet nu gaan.
		## iets ontzetteds dufs met .settings/version
		
		## FIXME, huh?
		installer_root = self.settings.installer_root
		packagedir = self.settings.packagedir
		NAME = 'lilypond'
		VERSION = '0.0.0'
		
		self.system ('tar -C %(installer_root)s -zcf %(packagedir)s/%(NAME)s-%(VERSION)s.tgz .' % locals ())
		self.system ('fakeroot alien --to-deb --to-rpm --to-tgz %(packagedir)s/%(NAME)s-%(VERSION)s.tgz' % locals ())
		# TODO: autopackage
