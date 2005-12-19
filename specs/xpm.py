import re
import gzip
import pickle
import os
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
	def __init__ (self, root):
		self.root = root
		self._packages = {}
		self.config = self.root + '/etc/xpm/'
		if not os.path.isdir (self.config):
			gub.system ('mkdir -p %s' % self.config)

	def is_installable (self, package):
		ball = package.expand_string ('%(gub_uploads)s/%(gub_name)s')
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

	def get_tarball_file_list (self, ball):
		flag = tar_compression_flag (ball)
		str = gub.read_pipe ('tar -tf%(flag)s "%(ball)s"'
				     % locals (), silent=True)

		lst = str.split ('\n')
		return lst

	def installed_files (self, package):
		listfile = self.file_list_name (package)

		f = gzip.open (listfile, 'r')
		lst = pickle.load (f)
		return lst

	def uninstall_package (self, package):
		for (nm, p) in self._packages.items():
			if (package.name () in p.dependencies
			    and self.is_installed (p)):
				raise ('Package %s depends on %s'
				       % (`p`, `package`))

		self.uninstall_single_package (package)

	def uninstall_single_package (self, package):
		gub.log_command ('uninstalling package %s\n' % `package`)

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
		ball = package.expand_string ('%(gub_uploads)s/%(gub_name)s')
		gub.log_command ('installing package from %s\n' % ball)

		flag = tar_compression_flag (ball)
		root = self.root

		gub.system ('tar -C %(root)s -xf%(flag)s %(ball)s' % locals ())

		lst = self.get_tarball_file_list (ball)
		listfile = self.file_list_name (package)
		f = gzip.open (listfile, 'w')
		pickle.dump (lst, f)

	def install_dependencies (self, package):
		for d in package.dependencies:
			if (not self.is_installed (d)
			    and self._packages.has_key (d.name ())):
				self.install_package (d)

	def install_package (self, package):
		self.install_dependencies (package)
		self.install_single_package (package)

	def resolve_dependencies (self):
		for p in self._packages.values ():
			p.dependencies = [self._packages[d] for d in p.dependencies]

	# NAME_ shortcuts
	def name_files (self, name):
		return self.installed_files (self._packages[name])
	def name_install (self, name):
		self.install_package (self._packages[name])
	def name_uninstall (self, name):
		self.uninstall_package (self._packages[name])
	def name_is_installed (self, name):
		return self.is_installed (self._packages[name])

