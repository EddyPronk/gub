import os
import pickle
import re
import string
import sys

try:
	fake_pipe = 0
	date = os.popen ('date').read ()
except:
	# Work around Cygwin-Python pipe brokenness
	##import tempfile
	def fake_pipe (command, mode = 'r'):
		if mode == 'w':
			raise 'ugh'
		##h, name = tempfile.mkstemp ('pipe', basename, '/tmp')x
		name = ('/tmp/%s.%d' % ('cyg-apt', os.getpid ()))
		system (command + ' > ' + name)
		return open (name)
	os.popen = fake_pipe
	pass


# cygwin stuff

def run_script (self, file_name):
	 sys.stderr.write ('running: %(file_name)s\n' % vars ())
	 system ('sh "%(file_name)s" && mv "%(file_name)s" "%(file_name)s.done"' % vars ())

def try_run_script (file_name):
	if os.path.isfile (file_name):
		if cygwin_p:
			run_script (file_name)
		else:
			sys.stderr.write ('warning: please see after: %(file_name)s' % vars ())
			sys.stderr.write ('\n')

def run_all (dir):
	if os.path.isdir (dir):
		#lst = filter (lambda x: x[-5:] != '.done', os.listdir (dir))
		lst = filter (lambda x: x[-3:] == '.sh', os.listdir (dir))
		for i in lst:
			try_run_script ('%s/%s' % (dir, i))

def version_to_string (t):
	def try_itoa (x):
		if type (x) == int:
			return "%d" % x
		return x
	return '%s-%s' % (string.join (map (try_itoa, t[:-1]), '.'), t[-1])

def string_to_version (s):
	s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
	s = re.sub ('[ _.-][ _.-]*', ' ', s)
	def try_atoi (x):
		if re.match ('^[0-9]*$', x):
			return string.atoi (x)
		return x
	return tuple (map (try_atoi, (string.split (s, ' '))))

def split_version (s):
	m = re.match ('^(([0-9].*)-([0-9]+))$', s)
	if m:
		return m.group (2), m.group (3)
	return s, '0'

def split_ball (s):
	m = re.match ('^(.*?)-([0-9].*(-[0-9]+)?)(\.tar\.bz2|\.[a-z]*\.gub)$', s)
	if not m:
		sys.stderr.write ('split_ball: ') + s
		sys.stderr.write ('\n')
		return (s[:2], (0, 0))
	return (m.group (1), string_to_version (string.join (split_version (m.group (2)), '-')))

def join_ball (t):
	return t[0] + '-' + version_to_string (t[1])

class Cpm:
	'''Cygwin package manager.

	Works on native Cygwin and cross Cygwin trees.
	'''
	installed_db_magic = 'INSTALLED.DB 2\n'
	compression = 'j'
	def __init__ (self, root):
		self.root = root
		self.config = self.root + '/etc/setup'
		self._installed_db = self.config + '/installed.db'
		self._installed = None
		self.setup ()

	def _write_installed (self):
		file = open (self._installed_db, 'w')
		file.write (self.installed_db_magic)
		file.writelines (map (lambda x: '%s %s 0\n' \
				      % (x, self._installed[x]),
				      self._installed.keys ()))
		if file.close ():
			raise 'urg'

	def _load_installed (self):
		self._installed = {}
		if os.path.isfile (self._installed_db):
			for i in open (self._installed_db).readlines ()[1:]:
				name, ball, status = string.split (i)
				##self._installed[int (status)][name] = ball
				self._installed[name] = ball

	def setup (self):
		if not os.path.isdir (self.config):
			sys.stderr.write ('creating %s\n' % self.config)
			os.makedirs (self.config)
			self._load_installed ()
		if not os.path.exists (self._installed_db):
			self._write_installed ()

	def filelist (self, name):
		pipe = os.popen ('gzip -dc "%s/%s.lst.gz"' % (self.config,
							      name), 'r')
		lst = map (string.strip, pipe.readlines ())
		if pipe.close ():
			raise 'urg'
		return lst

	def _write_filelist (self, lst, name):
		lst_name = '%s/%s.lst' % (self.config, name)
		if not fake_pipe:
			pipe = os.popen ('gzip -c > "%s.gz"' % lst_name, 'w')
		else:
			pipe = open (lst_name, 'w')
		for i in lst:
			pipe.write (i)
			pipe.write ('\n')
		if pipe.close ():
			raise 'urg'
		if fake_pipe:
			system ('gzip -f "%s"' % lst_name)
		
	def installed (self):
		if self._installed == None:
			self._load_installed ()
		return self._installed

	def _install (self, name, ball):
		root = self.root
		z = self.compression
		pipe = os.popen ('tar -C "%(root)s" -%(z)sxvf "%(ball)s"' \
				 % locals (), 'r')
		lst = map (string.strip, pipe.readlines ())
		if pipe.close ():
			raise 'urg'
		self._write_filelist (lst, name)
		self._installed[name] = os.path.basename (ball)
		self._write_installed ()

	def install (self, name, ball):
		if self.installed ().has_key (name):
			sys.stderr.write ('uninstalling: ' + name)
			sys.stderr.write ('\n')
			self.uninstall (name)
		sys.stderr.write ('installing: ' + name)
		sys.stderr.write ('\n')
		self._install (name, ball)
		self.run_scripts ()

	def uninstall (self, name):
		# FIXME: cygwin stuff
		try_run_script (self.root + '/etc/preremove/%s.sh' % name)
		postremove = self.root + '/etc/postremove/%s.sh' % name
		lst = self.filelist (name)
		for i in lst:
			file = os.path.join (self.root, i)
			if not os.path.exists (file) and not os.path.islink (file):
				sys.stderr.write ('warning: %s no such file\n' % file)
			elif not os.path.isdir (file) and file != postremove:
				if os.remove (file):
					raise 'urg'

		try_run_script (postremove)
		if os.path.isfile (postremove):
			if os.remove (postremove):
				raise 'urg'

		# remove empty dirs?
		self._write_filelist ([], name)
		del (self._installed[name])
		self._write_installed ()

	def run_scripts (self):
		run_all (self.root + '/etc/postinstall')

class Gpm (Cpm):
	'''Gub package manager.

	Reusing Cygwin package management.'''
	compression = 'z'
	def __init__ (self, root):
		Cpm.__init__ (self, root)
		self._installed_db = self.config + '/installed.pickle'

	def _write_installed (self):
		file = open (self._installed_db, 'w')
		pickle.dump (self._installed, file)

	def _load_installed (self):
		if not os.path.isfile (self._installed_db):
			self._installed = {}
		else:
			self._installed = pickle.load (open (self._installed_db))
