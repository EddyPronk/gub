import inspect
import os
import re
import traceback

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

class SetAttrTooLate(Exception):
    pass
class ExpandInInit(Exception):
    pass
class NonStringExpansion(Exception):
    pass

class Context:
    def __init__ (self, parent = None):
        self._substitution_dict = None
        self._parent = parent
        self._substitution_assignment_traceback = None

    def __setattr__(self, k, v):
        if (type(v) == type('')
            and k <> '_substitution_dict' and self._substitution_dict):
            print 'was already set in'
            print ''.join(traceback.format_list (self._substitution_assignment_traceback))

            raise SetAttrTooLate((k, self))

        self.__dict__[k] = v
        
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
                    raise NonStringExpansion
        
        d.update (vars)
        d.update (member_substs)

        d = recurse_substitutions (d)
        return d

    def get_substitution_dict (self, env={}):
        if self._substitution_dict == None:
            self._substitution_assignment_traceback = traceback.extract_stack()
            self._substitution_dict = self.get_constant_substitution_dict ()

            init_found = False
            for (file, line, name, text) in self._substitution_assignment_traceback:
                # this is a kludge, but traceback doesn't yield enough info
                # to actually check that the __init__ being called is a
                # derived from self.__init__
                if name == '__init__' and 'builder.py' not in file:
                    init_found = True
                 
            if init_found:
                # if this happens derived classes cannot override settings
                # from the baseclass.
                print ' Cannot Context.expand() in __init__()'
                raise ExpandInInit()
            
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
        try:
            e = s % d
        except KeyError, v:
            print 'format-string =', s
            raise v
        except ValueError, v:
            print 'format-string =', s
            raise v
        return e

class Os_context_wrapper (Context):
    def __init__ (self, settings):
        Context.__init__ (self, settings)
        self.os_interface = settings.os_interface
        self.verbose = settings.options.verbose
        
    def file_sub (self, re_pairs, name, to_name=None, env={}, must_succeed=False, use_re=True):
        substs = []
        for (frm, to) in re_pairs:
            frm = self.expand (frm, env)
            if type (to) ==type(''):
                to = self.expand (to, env)

            substs.append ((frm, to))

        if to_name:
            to_name = self.expand (to_name, env)
            
        return self.os_interface.file_sub (substs, self.expand (name, env), to_name=to_name,
                                           must_succeed=must_succeed, use_re=use_re)
    
    def fakeroot (self, s):
        self.os_interface.fakeroot (s)
        
    def command (self, str):
        self.os_interface.command (str)
        
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
              expand_string=True, expand_name=True, permissions=0644):
        if expand_name:
            name = self.expand (name, env)
        if expand_string:
            str = self.expand (str, env)
            
        return self.os_interface.dump (str, name, mode=mode, permissions=permissions)
    
    def locate_files (self, directory, pattern,
                      include_dirs=True, include_files=True):
        '''Return list of files under DIRECTORY using glob PATTERNs

Results include DIRECTORY in the filenames.'''

        return self.os_interface.locate_files (self.expand (directory),
                                               pattern, include_dirs, include_files)

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
    from gub import settings
    s = settings.Settings ('debian-arm')
    c = Os_context_wrapper (s)

    print c.locate_files ('/etc/', '*.conf')
    
    print p.expand ('%(name)s %(bladir)s')
