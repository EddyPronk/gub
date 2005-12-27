import re
import gzip
import os

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

	def is_installable (self, package):
		ball = package.expand ('%(gub_uploads)s/%(gub_name)s')
		return os.path.exists (ball)

	def register_package (self, pkg):
		self._packages[pkg.name()] = pkg

	def installed_packages (self):
		(root, dirs, files) = os.walk (self.config).next ()

		lists = []
		for f in files:
			m = re.match ('(.*).lst.gz', f)
			if m:
				lists.append (m.group (1))

		return [self._packages[p] for p in lists]

	def tarball_files (self, ball):
		flag = tar_compression_flag (ball)
		str = self.os_interface.read_pipe ('tar -tf%(flag)s "%(ball)s"'
						   % locals (), silent=True)

		lst = str.split ('\n')
		return lst

	def installed_files (self, package):
		return self._read_list_file (package)

	def uninstall_package (self, package):
		for (nm, p) in self._packages.items():
			if (package.name () in p.dependencies
			    and self.is_installed (p)):
				raise ('Package %s depends on %s'
				       % (`p`, `package`))

		self.uninstall_single_package (package)

	def uninstall_single_package (self, package):
		self.os_interface.log_command ('uninstalling package %s\n' % `package`)

		listfile = self.file_list_name (package)
		lst = self.installed_files (package)
		dirs = []
		for l in lst:
			f = os.path.join (self.root, l)
			if os.path.isdir (f):
				dirs.append (f)
			else:
				os.unlink (f)

		for d in reversed (dirs):
			try:
				os.rmdir (d)
			except OSError:
				print 'warning: %s not empty' % d

		os.unlink (listfile)

	def file_list_name (self, package):
		return '%s/%s.lst.gz' % (self.config, package.name ())

	def is_installed (self, package):
		return os.path.exists (self.file_list_name (package))

	def install_single_package (self, package):
		ball = package.expand ('%(gub_uploads)s/%(gub_name)s')
		name = package.name ()

		self.os_interface.log_command ('installing package %(name)s from %(ball)s\n'
					       % locals ())

		flag = tar_compression_flag (ball)
		root = self.root

		self.os_interface.system ('tar -C %(root)s -xf%(flag)s %(ball)s' % locals ())

		lst = self.tarball_files (ball)
		print 'list: ' + `lst[:10]`
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
		for d in package.dependencies:
			if (not self.is_installed (d)
			    and self._packages.has_key (d.name ())):
				self.install_package (d)

	def install_package (self, package):
		self.install_dependencies (package)
		self.install_single_package (package)

	def resolve_dependencies (self):
		try:
			for p in self._packages.values ():
				p.dependencies = [self._packages[d] for d in p.name_dependencies]
				if p in p.dependencies:
					print 'circular dependency', p, p.name_dependencies, p.dependencies, self._packages
					raise 'BARF'
				
		except KeyError, k:
			print 'Unknown package %s. I know about: ' % k, self._packages
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
		



def get_managers (settings):
	tool_manager = Package_manager (settings.tooldir, settings.os_interface)
	target_manager = Package_manager (settings.system_root, settings.os_interface)

	if settings.platform == 'darwin':
		import darwintools
		
		map (tool_manager.register_package,
		     darwintools.get_packages (settings))
	if settings.platform.startswith ('mingw'):
		import mingw
		map (tool_manager.register_package,
		     mingw.get_packages (settings))

	map (target_manager.register_package, framework.get_packages (settings))

	for m in tool_manager, target_manager:
		m.resolve_dependencies ()
		for p in m._packages.values():
			settings.build_number_db.set_build_number (p)

	return tool_manager, target_manager

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
