import inspect
import os
import time
import sys
import subprocess
import re
import stat

def subst_method (func):
	"""Decorator to match Context.get_substitution_dict()"""
	
	func.substitute_me = True
	return func

def is_subst_method_in_class (method_name, klass):
	bs = [k for k in klass.__bases__ if is_subst_method_in_class (method_name, k)]
	if bs:
		return True
	
	if (klass.__dict__.has_key(method_name)
	    and callable (klass.__dict__[method_name])
	    and klass.__dict__[method_name].__dict__.has_key ('substitute_me')):
		return True

	return False

def typecheck_substitution_dict (d):
	for (k, v) in d.items ():
		if type (v) != type(''):
			raise 'type', (k, v)

def recurse_substitutions (d):
	for (k, v) in d.items ():
		if type(v) != type(''):
			del d[k]
			continue

		try:
			while v.index ('%(') >= 0:
				v = v % d
		except ValueError:
			pass
		d[k] = v

	return d

class Context:
	def __init__ (self, parent = None):
		self._substitution_dict = None
		self._parent = parent

	def get_constant_substitution_dict (self):
		d = {}
		if self._parent:
			d = self._parent.get_substitution_dict ()
			d = d.copy ()
			
		ms = inspect.getmembers (self)
		vars = dict((k, v) for (k, v) in ms if type(v) == type(''))
		member_substs = dict((k, v ()) for (k, v) in ms if callable (v)
				      and is_subst_method_in_class (k, self.__class__))
		
		d.update (vars)
		d.update (member_substs)

#		typecheck_substitution_dict(d)
		d =  recurse_substitutions (d)


		return d

	def get_substitution_dict (self, env={}):
		if  self._substitution_dict == None:
			self._substitution_dict = self.get_constant_substitution_dict ()

		d = self._substitution_dict
		if env:
			d = d.copy ()
			d.update ((k, v % d) for (k, v) in env.items () if type(v) == type(''))
			
		return d
	
	def expand (self, s, env={}):
		d = self.get_substitution_dict (env)
		return s % d

def now ():
	return time.asctime (time.localtime ())


class Os_commands:
	"""Encapsulate OS/File system commands for proper logging. """
	
	def __init__ (self, logfile):
		self.log_file = open (logfile, 'a')
		self.log_file.write ('\n\n * Starting build: %s\n' %  now ())

	def system_one (self, cmd, env, ignore_error):
		self.log_command ('invoking %s\n' % cmd)

		proc = subprocess.Popen (cmd, shell=True, env=env,
					 stderr=subprocess.STDOUT)

		stat = proc.wait()

		if stat and not ignore_error:
			m = 'Command barfed: %s\n' % cmd
			self.log_command (m)
			raise m

		return 0

	def log_command (self, str):
		sys.stderr.write (str)
		if self.log_file:
			self.log_file.write (str)
			self.log_file.flush ()
		

	def system (self, cmd, env={}, ignore_error=False, verbose=False):
		"""Run multiple lines as multiple commands.
		"""

		call_env = os.environ.copy ()
		call_env.update (env)

		if verbose:
			keys =env.keys()
			keys.sort()
			for k in keys:
				sys.stderr.write ('%s=%s\n' % (k, env[k]))

			sys.stderr.write ('export %s\n' % ' '.join (keys))
		for i in cmd.split ('\n'):
			if i:
				self.system_one (i, call_env, ignore_error)

		return 0

	def dump (self, str, name, mode='w'):
		self.log_command ("Writing %s\n" % name)
		
		f = open (name, mode)
		f.write (str)
		f.close ()

	def file_sub (self, re_pairs, name, to_name=None, env={}, must_succeed=False):

		self.log_command ('substituting in %s\n' % name)
		self.log_command (''.join (map (lambda x: "'%s' -> '%s'\n" % x,
					   re_pairs)))

		s = open (name).read ()
		t = s
		for frm, to in re_pairs:
			new_text = re.sub (re.compile (frm, re.MULTILINE), to, t)
			if (t == new_text and must_succeed):
				raise 'nothing changed!'
			t = new_text
			
		if s != t or (to_name and name != to_name):
			stat_info = os.stat(name)
			mode = stat.S_IMODE(stat_info[stat.ST_MODE])

			if not to_name:
				self.system ('mv %(name)s %(name)s~' % locals ())
				to_name = name
			h = open (to_name, 'w')
			h.write (t)
			h.close ()
			os.chmod (to_name, mode)
			
	def read_pipe (self, cmd, ignore_error=False, silent=False):
		if not silent:
			self.log_command ('Reading pipe: %s\n' % cmd)

		pipe = os.popen (cmd, 'r')
		output = pipe.read ()
		status = pipe.close ()
		# successful pipe close returns None
		if not ignore_error and status:
			raise 'read_pipe failed'
		return output


	def shadow_tree (self, src, target):
		target = os.path.abspath (target)
		src = os.path.abspath (src)

		self.log_command ("Shadowing %s to %s\n" % (src, target))
		os.makedirs (target)
		(root, dirs, files) = os.walk(src).next()
		for f in files:
			os.symlink (os.path.join (root, f),
				    os.path.join (target, f))
		for d in dirs:
			self.shadow_tree (os.path.join (root, d),
					  os.path.join (target, d))

class Os_context_wrapper (Context):
	def __init__ (self, settings):
		Context.__init__ (self, settings)
		self.os_interface = settings.os_interface
		self.verbose = settings.verbose ()
		
	def file_sub (self, re_pairs, name, to_name=None, env={}, must_succeed=False):

		substs = []
		for (frm, to) in re_pairs:
			frm = self.expand (frm, env)
			if type (to) ==type(''):
				to = self.expand (to, env)

			substs.append ((frm, to))

		if to_name:
			to_name = self.expand (to_name, env)
			
		return self.os_interface.file_sub (substs, self.expand (name, env), to_name, must_succeed)
	def log_command (self, str, env={}):
		str = self.expand (str, env)
		self.os_interface.log_command (str)
		
	def read_pipe (self, cmd, env={}, ignore_error=False):
		dict = self.get_substitution_dict (env)
		return self.os_interface.read_pipe (cmd % dict, ignore_error=ignore_error)

	def system (self, cmd, env={}, ignore_error=False):
		dict = self.get_substitution_dict (env)
		cmd = self.expand (cmd, env)
		self.os_interface.system (cmd, env=dict, ignore_error=ignore_error,
					  verbose=self.verbose)

	def shadow_tree (self, src, dest):
		src = self.expand (src)
		dest = self.expand (dest)
		self.os_interface.shadow_tree (src, dest)
		
	def dump (self, str, name, mode='w', env={}):
		return self.os_interface.dump (self.expand (str, env),
			     self.expand (name, env), mode=mode)
	
	def locate_files (self, directory, pattern):
		command = "cd %(directory)s && find -name '%(pattern)s'" % locals()
		return [f for f in  self.read_pipe (command).split ('\n') if f.strip()]

if __name__=='__main__':
	class TestBase(Context):
		@subst_method
		def bladir(self):
			return 'foo'
		
	class TestClass(TestBase):
		@subst_method
		def name(self):
			return self.__class__.__name__
		
		def bladir(self):
			return 'derivedbladir'

	p = TestClass ()

	print p.expand ('%(name)s %(bladir)s')
