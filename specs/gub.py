import os
import sys
import re
import subprocess
import cross

def system_one (cmd, ignore_error, env):
	sys.stderr.write ('invoking %s\n' % cmd)

	proc = subprocess.Popen (cmd, shell=True, env=env)
	stat = proc.wait ()
	
	if stat and not ignore_error:
		raise 'barf'

	return 0 

def system (cmd, ignore_error=False, env={}):
	call_env = os.environ.copy ()
	call_env.update (env)

	for (k, v) in env.items ():
		sys.stderr.write ('%s=%s\n' % (k, v))

	for i in cmd.split ('\n'):
		if i:
			system_one (i, ignore_error, call_env)

	return 0

class Package:
	def __init__ (self, settings):
		self.settings = settings
	
	def system (self, cmd, env={}):
		system (cmd, ignore_error=False, env=env)
		
	def download (self):
		dir = self.settings.downloaddir
		if not os.path.exists (dir + '/' + self.file_name ()): 
			self.system ('cd %s ; wget %s ' % (dir, self.url))

	def unpack_destination (self):
		return self.settings.srcdir
	
	def basename (self):
		f = self.file_name ()
		f = re.sub ("\.tar.*", '', f)
		return f

	def name (self):
		s = self.basename ()
		s = re.sub ('-?[0-9][^-]+$', '', s)
		return s
	
	def srcdir (self):
		return self.unpack_destination () + '/' + self.basename ()

	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	def installdir (self):
		return self.settings.installdir + '/' + self.name ()

	def file_name (self):
		file = re.sub (".*/([^/]+)", '\\1', self.url)
		return file


	def done (self, stage):
		return os.path.exists ('%s/%s-%s' % (self.settings.statusdir, self.name (), stage))

	def set_done (self, stage):
		open ('%s/%s-%s' % (self.settings.statusdir, self.name(), stage), 'w').write ('')

	def autoupdate (self):
		if os.path.isdir (os.path.join (self.srcdir (), 'ltdl')):
			self.system ('''
rm -rf %(srcdir)s/libltdl
cd %(srcdir) && libtoolize --force --copy --automake --ltdl
''')
		else:
			self.system ('''
cd %(srcdir)s && libtoolize --force --copy --automake
''')
		if os.path.exists (os.path.join (self.srcdir (), 'bootstrap')):
			self.system ('''
cd %(srcdir)s && ./bootstrap
''')
		elif os.path.exists (os.path.join (self.srcdir (), 'autogen.sh')):
			self.system ('''
cd %(srcdir) && bash autogen.sh
''')
		else:
			self.system ('''
cd %(srcdir)s && aclocal
cd %(srcdir)s && autoheader
cd %(srcdir)s && autoconf
cd %(srcdir)s && automake --add-missing
''')

	def configure_command (self):
		return ("%s/configure --prefix=%s "
			% (self.srcdir (), self.installdir ()))

	def configure (self):
		self.system ("mkdir -p %s;  cd %s && %s" % (self.builddir(),
						       self.builddir(),
						       self.configure_command ()))

	def install_command (self):
		return 'make install'
	
	def install (self):
		self.system ("cd %s && %s" % (self.builddir (), self.install_command ())) 

	def compile_command (self):
		return 'make'

	def compile (self):
		self.system ("cd %s && %s" % (self.builddir(), self.compile_command ()))

	def patch (self):
		pass
	
	def unpack (self):
		file = self.settings.downloaddir + '/' + self.file_name ()

		cmd = ""
		if re.search (".tar$", file):
			cmd = "-xf "
		elif re.search (".tar.bz2", file):
			cmd = "-jxf "
		elif re.search ('.tar.gz', file):
			cmd = '-xzf '

		cmd = "tar %s %s -C %s " % (cmd, file, self.unpack_destination ())
		self.system (cmd) 


class Cross_package (Package):
	def configure_command (self):
		cmd = Package.configure_command (self)
		cmd += ' --target=%s --with-sysroot=%s ' % (self.settings.target_architecture, self.settings.systemdir)
		return cmd
	
class Target_package (Package):
	def configure_command (self):
		# --config-cache
		flags = ' --enable-shared --disable-static --build=%(build_spec)s --host=%(target_architecture)s --target=%(target_architecture)s --prefix=/usr --sysconfdir=/etc --includedir=%(garbagedir)s '
		flags = flags % self.settings.__dict__

		return '%s/configure %s' % (self.srcdir(), flags)

	def configure_cache_overrides (self,str):
		return str

	def installdir (self):
		# the usr/ works around a fascist check in libtool
		return self.settings.installdir + "/" + self.name () + "-root/usr"

	def install_command (self):
		return 'make prefix=%s install' % self.installdir ()
		
	def configure (self):
		self.system ("mkdir -p %s" % self.builddir ())
		cache_fn = self.builddir () +'/config.cache'
		cache = open (cache_fn, 'w')
		str = cross.cross_config_cache + cross.cygwin
		str = self.configure_cache_overrides (str)
		cache.write (str)
		cache.close ()

		os.chmod (cache_fn, 0755)
		Package.configure (self)

	def system (self, cmd):
		dict = {
			'CXX':'%(target_architecture)s-g++ %(target_gcc_flags)s',
			'CC':'%(target_architecture)s-gcc %(target_gcc_flags)s',
			'RANLIB': '%(target_architecture)s-ranlib',
			'DLLWRAP' : '%(target_architecture)s-dllwrap',
			'DLLTOOL' : '%(target_architecture)s-dlltool',
			'LD': '%(target_architecture)s-ld',
			'AR': '%(target_architecture)s-ar',
			'NM': '%(target_architecture)s-nm',
			
			'srcdir': self.srcdir (),
			'builddir': self.builddir (),
			
			}
		
		for (k, v) in dict.items ():
			v = v % self.settings.__dict__
			dict[k] = v
			
		return Package.system (self, cmd, env=dict)
		

		

