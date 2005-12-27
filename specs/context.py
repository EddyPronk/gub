import inspect

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

def typecheck_substitution_dict(d):
	for (k,v) in d.items():
		if type (v) <> type(''):
			raise 'type', (k, v)

class Context:
	def __init__ (self, parent = None):
		self._substitution_dict = None
		self._parent = parent

	def get_constant_substitution_dict (self):
		d = {}
		if self._parent:
			d = self._parent.get_substitution_dict ()
		
		ms = inspect.getmembers(self)
		vars = (dict([(k,v) for (k, v) in ms if type(v) == type('')]))
		member_substs = dict([(k, v()) for (k,v) in ms if callable(v)
				      and is_subst_method_in_class (k, self.__class__)])
		
		d.update (vars)
		d.update (member_substs)

#		typecheck_substitution_dict(d)

		for (k,v) in d.items ():
			if type(v) <> type(''):
				del d[k]
				continue
			try:
				while v.index ('%(') >= 0:
					v = v % d
			except ValueError:
				pass
			d[k] = v
			
		
		return d

	def get_substitution_dict (self, env={}):
		if  self._substitution_dict == None:
			self._substitution_dict  = self.get_constant_substitution_dict ()

		d = self._substitution_dict
		if env:
			d = d.copy()
			d.update ([(k,v % d) for (k,v) in env.items() if type(v)==type('')])
			
		return d
	
	def expand (self, s, env={}):
		d = self.get_substitution_dict (env)
		return s % d


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
