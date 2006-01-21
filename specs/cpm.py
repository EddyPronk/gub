import os
import pickle
import re
import stat
import string
import sys
import time
import gzip

def debug (s):
	s


# Cygwin stuff

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

def run_script (file_name):
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
	def itoa (x):
		if type (x) == int:
			return "%d" % x
		return x
	return '%s-%s' % (string.join (map (itoa, t[:-1]), '.'), t[-1])

def string_to_version (s):
	s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
	s = re.sub ('[ _.-][ _.-]*', ' ', s)
	s = s.strip ()
	def atoi (x):
		if re.match ('^[0-9]+$', x):
			return string.atoi (x)
		return x
	return tuple (map (atoi, (string.split (s, ' '))))

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
		self._setup_ini = self.config + '/setup.ini'
		self._installed = None
		self._depends = {}
		self._dists = None
		self.installed ()
		self.setup ()

	def _write_installed (self):
		file = open (self._installed_db, 'w')
		file.write (self.installed_db_magic)
		file.writelines (map (lambda x: '%s %s 0\n' \
				      % (x, self._installed[x]),
				      self._installed.keys ()))
		status = file.close ()

		if status:
			raise 'file.close(): %d' % status

	def _load_installed (self):
		self._installed = {}
		if os.path.isfile (self._installed_db):
			for i in open (self._installed_db).readlines ()[1:]:
				name, ball, status = string.split (i)
				##self._installed[int (status)][name] = ball
				self._installed[name] = ball

	def setup (self, setup_ini=None):
		if setup_ini:
			self._setup_ini = setup_ini
		if not os.path.isdir (self.config):
			sys.stderr.write ('creating %s\n' % self.config)
			os.makedirs (self.config)
			self._load_installed ()
		if not os.path.exists (self._installed_db):
			self._write_installed ()

	def filelist (self, name):
		list_file = "%s/%s.lst.gz" % (self.config, name)
		return [l[:-1] for l in gzip.open (list_file).readlines ()]

	def _write_filelist (self, lst, name):
		lst_name = '%s/%s.lst.gz' % (self.config, name)
		f = gzip.open (lst_name, 'w')
		for i in lst:
			f.write ('%s\n' % i)

		
	def installed (self):
		if self._installed == None:
			self._load_installed ()
		return self._installed

	def is_installed (self, name):
		return name in self._installed.keys ()

	def version (self, name):
		if name in self._installed.keys ():
			return split_ball (self.installed ()[name])[1]
		return 0, 0

	def _install (self, name, ball, depends=[]):
		if cygwin_p and name in ('cygwin', 'python'):
			sys.stderr.write ('error: cannot install on Cygwin: '
					  + name)
			sys.stderr.write ('\n')
			raise 'urg'
		root = self.root
		z = self.compression
		pipe = os.popen ('tar -C "%(root)s" -%(z)sxvf "%(ball)s"' \
				 % locals (), 'r')
		lst = map (string.strip, pipe.readlines ())
		status = pipe.close ()
		if status:
			raise '_install(): pipe close %d' % status
		
		self._write_filelist (lst, name)
		self._installed[name] = os.path.basename (ball)
		self._depends[name] = depends
		self._write_installed ()

	def install (self, name, ball, depends=[]):
		##if self.installed ().has_key (name):
		## Fixme: huh?
		if self.installed ().has_key (name):
			sys.stderr.write ('uninstalling: ' + name)
			sys.stderr.write ('\n')
			self.uninstall (name)
		sys.stderr.write ('installing: ' + name)
		sys.stderr.write ('\n')
		self._install (name, ball, depends)
		self.run_scripts ()

	def uninstall (self, name):
		if cygwin_p and name in ('cygwin', 'python'):
			sys.stderr.write ('error: cannot uninstall on Cygwin: '
					  + name)
			sys.stderr.write ('\n')
			raise 'urg'
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

	def dists (self):
		if not self._dists:
			self._read_setup_ini (self._setup_ini)
		return self._dists

	def _read_setup_ini (self, setup_ini):
		self._dists = {'test': {}, 'curr': {}, 'prev' : {}}
		chunks = string.split (open (setup_ini).read (), '\n\n@ ')
		for i in chunks[1:]:
			lines = string.split (i, '\n')
			name = string.strip (lines[0])
			debug ('package: ' + name)
			packages = self._dists['curr']
			records = {'sdesc': name}
			j = 1
			while j < len (lines) and string.strip (lines[j]):
				debug ('raw: ' + lines[j])
				if lines[j][0] == '#':
					j = j + 1
					continue
				elif lines[j][0] == '[':
					debug ('dist: ' + lines[j][1:5])
					packages[name] = records.copy ()
					packages = self._dists[lines[j][1:5]]
					j = j + 1
					continue

				try:
					key, value = map (string.strip,
						  string.split (lines[j], ': ', 1))
				except:
					print lines[j], setup_ini, self
					raise 'URG'
				if value.startswith ('"') and value.find ('"', 1) == -1:
					while 1:
						j = j + 1
						value += '\n' + lines[j]
						if lines[j].find ('"') != -1:
							break
				records[key] = value
				j = j + 1
			packages[name] = records

class Gpm (Cpm):
	'''Gub package manager.

	Reusing Cygwin package management.'''
	compression = 'z'
	def __init__ (self, root):
		Cpm.__init__ (self, root)

	def _write_installed (self):
		file = open (self._installed_db, 'w')

		# todo, use eval , `obj` ? 
		pickle.dump (self._installed, file)

	def _load_installed (self):
		if not os.path.isfile (self._installed_db):
			self._installed = {}
		else:
			self._installed = pickle.load (open (self._installed_db))

	def xxxsimple_read_setup_ini (self, setup_ini):
		packages = {}
		if os.path.exists (setup_ini):
			chunks = string.split (open (setup_ini).read (),
					       '\n\n@ ')
			for i in chunks[1:]:
				name = i[:i.find ('\n')]
				packages[name] = i
		return packages

	def write_setup_ini (self, setup_ini):
		now = `time.time ()`
		now = now[:now.find ('.')]
		s = '''setup-timestamp: %(now)s
''' % locals ()
		packages = self._read_setup_ini (setup_ini)
		for name in packages.keys ():
			if name not in self.installed ().keys ():
				s += '\n\n@ ' + packages[name]

		for name in self.installed ().keys ():
			Name = name[0].upper () + name[1:]
			ball = self.installed ()[name]
			version = version_to_string (split_ball (ball)[1])
			uploads = 'uploads'
			dir = 'gub'
			depends = ''
			if self._depends.has_key (name):
				depends = string.join (self._depends[name])
			pipe = os.popen ('md5sum "%(uploads)s/%(dir)s/%(ball)s"' \
					 % locals ())
			size = os.stat (os.path.join (uploads, dir, ball))[stat.ST_SIZE]
			md5 = string.split (pipe.read ())[0]
			# FIXME: TODO build-requires from old mingw-installer
			# fine-grained libFOOx.y, FOO-devel, FOO-doc package
			# splitting from old mingw-installer?
			s += '''
@ %(name)s
sdesc: "%(Name)s"
ldesc: "%(Name)s - no description available"
requires: %(depends)s
version: %(version)s
install: %(dir)s/%(ball)s %(size)d %(md5)s
source: TBD
''' % locals ()
		f = open (setup_ini, 'w')
		f.write (s)
		f.close ()
