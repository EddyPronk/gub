import inspect
import os
import re
import traceback
import types

def subst_method (func):
    '''Decorator to match Context.get_substitution_dict ()'''
    func.substitute_me = True
    return func

NAME = 0
OBJECT = 1
def is_method (member):
    return type (member[OBJECT]) == types.MethodType

def is_subst_method (member):
    return (is_method (member)
            and (hasattr (member[OBJECT], 'substitute_me')
                 or base_is_class_subst_method (member[NAME],
                                                member[OBJECT].im_class)))

class _C (object):
    pass

def is_class_subst_method (name, cls):
    if (cls.__dict__.has_key (name)
        and classmethod (cls.__dict__[name])
        and type (cls.__dict__[name]) != type (_C.__init__)
        and cls.__dict__[name].__dict__.has_key ('substitute_me')):
        return True
    return False

def base_is_class_subst_method (name, cls):
    if is_class_subst_method (name, cls):
        return True
    for c in cls.__bases__:
        if base_is_class_subst_method (name, c):
            return True
    return False

def typecheck_substitution_dict (d):
    for (k, v) in d.items ():
        if type (v) != str:
            raise Exception ('type', (k, v))

def recurse_substitutions (d):
    for (k, v) in d.items ():
        if type (v) != str:
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

class SetAttrTooLate (Exception):
    pass

class ExpandInInit (Exception):
    pass

class NonStringExpansion (Exception):
    pass

# New style classes should now work
#class Context (object):
class Context ():
    def __init__ (self, parent = None):
        self._substitution_dict = None
        self._parent = parent
        self._substitution_assignment_traceback = None

    def __setattr__ (self, k, v):
        if (type (v) == str
            and k != '_substitution_dict' and self._substitution_dict):

            msg =  ('%s was already set in\n%s'
                    % (k, 
                       ''.join (traceback.format_list (self._substitution_assignment_traceback))))
            
            raise SetAttrTooLate (msg)
        self.__dict__[k] = v
        
    def get_constant_substitution_dict (self):
        d = {}
        if self._parent:
            d = self._parent.get_substitution_dict ()
            d = d.copy ()
            
        members = inspect.getmembers (self)
        member_substs = {}
        for (name, method) in filter (is_subst_method, members):
            val = method ()
            self.__dict__[name] = ConstantCall (val)
            member_substs[name] = val
            if type (val) != str:
                message = 'non string value ' + val + 'for subst_method' + name
                print message
                raise NonStringExpansion (message)

        string_vars = dict ((k, v) for (k, v) in members if type (v) == str)
        d.update (string_vars)
        d.update (member_substs)
        d = recurse_substitutions (d)
        return d

    def get_substitution_dict (self, env={}):
        if self._substitution_dict == None:
            self._substitution_assignment_traceback = traceback.extract_stack ()
            self._substitution_dict = self.get_constant_substitution_dict ()

            init_found = False
            for (file, line, name, text) in self._substitution_assignment_traceback:
                # this is a kludge, but traceback doesn't yield enough info
                # to actually check that the __init__ being called is a
                # derived from self.__init__
                if name == '__init__' and 'buildrunner.py' not in file:
                    init_found = True
                 
            if init_found:
                # if this happens derived classes cannot override settings
                # from the baseclass.
                msg = 'Cannot Context.expand () in __init__ ()'
                raise ExpandInInit (msg)
            
        d = self._substitution_dict
        if env:
            d = d.copy ()
            for (k, v) in env.items ():
                try:
                    if type (v) == str:
                        d.update ({k: v % d})
                except:
                    repr_v = repr (v)
                    repr_k = repr (k)
                    type_v = type (v)
                    type_k = type (k)
                    msg = 'Error substituting in %(repr_v)s(%(type_v)s) with %(repr_k)s(%(type_k)s)' % locals ()
                    raise NonStringExpansion (msg)
        return d
    
    def expand (self, s, env={}):
        d = self.get_substitution_dict (env)
        try:
            e = s % d
        except KeyError, v:
            print 'format string: >>>' + s + '<<<'
            print 'self:', self
            raise v
        except ValueError, v:
            print 'format string: >>>' + s + '<<<'
            print 'self:', self
            raise v
        return e

class RunnableContext (Context):
    def __init__ (self, *args):
        Context.__init__ (self, *args)

        # TODO: should use _runner ?
        self.runner = None
        
    def connect_command_runner (self, runner):
        previous = self.runner
        self.runner = runner
        return previous

    def file_sub (self, re_pairs, name, to_name=None, env={}, must_succeed=False, use_re=True):
        substs = []
        for (frm, to) in re_pairs:
            frm = self.expand (frm, env)
            if type (to) == str:
                to = self.expand (to, env)

            substs.append ((frm, to))

        if to_name:
            to_name = self.expand (to_name, env)
            
        return self.runner.file_sub (substs, self.expand (name, env), to_name=to_name,
                                     must_succeed=must_succeed, use_re=use_re)
    
    def fakeroot (self, s, env={}):
        self.runner.fakeroot (self.expand (s, env=env))
        
    def command (self, str):
        self.runner.command (str)
        
    def system (self, cmd, env={}, ignore_errors=False):
        dict = self.get_substitution_dict (env)
        cmd = self.expand (cmd, env)
        self.runner.system (cmd, env=dict, ignore_errors=ignore_errors)

    def shadow_tree (self, src, dest, env={}):
        src = self.expand (src, env=env)
        dest = self.expand (dest, env=env)
        self.runner.shadow_tree (src, dest)
        
    def dump (self, str, name, mode='w', env={},
              expand_string=True, expand_name=True, permissions=0644):
        if expand_name:
            name = self.expand (name, env)
        if expand_string:
            str = self.expand (str, env)
        return self.runner.dump (str, name, mode=mode, permissions=permissions)
    
    def map_locate (self, func, directory, pattern, **kwargs):
        return self.runner.map_locate (func, self.expand (directory),
                                       pattern, **kwargs)

    def copy (self, src, dest, env={}):
        return self.runner.copy (self.expand (src, env=env), self.expand (dest, env=env))

    def func (self, f, *args):
        return self.runner.func (f, *args)

    def chmod (self, file, mode, env={}):
        return self.runner.chmod (self.expand (file, env=env), mode)

    def symlink (self, src, dest, env={}):
        return self.runner.symlink (self.expand (src, env=env), self.expand (dest, env=env))

    def rename (self, src, dest, env={}):
        return self.runner.rename (self.expand (src, env=env), self.expand (dest, env=env))

    def mkdir (self, dir, env={}):
        return self.runner.mkdir (self.expand (dir, env=env))

    def remove (self, file, env={}):
        return self.runner.remove (self.expand (file, env=env))

    def rmtree (self, file, env={}):
        return self.runner.rmtree (self.expand (file, env=env))

#
# Tests.
#
if __name__=='__main__':
    class TestBase (Context):
        @subst_method
        def bladir (self):
            return 'foo'
        
    class TestClass (TestBase):
        @subst_method
        def name (self):
            return self.__class__.__name__
        
        def bladir (self):
            return 'derivedbladir'
    class S: 
        pass
    
    p = TestClass ()
    from gub import settings
    s = settings.Settings ('debian-arm')
    c = RunnableContext (s)

    print c.locate_files ('/etc/', '*.conf')
    
    print p.expand ('%(name)s %(bladir)s')
