
import gdbm as dbmodule
#import dbhash as dbmodule

import dbhash
import gzip
import os
import re
import string
#
import buildnumber
import framework
import gub
import fcntl
import sys

# X package manager (x for want of better name)

def tar_compression_flag (ball):
	compression_flag = ''
	if ball.endswith ('bz2'):
		compression_flag = 'j'
	if ball.endswith ('gz'):
		compression_flag = 'z'
	return compression_flag

#
# TODO:

#
# separate into interface and
# implementation (loose all the _methods() )
#
class Package_manager:
	def __init__ (self, root, os_interface):
		self.root = root
		self.config = self.root + '/etc/xpm/'
		self.os_interface = os_interface
		self._packages = {}
		self.include_build_deps = True

		if not os.path.isdir (self.config):
			os_interface.system ('mkdir -p %s' % self.config)


		
		lock_file = self.config + 'lock'
		self._lock_file = open (lock_file, 'w')

		try:
			fcntl.flock (self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
		except IOError:			
			sys.stderr.write ("Can't acquire Package_manager lock %s\n\nAbort\n" % lock_file)
			sys.exit (1)


		self._file_package_db = dbmodule.open (self.config
						       + '/files.db', 'c')
		self._package_file_db = dbmodule.open (self.config
						       + '/packages.db', 'c')


		
		
	def is_installable (self, package):
		ball = package.expand ('%(gub_uploads)s/%(gub_name)s')
		return os.path.exists (ball)

	def installed_packages (self):
		names = self._package_file_db.keys ()
		return [self._packages[p] for p in names]

	def tarball_files (self, ball):
		flag = tar_compression_flag (ball)
		str = self.os_interface.read_pipe ('tar -tf%(flag)s "%(ball)s"'
						   % locals (), silent=True)
		lst = str.split ('\n')
		return lst

	def installed_files (self, package):
		return self._package_file_db[package.name ()].split ('\n')

	def file_list_name (self, package):
		return '%s/%s.lst.gz' % (self.config, package.name ())

	def is_installed (self, package):
		return self._package_file_db.has_key (package.name())

	def _read_file_list (self, package):
		return map (string.strip,
			    gzip.open (self.file_list_name (package)).readlines ())

	def _write_file_list (self, package, lst):
		f = gzip.open (self.file_list_name (package), 'w')
		for i in lst:
			f.write ('%s\n' % i)
		f.close ()

	def _build_package (self, package):
		if self.is_installed (package):
			return
		if not self.is_installable (package):
			self.os_interface.log_command ('building package: %s\n'
						       % `package`)
			package._builder ()
		if (self.is_installable (package)
		    and not self.is_installed (package)):
			self._install_package (package)

	def _dependencies_package (self, package):
		if package._dependencies != None:
			return

		if package.verbose:
			self.os_interface.log_command ('resolving dependencies: %s\n'
						       % `package`)
		package._dependencies = []
		package._build_dependencies = []
		try:
			package._dependencies = map (lambda x:
						     self._packages[x],
						     package.name_dependencies)
			if package in package._dependencies:
				print ('simple circular dependency',
				       package,
				       package.name_dependencies,
				       package._dependencies,
				       self._packages)
				raise 'BARF'

			package._build_dependencies = map (lambda x:
							   self._packages[x],
							   package.name_build_dependencies)

			if package in package._build_dependencies:
				print ('simple circular build dependency',
				       package,
				       package.name_build_dependencies,
				       package._build_dependencies,
				       self._packages)
				raise 'BARF'

			## should use name_dependencies ?
			#if self.include_build_deps:
			#	package._dependencies += package._build_dependencies


		except KeyError, k:
			print 'xpm: resolving dependencies for: %s' % package
			print 'xpm: unknown package: %s' % k
			print 'xpm: available packages: %s' % self._packages
			print 'xpm: deps: %s' % package.name_dependencies

			# don't barf.  This fucks up with SDK
			# packages, and separate target/framework
			# managers.

	def _download_package (self, package):
		self.os_interface.log_command ('downloading package: %s\n'
					       % `package`)
		package._download ()

	def _install_package (self, package):
		if self.is_installed (package):
			return
		self.os_interface.log_command ('installing package: %s\n'
					       % `package`)
		name = package.name ()
		if self._package_file_db.has_key (name):
			print 'already have package ', name
			raise 'abort'

		ball = package.expand ('%(gub_uploads)s/%(gub_name)s')

		self.os_interface.log_command ('installing package %(name)s from %(ball)s\n'
					       % locals ())

		flag = tar_compression_flag (ball)
		root = self.root
		lst = self.tarball_files (ball)

		conflicts = False
		for f in lst:
			if (self._file_package_db.has_key (f)
			    and not os.path.isdir (self.root + '/'+  f)):
				print 'already have file %s: %s' % (f, self._file_package_db[f])
				conflicts = True

		if conflicts and not package.settings.is_distro:
			raise 'abort'

		self.os_interface.system ('tar -C %(root)s -xf%(flag)s %(ball)s' % locals ())

		self._package_file_db[name] = '\n'.join (lst)
		for f in lst:
			
			# ignore directories.
			if f and  f[-1] != '/':
				self._file_package_db[f] = name
			
		self._write_file_list (package, lst)

	def _register_package (self, package):
		if package.verbose:
			self.os_interface.log_command ('registering package: %s\n'
						       % `package`)
		self._packages[package.name ()] = package

	def _uninstall_package (self, package):
		self.os_interface.log_command ('uninstalling package: %s\n'
					       % `package`)
		listfile = self.file_list_name (package)
		lst = self.installed_files (package)
		name = package.name()
		
		dirs = []
		files = []
		for i in lst:
			f = os.path.join (self.root, i)
			if (not os.path.exists (f)
			    and not os.path.islink (f)
			    and not package.settings.is_distro):
				print 'xpm: uninstall: %s' % package
				print 'xpm: no such file: %s' % f
				# should've dealt with this in install stage.
			        print "\n\nBARF\n\n" 
			elif os.path.isdir (f):
				dirs.append (f)
			else:
				files.append (f)

		for f in files:
			os.unlink (f)

		for d in reversed (dirs):
			try:
				os.rmdir (d)
			except OSError:
				print 'warning: %s not empty' % d

		for f in lst:
			if not f or f[-1] == '/':
				continue
			try:
				del self._file_package_db[f]
			except:
				print 'db delete failing for ', f
		del self._package_file_db[name]
		os.unlink (listfile)

	def with_dependencies (self, package, before=None, after=None):

		# FIXME: circular depends hack for debian
		busy = ''
		if before:
			busy += before.__name__
		if after:
			busy += after.__name__
		if package.__dict__.has_key (busy):
			return
		package.__dict__[busy] = None
		if before:
			before (package)

		for d in self.dependencies (package):
			if package.verbose:
				self.os_interface.log_command (busy + ': '
							       + 'dependency: '
							       + d.name ()
							       + ' for package: '
							       + package.name ()
							       + '\n')
			self.with_dependencies (d, before, after)
		if after:
			after (package)
			
		# FIXME: work around debian's circular dependencies
		del (package.__dict__[busy])

	def build_package (self, package):
		self.with_dependencies (package, after=self._build_package)

	def dependencies (self, package):
		if package._dependencies == None:
			self.with_dependencies (package,
						before=self._dependencies_package)
		deps = package._dependencies
		if self.include_build_deps:
			deps += package._build_dependencies
		return deps

	def download_package (self, package):
		self.with_dependencies (package, before=self._download_package)

	def install_package (self, package):
		self.with_dependencies (package, after=self._install_package)

	def uninstall_package (self, package):
## FIXME: what did we do before / what was I thinking?
##	       self.with_dependencies (package, after=self._uninstall_package)
		self._uninstall_package (package)

	def register_package (self, package):
		self.with_dependencies (package, after=self._register_package)

	def topological_sort (manager, nodes):
		deps = dict ([(n, [d for d in manager.dependencies (n)
				   if d in nodes])
			      for n in nodes])

		done = {}

		sorted = []
		while deps:
			rm = [n for (n, ds) in deps.items () if ds == []]
			sorted += rm

			deps = dict ([(n, ds) for (n, ds) in deps.items ()
				      if ds != []])
			for ds in deps.values ():
				ds[:] = [d for d in ds if d not in rm]

		return sorted

	# NAME_ shortcuts
	def name_build (self, name):
		self.build_package (self._packages[name])
	def name_download (self, name):
		self.download_package (self._packages[name])
	def name_files (self, name):
		return self.installed_files (self._packages[name])
	def name_install (self, name):
		self.install_package (self._packages[name])
	def name_uninstall (self, name):
		self.uninstall_package (self._packages[name])
	def name_is_installed (self, name):
		try:
			return self.is_installed (self._packages[name])
		except KeyError, k:
			print 'known packages', self._packages
			raise "Unknown package", k

class Cygwin_package_manager (Package_manager):
	def __init__ (self, settings):
		Package_manager.__init__ (self, settings.system_root,
					  settings.os_interface)
		self.mirror = 'http://gnu.kookel.org/ftp/cygwin'
		self.settings = settings
		self.dist = 'curr'

	def get_packages (self, package_file):
		def get_package (name, dict):
			from new import classobj
			Package = classobj (name, (gub.Binary_package,), {})
			package = Package (self.settings)
			package.name_dependencies = []
			package.name_build_dependencies = []
			if dict.has_key ('requires'):
				deps = map (string.strip,
					    re.sub ('\([^\)]*\)', '',
						    dict['requires']).split ())
				blacklist = (
					'_update-info-dir',
					'bintutils',
					'gcc', 'gcc-core', 'gcc-g++',
					'gcc-mingw', 'gcc-mingw-core', 'gcc-mingw-g++',
					'libXft', 'libXft1', 'libXft2',
					'libbz2_1',
					'libguile16',
					'X-startup-scripts',
					'xorg-x11-bin-lndir',
					)
				deps = filter (lambda x: x not in blacklist, deps)
				package.name_dependencies = deps
			package.ball_version = dict['version']
			package.url = (self.mirror + '/'
				       + dict['install'].split ()[0])
			package.format = 'bz2'
			return package

		self._dists = {'test': [], 'curr': [], 'prev' : []}
		chunks = string.split (open (package_file).read (), '\n\n@ ')
		for i in chunks[1:]:
			lines = string.split (i, '\n')
			name = string.strip (lines[0])
			blacklist = ('binutils', 'gcc')
			if name in blacklist:
				continue
			packages = self._dists['curr']
			records = {
				'sdesc': name,
				'version': '0-0',
				'install': 'urg 0 0',
				}
			j = 1
			while j < len (lines) and string.strip (lines[j]):
				if lines[j][0] == '#':
					j = j + 1
					continue
				elif lines[j][0] == '[':
					packages.append (get_package (name,
								      records.copy ()))
					packages = self._dists[lines[j][1:5]]
					j = j + 1
					continue

				try:
					key, value = map (string.strip,
							  lines[j].split (': ',
									  1))
				except:
					print lines[j], package_file, self
					raise 'URG'
				if (value.startswith ('"')
				    and value.find ('"', 1) == -1):
					while 1:
						j = j + 1
						value += '\n' + lines[j]
						if lines[j].find ('"') != -1:
							break
				records[key] = value
				j = j + 1
			packages.append (get_package (name, records))
		return self._dists[self.dist]
		#return self._dists['curr'] + self._dists['test']

class Debian_package_manager (Package_manager):
	def __init__ (self, settings):
		Package_manager.__init__ (self, settings.system_root,
					  settings.os_interface)
		self.mirror = 'http://ftp.de.debian.org/debian'
		self.settings = settings

	def get_packages (self, package_file):
		return map (self.debian_package,
			    open (package_file).read ().split ('\n\n')[:-1])

	def debian_package (self, description):
		from new import classobj
		s = description[:description.find ('\nDescription')]
		d = dict (map (lambda line: line.split (': ', 1),
			       map (string.strip, s.split ('\n'))))
		Package = classobj (d['Package'], (gub.Binary_package,), {})
		package = Package (self.settings)
		package.name_dependencies = []
		if d.has_key ('Depends'):
			deps = map (string.strip,
				    re.sub ('\([^\)]*\)', '',
					    d['Depends']).split (', '))
			# FIXME: BARF, ignore choices
			deps = filter (lambda x: x.find ('|') == -1, deps)
			# FIXME: how to handle Provides: ?
			# FIXME: BARF, fixup libc Provides
			deps = map (lambda x: re.sub ('libc($|-)', 'libc6\\1',
						      x), deps)
			# FIXME: ugh, skip some
			blacklist = ('perl', 'perl-modules', 'perl-base')
			deps = filter (lambda x: x not in blacklist, deps)
			package.name_dependencies = deps
 
		package.name_build_dependencies = []
		package.ball_version = d['Version']
		package.url = self.mirror + '/' + d['Filename']
		package.format = 'deb'
		return package

def get_manager (settings):
	cross_module = None
	if settings.platform == 'cygwin':
		import cygwin
		cross_module = cygwin
	elif settings.platform == 'darwin':
		import darwintools
		cross_module = darwintools
	elif settings.platform.startswith ('debian'):
		import debian_unstable
		cross_module = debian_unstable
	elif settings.platform.startswith ('freebsd'):
		import freebsd
		cross_module = freebsd
	elif settings.platform.startswith ("linux"):
		import linux
		cross_module = linux
	elif settings.platform.startswith ('local'):
		import tools
		cross_module = tools
	elif settings.platform.startswith ('mingw'):
		import mingw
		cross_module = mingw

	cross_packages = cross_module.get_packages (settings)
	
	target_manager = Package_manager (settings.system_root,
					  settings.os_interface)

	map (target_manager._register_package, cross_packages)
	map (target_manager._register_package,
	     framework.get_packages (settings))

	for p in target_manager._packages.values ():
		settings.build_number_db.set_build_number (p)

	cross_module.change_target_packages (target_manager._packages.values ())

	return target_manager

def intersect (l1, l2):
	return [l for l in l1 if l in l2]

def determine_manager (settings, managers, args):
	for p in managers:
		if intersect (args, p._packages.keys ()):
			return p

	if settings.use_tools:
		return managers[0]
	else:
		return managers[-1]
