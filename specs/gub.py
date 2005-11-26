import cross
import cvs
import download as dl
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
		log_command ('Command barfed: %s' % cmd )
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
			'build_spec': self.settings.build_spec,
			'garbagedir': self.settings.garbagedir,
			'gtk_version': self.settings.gtk_version,
			'systemdir': self.settings.systemdir,
			'target_architecture': self.settings.target_architecture,
			'target_gcc_flags': self.settings.target_gcc_flags,
			'name': self.name (),
			'version': self.version,
			'url': self.url,
			'builddir': self.builddir (),
			'compile_command': self.compile_command (),
			'configure_command': self.configure_command (),
			'install_command': self.install_command (),
			'installdir': self.installdir (),
			'srcdir': self.srcdir (),
			'sourcesdir': self.settings.srcdir,
			'uploaddir': self.settings.uploaddir,
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
		f = re.sub ('-src\.tar.*', '', f)
		f = re.sub ('\.tar.*', '', f)
		return f

	def name (self):
		s = self.basename ()
		s = re.sub ('-?[0-9][^-]+$', '', s)
		return s
	
	def srcdir (self):
		return self.settings.srcdir + '/' + self.basename ()

	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	def installdir (self):
		return self.settings.installdir + '/' + self.name ()

	def file_name (self):
		if self.url:
			file = re.sub ('.*/([^/]+)', '\\1', self.url)
		else:
			file = self.__class__.__name__.lower ()
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
		return '%(srcdir)s/configure --prefix=%(installdir)s'

	def configure (self):
		self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

	def install_command (self):
		return 'make install'
	
	def install (self):
		self.system ('cd %(builddir)s && %(install_command)s')

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
		file = self.settings.downloaddir + '/' + self.file_name ()

		if not os.path.exists (file):
			return

		flags = ''
		if re.search ('.tar$', file):
			flags = '-xf '
		elif re.search ('.tar.bz2', file):
			flags = '-jxf '
		elif re.search ('.tar.gz', file):
			flags = '-xzf '

		# clean up
		self.system ("rm -rf  %(srcdir)s %(builddir)s")
		cmd = 'tar %(flags)s %(file)s -C %(sourcesdir)s'
		self.system (cmd, locals ())

	def set_download (self, mirror=dl.gnu, format='gz', download=wget):
		d = self.package_dict ()
		d.update (locals ())
		self.url = mirror () % d
		self.download = lambda : download (self)

	def with (self, version='HEAD', mirror=dl.gnu, format='gz', download=wget):
		self.version = version
		self.set_download (mirror, format, download)
		return self

class Cross_package (Package):
	"Package for cross compilers/linkers etc."

	def configure_command (self):
		cmd = Package.configure_command (self)
		cmd += ''' --target=%(target_architecture)s
--with-sysroot=%(systemdir)s'''
		return join_lines (cmd)
	
class Target_package (Package):
	def configure_command (self):
		return join_lines ('''%(srcdir)s/configure 
--config-cache 
--enable-shared 
--disable-static 
--build=%(build_spec)s 
--host=%(target_architecture)s 
--target=%(target_architecture)s 
--prefix=/usr 
--sysconfdir=/etc 
--includedir=/usr/include 
--libdir=/usr/lib 
''')

	def configure_cache_overrides (self, str):
		return str

	def installdir (self):
		# FIXME: the usr/ works around a fascist check in libtool
		# better use %(installdir)s/USR throughout and remove here?
		return self.settings.installdir + "/" + self.name () + "-root/usr"
		# FIXME: system dir vs packaging install
		# no packages for now
		# return self.settings.systemdir + '/usr'

	def install_command (self):
		return '''make install \
prefix=%(installdir)s \
exec_prefix=%(installdir)s \
bindir=%(installdir)s/bin \
infodir=%(installdir)s/share/info \
mandir=%(installdir)s/share/man \
libdir=%(installdir)s/lib \
sysconfdir=%(installdir)s/etc \
includedir=%(installdir)s/include \
tooldir=%(installdir)s \
gcc_tooldir=%(installdir)s \
libexecdir=%(installdir)s/lib \
'''
		
	def config_cache (self):
		self.system ('mkdir -p %(builddir)s')
		cache_fn = self.builddir () + '/config.cache'
		cache = open (cache_fn, 'w')
		str = (cross.cross_config_cache['all']
		       + cross.cross_config_cache[self.settings.platform])
		str = self.configure_cache_overrides (str)
		cache.write (str)
		cache.close ()
		os.chmod (cache_fn, 0755)
		
	def configure (self):
		self.config_cache ()
		Package.configure (self)

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(installdir)s -zcf %(uploaddir)s/%(name)s.gub .
''')

	def sysinstall (self):
		self.system ('''
mkdir -p %(systemdir)s/usr
tar -C %(systemdir)s/usr -zxf %(uploaddir)s/%(name)s.gub
''')

	def target_dict (self, env={}):
		dict = {
			'AR': '%(target_architecture)s-ar',
			'CC':'%(target_architecture)s-gcc %(target_gcc_flags)s',
			'CPPFLAGS': '-I%(systemdir)s/usr/include',
			'CXX':'%(target_architecture)s-g++ %(target_gcc_flags)s',
			'DLLTOOL' : '%(target_architecture)s-dlltool',
			'DLLWRAP' : '%(target_architecture)s-dllwrap',
			'LD': '%(target_architecture)s-ld',
#			'LDFLAGS': '-L%(systemdir)s/usr/lib',
# FIXME: for zlib, try adding bin
			'LDFLAGS': '-L%(systemdir)s/usr/lib -L%(systemdir)s/usr/bin',
			'MINGW_RUNTIME_DIR': self.settings.runtimedir,
			'NM': '%(target_architecture)s-nm',
			'PKG_CONFIG_PATH': '%(systemdir)s/usr/lib/pkgconfig',
			'PKG_CONFIG': '''/usr/bin/pkg-config \
--define-variable prefix=%(systemdir)s/usr \
--define-variable includedir=%(systemdir)s/usr/include \
--define-variable libdir=%(systemdir)s/usr/lib \
''',
			'RANLIB': '%(target_architecture)s-ranlib',
			'SED': 'sed', # libtool (expat mingw) fixup
			}

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
		
