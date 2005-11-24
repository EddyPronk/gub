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

def gnu_mirror (dict):
	return 'ftp://dl.xs4all.nl/pub/mirror/gnu/%(name)s/%(name)s-%(version)s.tar.gz' % dict

def gnu_org_mirror (dict):
	return 'ftp://ftp.gnu.org/pub/gnu/%(name)s/%(name)s-%(version)s.tar.gz' % dict

def gtk_mirror (dict):
	return 'ftp://ftp.gtk.org/pub/gtk/v%(gtk_version)s/%(name)s-%(version)s.tar.gz' % dict

class Package:
	def __init__ (self, settings, version, mirror=gnu_mirror):
		self.settings = settings
		gtk_version = settings.gtk_version
		name = self.__class__.__name__.lower ()
		self.url = mirror (locals ())
	
	def system (self, cmd, env={}):
		dict = {
			'build_spec': self.settings.build_spec,
			'garbagedir': self.settings.garbagedir,
			'systemdir': self.settings.systemdir,
			'target_architecture': self.settings.target_architecture,
			'target_gcc_flags': self.settings.target_gcc_flags,

			'url': self.url,

			'builddir': self.builddir (),
			'compile_command': self.compile_command (),
			'configure_command': self.configure_command (),
			'install_command': self.install_command (),
			'installdir': self.installdir (),
			'srcdir': self.srcdir (),
			'unpack_destination': self.unpack_destination (),
			}
		dict.update (env)

		for (k, v) in dict.items ():
			if type (v) == type (''):
				v = v % dict
				dict[k] = v
			else:
				del dict[k]

		system (cmd % dict, ignore_error=False, env=dict)
		
	def download (self):
		dir = self.settings.downloaddir
		if not os.path.exists (dir + '/' + self.file_name ()):
			self.system ('''
cd %(dir)s && wget %(url)s
''', locals ())

	def unpack_destination (self):
		return self.settings.srcdir
	
	def basename (self):
		f = self.file_name ()
		f = re.sub ('\.tar.*', '', f)
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
		file = re.sub ('.*/([^/]+)', '\\1', self.url)
		return file

	def done (self, stage):
		return '%s/%s-%s' % (self.settings.statusdir, self.name (), stage)
	def is_done (self, stage):
		return os.path.exists (self.done (stage))

	def set_done (self, stage):
		open (self.done (stage), 'w').write ('')

	def autoupdate (self):
		if os.path.isdir (os.path.join (self.srcdir (), 'ltdl')):
			self.system ('''
rm -rf %(srcdir)s/libltdl
cd %(srcdir)s && libtoolize --force --copy --automake --ltdl
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
		return '''%(srcdir)s/configure
--prefix=%(installdir)s
'''

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
	
	def unpack (self):
		file = self.settings.downloaddir + '/' + self.file_name ()

		flags = ''
		if re.search ('.tar$', file):
			flags = '-xf '
		elif re.search ('.tar.bz2', file):
			flags = '-jxf '
		elif re.search ('.tar.gz', file):
			flags = '-xzf '

		cmd = 'tar %(flags)s %(file)s -C %(unpack_destination)s'
		self.system (cmd, locals ())


class Cross_package (Package):
	def configure_command (self):
		return Package.configure_command (self) + ''' \
--target=%(target_architecture)s \
--with-sysroot=%(systemdir)s \
'''
		return cmd
	
class Target_package (Package):
	def configure_command (self):
		return '''%(srcdir)s/configure \
--config-cache \
--enable-shared \
--disable-static \
--build=%(build_spec)s \
--host=%(target_architecture)s \
--target=%(target_architecture)s \
--prefix=/usr \
--sysconfdir=/etc \
--includedir=%(systemdir)s/include \
--libdir=%(systemdir)s/lib \
'''

## wtf?
##--includedir=%(garbagedir)s \

	def configure_cache_overrides (self, str):
		return str

	def installdir (self):
		# the usr/ works around a fascist check in libtool
		##return self.settings.installdir + "/" + self.name () + "-root/usr"
		# no packages for now
		return self.settings.systemdir + '/usr'

	def install_command (self):
		return 'make prefix=%(installdir)s install'
		
	def configure (self):
		self.system ('mkdir -p %(builddir)s')
		cache_fn = self.builddir () +'/config.cache'
		cache = open (cache_fn, 'w')
		str = cross.cross_config_cache + cross.cygwin
		str = self.configure_cache_overrides (str)
		cache.write (str)
		cache.close ()

		os.chmod (cache_fn, 0755)
		Package.configure (self)

	def system (self, cmd, env={}):
		dict = {
			'AR': '%(target_architecture)s-ar',
			'CC':'%(target_architecture)s-gcc %(target_gcc_flags)s',
			'CPPFLAGS': '-I%(installdir)s/include',
			'CXX':'%(target_architecture)s-g++ %(target_gcc_flags)s',
			'DLLTOOL' : '%(target_architecture)s-dlltool',
			'DLLWRAP' : '%(target_architecture)s-dllwrap',
			'LD': '%(target_architecture)s-ld',
			'LDFLAGS': '-L%(installdir)s/lib',
			'NM': '%(target_architecture)s-nm',
			'RANLIB': '%(target_architecture)s-ranlib',
			}

		dict.update (env)

		return Package.system (self, cmd, env=dict)
