import gdbm as dbmodule
#import dbhash as dbmodule

import pickle
import dbhash
import gzip
import os
import re
import string
import fcntl
import sys
import imp
import glob

#
import cross
import framework
import gub
import targetpackage
from misc import *  # URG, fixme
import cygwin



class File_manager:
	def __init__ (self, root, os_interface, dbdir=None):
		self.root = root
		if dbdir:
			self.config = dbdir
		else:
			self.config = self.root + '/etc/xpm/'
			
		self.os_interface = os_interface
		self.verbose = True
		self.is_distro = False

		if not os.path.isdir (self.config):
			os_interface.system ('mkdir -p %s' % self.config)
		if not os.path.isdir (self.root):
			os_interface.system ('mkdir -p %s' % self.root)

		lock_file = self.config + 'lock'
		self._lock_file = open (lock_file, 'w')

		try:
			fcntl.flock (self._lock_file.fileno (),
				     fcntl.LOCK_EX | fcntl.LOCK_NB)
		except IOError:
			sys.stderr.write ("Can't acquire Package_manager lock %s\n\nAbort\n" % lock_file)
			sys.exit (1)

		self._file_package_db = dbmodule.open (self.config
						       + '/files.db', 'c')
		self._package_file_db = dbmodule.open (self.config
						       + '/packages.db', 'c')
		
	def __repr__ (self):
		name = self.__class__.__name__
		root = self.root
		distro =  self.is_distro
		return '%(name)s: %(root)s, distro: %(distro)d build: %(build)d'  % locals()

	def tarball_files (self, ball):
		flag = tar_compression_flag (ball)
		str = self.os_interface.read_pipe ('tar -tf%(flag)s "%(ball)s"'
						   % locals (), silent=True)
		lst = str.split ('\n')
		return lst

	def installed_files (self, package):
		return self._package_file_db[package].split ('\n')

	def is_installed (self, name):
		return self._package_file_db.has_key (name)

	def install_tarball (self, ball, name):
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

		if conflicts and not self.is_distro:
			raise 'abort'

		self.os_interface.system ('tar -C %(root)s -xf%(flag)s %(ball)s' % locals ())

		self._package_file_db[name] = '\n'.join (lst)
		for f in lst:

			# ignore directories.
			if f and  f[-1] != '/':
				self._file_package_db[f] = name

	def uninstall_package (self, name):
		self.os_interface.log_command ('uninstalling package: %s\n' % name)

		lst = self.installed_files (name)

		dirs = []
		files = []
		for i in lst:
			f = os.path.join (self.root, i)
			if os.path.islink (f):
				files.append (f)
			elif (not os.path.exists (f)
			      and not self.is_distro):
				print 'xpm: uninstall: %s' % name
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

	def installed_package_dicts (self):
		names = self._package_file_db.keys ()
		return [self._packages[p] for p in names]

	def installed_packages (self):
		names = self._package_file_db.keys ()
		return names

class Package_manager (File_manager):
	def __init__ (self, root, os_interface, dbdir=None):
		File_manager.__init__ (self, root, os_interface, dbdir)

		self._package_dict_db = dbmodule.open (self.config
						       + '/dicts.db', 'c')
		self._packages = {}
		for k in self._package_dict_db.keys ():
			v = self._package_dict_db[k]
			self.register_package_dict (pickle.loads (v))

	def register_package_dict (self, d):
		nm = d['name']
		if (self._packages.has_key (nm)):
			if self._packages[nm]['checksum'] != d['checksum']:
				self.os_interface.log_command ('******** checksum of %s changed!\n\n' % nm)
			if self._packages[nm]['cross_checksum'] != d['cross_checksum']:
				self.os_interface.log_command ('******** checksum of cross changed for %s\n' % nm)
			return

		self._packages[nm] = d

	def register_package_header (self, package_hdr, branch):
		str = open (package_hdr).read ()

		d = pickle.loads (str)


		## FIXME: take out has_key
		if (d.has_key ("cvs_branch") and branch <> d['cvs_branch']):
			print 'ignoring header for wrong branch', package_hdr
			return
		
		
		if self._package_dict_db.has_key (d['name']):
			if str != self._package_dict_db[d['name']]:
				self.os_interface.log_command ("package header changed for %(name)s\n" % d)

			return

		if self.verbose:
			self.os_interface.log_command ('registering package: %s\n'
						       % `package_hdr`)

		self.register_package_dict (d)

	def read_package_headers (self, dir, branch):
		for f in glob.glob ('%s/*hdr' % dir):
			self.register_package_header (f, branch)

	def is_installable (self, name):
		d = self._packages[name]

		ball = '%(gub_ball)s' % d
		hdr = '%(hdr_file)s' % d
		return os.path.exists (ball) and os.path.exists (ball)

	def install_package (self, name):
		if self.is_installed (name):
			return
		self.os_interface.log_command ('installing package: %s\n'
					       % name)
		if self._package_file_db.has_key (name):
			print 'already have package ', name
			raise 'abort'
		d = self._packages[name]
		ball = '%(gub_ball)s' % d
		self.install_tarball (ball, name)
		self._package_dict_db[name] = pickle.dumps (d)

	def uninstall_package (self, name):
		File_manager.uninstall_package (self, name)
		del self._package_dict_db[name]

	def is_registered (self, package):
		return self._packages.has_key (package)

	def package_dict (self, package_name):
		return self._packages[package_name]
	
def is_string (x):
	return type (x) == type ('')

class Dependency_manager (Package_manager):

	"Manage packages that have dependencies and build_dependencies."

	def __init__ (self, root, os_interface, dbdir=None):
		Package_manager.__init__ (self, root, os_interface, dbdir)
		self.include_build_deps = True

	def dependencies (self, name):
		assert is_string (name)
		try:
			return self.dict_dependencies (self._packages[name])
		except KeyError:
			print 'unknown package', name
			return []

	def dict_dependencies (self, dict):
		deps = dict['dependencies_string'].split (';')
		if self.include_build_deps:
			deps += dict['build_dependencies_string'].split (';')

		deps = [d for d in deps if d]
		return deps

################
# UGh moveme

def topologically_sorted_one (todo, done, dependency_getter,
			      recurse_stop_predicate=None):
	sorted = []
	if done.has_key (todo):
		return sorted

	done[todo] = 1

	deps = dependency_getter (todo)
	for d in deps:
		if recurse_stop_predicate and recurse_stop_predicate (d):
			continue

		assert type(d) == type (todo)
		
		sorted += topologically_sorted_one (d, done, dependency_getter,
						    recurse_stop_predicate=recurse_stop_predicate)

	sorted.append (todo)
	return sorted

def topologically_sorted (todo, done, dependency_getter,
			  recurse_stop_predicate=None):
	s = []
	for t in todo:
		s += topologically_sorted_one (t, done, dependency_getter,
					       recurse_stop_predicate)

	return s


################################################################
# UGH
# this is too hairy. --hwn
def get_packages (settings, todo):
	cross_packages = cross.get_cross_packages (settings)
	pack_dict = dict ((p.name (), p) for p in cross_packages)


	def name_to_dependencies_via_gub (name):
		try:
			pack = pack_dict[name]
		except KeyError:
			pack = targetpackage.load_target_package (settings, name)
			pack_dict[name] = pack

		retval = pack.name_dependencies + pack.name_build_dependencies
		return retval

	def name_to_dependencies_via_cygwin (name):
		try:
			pack = pack_dict [name]
		except KeyError:
			try:
				pack = cygwin.cygwin_name_to_dependency_names (name)
			except KeyError:
				pack = targetpackage.load_target_package (settings, name)

		pack_dict[name] = pack

		return pack.name_dependencies + pack.name_build_dependencies

	todo += pack_dict.keys ()

	name_to_deps = name_to_dependencies_via_gub
	if settings.platform == 'cygwin':
		cygwin.init_cygwin_package_finder (settings)
		name_to_deps = name_to_dependencies_via_cygwin
		
	package_names = topologically_sorted (todo, {}, name_to_deps)
	pack_dict = dict ((n,pack_dict[n]) for n in package_names)

	cross.set_cross_dependencies (pack_dict)

	## sort for cross deps too.

	def obj_to_dependency_objects (obj):
		return [pack_dict[n] for n in obj.name_dependencies
			+ obj.name_build_dependencies]
	
	package_objs = topologically_sorted (pack_dict.values (), {},
					     obj_to_dependency_objects)

	framework.version_fixups (settings, package_objs)

	return ([o.name () for o in package_objs], pack_dict)







def get_target_manager (settings):
	target_manager = Dependency_manager (settings.system_root,
					     settings.os_interface)
	return target_manager

def add_packages_to_manager (target_manager, settings, package_object_dict):

	## Ugh, this sucks: we now have to have all packages
	## registered at the same time.

	cross_module = cross.get_cross_module (settings.platform)
	cross_module.change_target_packages (package_object_dict)

	for p in package_object_dict.values ():
		target_manager.register_package_dict (p.get_substitution_dict ())

	return target_manager
