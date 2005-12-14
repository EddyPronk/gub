import os
import string
import sys
import pickle

cygwin_p = 0
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

class Cpm:
	def __init__ (self, root):
		self.root = root
		self.config = self.root + '/etc/setup'
		self._installed_db = self.config + '/installed.db'
		self._installed = None
		self.setup ()
		self.installed ()

	def _write_installed (self):
		file = open (self._installed_db, 'w')
		pickle.dump (self._installed, file)
	def load_installed (self):
		if not os.path.isfile (self._installed_db):
			self._installed = {}
		else:
			pickle.load (open (self._installed_db))


	def setup (self):
		if not os.path.isdir (self.config):
			sys.stderr.write ('creating %s\n' % self.config)
			os.makedirs (self.config)

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
			self.load_installed ()

		return self._installed

	def _install (self, name, ball):
		root = self.root
		## FIXME
		z = 'z'
		if cygwin_p:
			z = 'j'
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

