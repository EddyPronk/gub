import dbhash
import gzip
import os
import re
import string
#
import buildnumber
import framework
import gub

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
# use (G)DBM or similar to maintain package database.
#
class Package_manager:
	def __init__ (self, root, os_interface):
		self.os_interface = os_interface
		self.root = root
		self._packages = {}
		self.config = self.root + '/etc/xpm/'
		
		if not os.path.isdir (self.config):
			os_interface.system ('mkdir -p %s' % self.config)

		self._file_package_db = dbhash.open (self.config + '/files.db', 'c')
		self._package_file_db = dbhash.open (self.config + '/packages.db', 'c')

	def is_installable (self, package):
		ball = package.expand ('%(gub_uploads)s/%(gub_name)s')
		return os.path.exists (ball)

	def register_package (self, pkg):
		self._packages[pkg.name ()] = pkg

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
		return self._package_file_db[package.name()].split ('\n')

	def uninstall_package (self, package):
		if package not in self._packages.values ():
			return
		
		for (nm, p) in self._packages.items ():
			if (package in self.dependencies (p)
			    and self.is_installed (p)):
				raise ('Package %s depends on %s'
				       % (`p`, `package`))

		self.uninstall_single_package (package)

	def uninstall_single_package (self, package):
		self.os_interface.log_command ('uninstalling package %s\n' % `package`)

		listfile = self.file_list_name (package)
		lst = self.installed_files (package)
		name = package.name()
		
		dirs = []
		files = []
		for i in lst:
			f = os.path.join (self.root, i)
			force = False
			if not os.path.exists (f) and not os.path.islink (f):
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
		
	def file_list_name (self, package):
		return '%s/%s.lst.gz' % (self.config, package.name ())

	def is_installed (self, package):
		return self._package_file_db.has_key (package.name())

	def install_single_package (self, package):
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
			if self._file_package_db.has_key (f) and not os.path.isdir (self.root + '/'+  f):
				print 'already have file %s: %s' % (f, self._file_package_db[f])
				conflicts = True

		if conflicts:
			raise 'abort'

		self.os_interface.system ('tar -C %(root)s -xf%(flag)s %(ball)s' % locals ())

		self._package_file_db[name] = '\n'.join (lst)
		for f in lst:
			
			# ignore directories.
			if f and  f[-1] != '/':
				self._file_package_db[f] = name
			
		self._write_file_list (package, lst)

	def _read_file_list (self, package):
		return map (string.strip,
			    gzip.open (self.file_list_name (package)).readlines ())

	def _write_file_list (self, package, lst):
		f = gzip.open (self.file_list_name (package), 'w')
		for i in lst:
			f.write ('%s\n' % i)
		f.close ()

	def install_dependencies (self, package):
		for d in self.dependencies (package):
			self.install_package (d)

	def install_build_dependencies (self, package):
		for d in package.build_dependencies:
			self.install_package (d)

	def install_package (self, package):

		## packages may actually come from different managers.
		## we only handle registered packages.
		if package not in self._packages.values ():
			return
		
		self.install_dependencies (package)

		## need to check deps, but do anything if package is already there.
		if self.is_installed (package):
			return
		self.install_single_package (package)

	def dependencies (self, package):
		# FIXME: check twice
		if package._dependencies == None:
			self._resolve_dependencies (package)
		print 'dependencies for: ' + package.name () + ':' + `package._dependencies`
		return package._dependencies + package.build_dependencies

	def _resolve_dependencies (self, package):
		package._dependencies = []
		print 'name_dependencies for: ' + package.name () + ':' + `package.name_dependencies`
		try:
			for d in package.name_dependencies:
				dependency = self._packages[d]
				package._dependencies += [dependency]
				if dependency._dependencies == None:
					self._resolve_dependencies (dependency)
			if package in package._dependencies:
				print 'circular dependency', package, package.name_dependencies, package._dependencies, self._packages
				raise 'BARF'

		except KeyError, k:
			print 'xpm: resolving dependencies for: %s' % package
			print 'xpm: unknown package: %s' % k
			print 'xpm: available packages: %s' % self._packages
			print 'xpm: deps: %s' % package.name_dependencies
			raise 'barf'

	# NAME_ shortcuts
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

#Class factory in the [new] module (python)
#>>> from new import classobj
#>>> Foo2 = classobj('Foo2',(Foo,),{'bar':lambda self:'bar'})
#>>> Foo2().bar()
#'bar'
#>>> Foo2().say_foo()
#foo

class Debian_package_manager (Package_manager):
	def __init__ (self, settings):
		Package_manager.__init__ (self, settings.system_root,
					  settings.os_interface)
		self.pool = 'http://ftp.de.debian.org/debian'
		self.settings = settings

	def register_packages (self, package_file):
		for description in '\n\n'.split (open (package_file).read ()):
			self.register_package (self.debian_package (description))
			
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
		t = {
			'Package' : 'name',
			'Version' : 'ball_version',
			'Depends' : 'name_dependencies',
			'Filename' : 'url',
			}

		package.name_dependencies = []
		if d.has_key ('Depends'):
			# not changing package name - _ helps in
			# resolving dependencies
			package.name_dependencies = map (string.strip,
							 re.sub ('-', '-',
							re.sub ('\([^\)]*\)',
								'',
							d['Depends'])).split (', '))
			# FIXME: BARF, ignore choices
			package.name_dependencies = filter (lambda x: x.find ('|') == -1,
							    package.name_dependencies)
					
		package.ball_version = d['Version']
		package.xxurl = (self.pool
			       + '/%(Filename)s_%(Version)s_%(Architecture)s.deb'
			       % d)
		package.url = self.pool + '/' + d['Filename']
		package.format = 'deb'
		return package

def get_manager (settings):
	target_manager = Package_manager (settings.system_root,
					  settings.os_interface)

	cross_module = None
	if settings.platform == 'darwin':
		import darwintools
		cross_module = darwintools
	if settings.platform.startswith ('freebsd'):
		import freebsd
		cross_module = freebsd
	elif settings.platform.startswith ("linux"):
		import linux
		cross_module = linux
	elif settings.platform.startswith ('mingw'):
		import mingw
		cross_module = mingw
	elif settings.platform.startswith ('local'):
		import tools
		cross_module = tools
	elif settings.platform.startswith ('debian'):
		import debian_unstable
		cross_module = debian_unstable

	map (target_manager.register_package, cross_module.get_packages (settings))
	# FIXME: only resolve necessary dependencies.
	# actually, we should only ever look at:
	#   - lilypond
	#   - ghostscript
	#   - lilypad
	#   - python
	# all other libraries should be examined automatically as a dependency
	# map (target_manager.register_package, framework.get_packages (settings))
	fp = framework.get_packages (settings)
	map (target_manager.register_package, fp)

	for m in (target_manager,):
		#m.resolve_dependencies (fp)
		for p in m._packages.values ():
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
