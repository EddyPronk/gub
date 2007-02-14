import inspect
import os
import re
import fnmatch

def subst_method (func):
    """Decorator to match Context.get_substitution_dict()"""
    
    func.substitute_me = True
    return func

def is_subst_method_in_class (method_name, klass):
    bs = [k for k in klass.__bases__
          if is_subst_method_in_class (method_name, k)]
    if bs:
        return True
    
    if (klass.__dict__.has_key (method_name)
      and callable (klass.__dict__[method_name])
      and klass.__dict__[method_name].__dict__.has_key ('substitute_me')):
        return True

    return False

def typecheck_substitution_dict (d):
    for (k, v) in d.items ():
        if type (v) != type(''):
            raise Exception ('type', (k, v))

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

class ConstantCall:
    def __init__ (self, const):
        self.const = const
    def __call__ (self):
        return self.const
    
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
        vars = dict((k, v) for (k, v) in ms if type (v) == type (''))

        member_substs = {}
        for (name, method) in ms:
            try:
                ccall = self.__dict__[name]
                if isinstance (ccall, ConstantCall):
                    method = ccall
            except KeyError:
                pass
            
            if (callable (method)
                and is_subst_method_in_class (name, self.__class__)):
                
                val = method ()
                self.__dict__[name] = ConstantCall (val)

                member_substs[name] = val

                if type (val) != type (''):
                    print 'non string value ', val, 'for subst_method', name
                    raise Exception
        
        d.update (vars)
        d.update (member_substs)

        d = recurse_substitutions (d)
        return d

    def get_substitution_dict (self, env={}):
        if  self._substitution_dict == None:
            self._substitution_dict = self.get_constant_substitution_dict ()

        d = self._substitution_dict
        if env:
            d = d.copy ()
            for (k, v) in env.items ():
                try:
                    if type (v) == type (''):
                        d.update ({k: v % d})
                except:
                    print 'error substituting in', v
                    print 'with', k
                    raise 
        return d
    
    def expand (self, s, env={}):
        d = self.get_substitution_dict (env)
        return s % d

class Os_context_wrapper (Context):
    def __init__ (self, settings):
        Context.__init__ (self, settings)
        self.os_interface = settings.os_interface
        self.verbose = settings.verbose ()
        
    def file_sub (self, re_pairs, name, to_name=None, env={}, must_succeed=False, use_re=True):
        substs = []
        for (frm, to) in re_pairs:
            frm = self.expand (frm, env)
            if type (to) ==type(''):
                to = self.expand (to, env)

            substs.append ((frm, to))

        if to_name:
            to_name = self.expand (to_name, env)
            
        return self.os_interface.file_sub (substs, self.expand (name, env), to_name, must_succeed, use_re=use_re)
    
    def log_command (self, str, env={}):
        str = self.expand (str, env)
        self.os_interface.log_command (str)
        
    def read_pipe (self, cmd, env={}, ignore_errors=False):
        dict = self.get_substitution_dict (env)
        return self.os_interface.read_pipe (cmd % dict, ignore_errors=ignore_errors)

    def system (self, cmd, env={}, ignore_errors=False):
        dict = self.get_substitution_dict (env)
        cmd = self.expand (cmd, env)
        self.os_interface.system (cmd, env=dict, ignore_errors=ignore_errors,
                                  verbose=self.verbose)

    def shadow_tree (self, src, dest):
        src = self.expand (src)
        dest = self.expand (dest)
        self.os_interface.shadow_tree (src, dest)
        
    def dump (self, str, name, mode='w', env={},
              expand_string=True, expand_name=True):
        if expand_name:
            name = self.expand (name, env)
        if expand_string:
            str = self.expand (str, env)
            
        return self.os_interface.dump (str, name, mode=mode)
    
    def locate_files (self, directory, pattern,
                      include_dirs=True, include_files=True):
        """
        Find file using glob PATTERNs. DIRECTORY is expanded.

        Results include DIRECTORY in the filenames.
        """

        ## find() is actually not portable across unices,
        ## so we bake our own.
        
        directory = self.expand (directory)
        directory = re.sub ( "/*$", '/', directory)
        
        results = []
        for (root, dirs, files) in os.walk (directory):
            relative_results = []
            if include_dirs:
                relative_results += dirs
            if include_files:
                relative_results += files
                
            results += [os.path.join (root, f)
                        for f in (fnmatch.filter (relative_results, pattern))]

        return results

#
# Tests.
#
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
    class S: 
        pass
    
    p = TestClass ()
    import settings
    s = settings.Settings ('arm')
    c = Os_context_wrapper (s)

    print c.locate_files ('/etc/', '*.conf')
    
    print p.expand ('%(name)s %(bladir)s')
