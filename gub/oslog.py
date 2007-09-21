import subprocess
import sys
import os
import time
import re
import stat
import traceback

from gub import misc

def now ():
    return time.asctime (time.localtime ())

level = {'quiet': 0,
         'error': 0,
         'stage': 0,
         'info': 1,
         'harmless': 23,
         'warning': 1,
         'command': 2,
         'action': 2,
         'output': 3,
         'debug': 4}

class SerializedCommand:
    def __init__ (self):
        self.instantiation_traceback = traceback.extract_stack ()

    def execute (self, os_commands):
        print 'Not implemented', self

    def print_source (self):
        print ''.join (traceback.format_list (self.instantiation_traceback))

class Nop (SerializedCommand):
    def execute (self):
        pass
    
class System (SerializedCommand):
    def __init__(self, c, **kwargs):
        SerializedCommand.__init__ (self)
        self.command = c
        self.kwargs = kwargs
        
    def __repr__ (self):
        return 'System(%s)' % repr(self.command)

    def execute (self, os_commands):
        cmd = self.command
        verbose = os_commands.verbose
        ignore_errors = self.kwargs.get('ignore_errors')
        os_commands.log ('invoking %s\n' % cmd, level['command'], verbose)

        if os_commands.dry_run:
            return 0

        proc = subprocess.Popen (cmd,  bufsize=1, shell=True, env=self.kwargs.get('env'),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
        
        while proc.poll () is None:
            line = proc.stdout.readline ()
            os_commands.log (line, level['output'], verbose)

            # FIXME: how to yield time slice in python?
            time.sleep (0.001)

        line = proc.stdout.readline ()
        while line:
            os_commands.log (line, level['output'], verbose)
            line = proc.stdout.readline ()

        if proc.returncode:
            m = 'Command barfed: %(cmd)s\n' % locals ()
            os_commands.error (m)
            if not ignore_errors:
                print self.kwargs
                raise misc.SystemFailed (m)

        return proc.returncode

class Message (SerializedCommand):
    def __init__ (self, message):
        self.message = message
    def execute (self, os_commands):
        os_commands.log (self.message, level['stage'], os_commands.verbose)
        
class ReadFile (SerializedCommand):
    def __init__ (self, file):
        self.file = file
    def execute (self, os_commands):
        os_commands.action ('Reading %(file)s\n' % self.__dict__)
        return file (self.file).read ()
        
class Dump (SerializedCommand):
    def __init__ (self, *args, **kwargs):
        SerializedCommand.__init__ (self)
        self.args = args
        self.kwargs = kwargs
    def __repr__ (self):
        return 'Dump(%s)' % repr(self.args)

    def execute (self, os_commands):
        str, name = self.args
        mode = self.kwargs.get('mode', 'w')
        assert type(mode) == type('')
        
        dir = os.path.split (name)[0]
        if not os.path.exists (dir):
            os.makedirs (dir)

        os_commands.action ('Writing %s (%s)\n' % (name, mode))

        f = open (name, mode)
        f.write (str)
        f.close ()

        if 'permissions' in self.kwargs:
            os.chmod (name, self.kwargs['permissions'])
            
class Substitute (SerializedCommand):
    '''Substitute RE_PAIRS in file NAME.
If TO_NAME is specified, the output is sent to there.
'''

    def __init__ (self, *args, **kwargs):
        SerializedCommand.__init__ (self)
        self.args = args
        self.kwargs = kwargs
        
    def __repr__ (self):
        return 'Substitute(%s)' % repr(self.args)

    def execute (self, os_commands):
        (re_pairs, name) = self.args
        to_name = self.kwargs.get ('to_name')
        must_succeed = self.kwargs.get ('must_succeed')
        use_re = self.kwargs.get ('use_re')
                  
        os_commands.action ('substituting in %s\n' % name)
        os_commands.command (''.join (map (lambda x: "'%s' -> '%s'\n" % x,
                                   re_pairs)))

        s = open (name).read ()
        t = s
        for frm, to in re_pairs:
            new_text = ''
            if use_re:
                new_text = re.sub (re.compile (frm, re.MULTILINE), to, t)
            else:
                new_text = t.replace (frm, to)

            if (t == new_text and must_succeed):
                raise Exception ('nothing changed!')
            t = new_text

        if s != t or (to_name and name != to_name):
            stat_info = os.stat(name)
            mode = stat.S_IMODE(stat_info[stat.ST_MODE])

            if not to_name:
                os_commands.action ('backing up %(name)s' % locals())
                try:
                    os.unlink (name + '~')
                except OSError:
                    pass
                os.rename (name, name + '~')
                to_name = name
            h = open (to_name, 'w')
            h.write (t)
            h.close ()
            os.chmod (to_name, mode)

class Conditional (SerializedCommand):
    def __init__ (self, predicate, child, child_false=None):
        SerializedCommand.__init__ (self)
        self.predicate = predicate
        self.child = child
        self.child_false = child_false

    def execute (self, os_commands):
        if self.predicate():
            return self.child.execute (os_commands)
        elif self.child_false:
            return self.child_false.execute (os_commands)

class FilePredicateConditional (Conditional):
    def exists (self):
        self.name 
    def __init__ (self, name, predicate, child):
        SerializedCommand.__init__ (self)
        def pred():
            return predicate (name)
        self.predicate = pred
        self.child = child

class ShadowTree (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
        
    def execute (self, os_commands):
        '''Symlink files from SRC in TARGET recursively'''
        self.shadow (self.src, self.dest, os_commands)

    def shadow (self, src, target, os_commands):
        target = os.path.abspath (target)
        src = os.path.abspath (src)

        os_commands.action ('Shadowing %s to %s\n' % (src, target))
        os.makedirs (target)
        (root, dirs, files) = os.walk (src).next ()
        for f in files:
            os.symlink (os.path.join (root, f), os.path.join (target, f))
        for d in dirs:
            self.shadow (os.path.join (root, d), os.path.join (target, d), os_commands)


class PackageGlobs (SerializedCommand):
    def __init__ (self, root, suffix_dir, globs, dest):
        self.globs = globs
        self.root = root
        self.suffix_dir = suffix_dir
        self.dest = dest
        
    def execute (self, os_commands):
        root = self.root
        suffix_dir = self.suffix_dir
        dest = self.dest
        


        import glob
        globs = []
        for f in self.globs:
            f = re.sub ('/+', '/', f)
            if f.startswith ('/'):
                f = f[1:]
                
            for exp in glob.glob (os.path.join (self.root, f)):
                globs.append (exp.replace (root, './').replace ('//', '/'))

        if not globs:
            globs.append ('thisreallysucks-but-lets-hope-I-dont-exist/')

        cmd = 'tar -C %(root)s/%(suffix_dir)s --ignore-failed --exclude="*~" -zcf %(dest)s ' % locals()
        cmd += ' '.join (globs) 
        System (cmd).execute(os_commands)

# FIXME
class ForcedAutogenMagic (Conditional):
    def __init__ (self, package):
        self.package = package
        SerializedCommand.__init__ (self)

    def system (self, cmd, os_commands):
        return System (cmd).execute (os_commands)

    def execute (self, os_commands):
        package = self.package
        autodir = None
        if not autodir:
            autodir = package.srcdir ()
        if os.path.isdir (os.path.join (package.srcdir (), 'ltdl')):
            self.system (package.expand ('rm -rf %(autodir)s/libltdl && cd %(autodir)s && libtoolize --force --copy --automake --ltdl',
                                         locals ()), os_commands)
        else:
            # fixme
            self.system (package.expand ('cd %(autodir)s && libtoolize --force --copy --automake',
                                         locals ()), os_commands)

        if os.path.exists (os.path.join (autodir, 'bootstrap')):
            self.system (package.expand ('cd %(autodir)s && ./bootstrap', locals ()), os_commands)
        elif os.path.exists (os.path.join (autodir, 'autogen.sh')):

            ## --noconfigure ??
            ## is --noconfigure standard for autogen?
            self.system (package.expand ('cd %(autodir)s && bash autogen.sh  --noconfigure',
                                         locals ()), os_commands)

        else:
            aclocal_opt = ''
            if os.path.exists (package.expand ('%(system_root)s/usr/share/aclocal')):
                aclocal_opt = '-I %(system_root)s/usr/share/aclocal'

            headcmd = ''
            for c in ('configure.in','configure.ac'):
                try:
                    str = open (package.expand ('%(srcdir)s/' + c)).read ()
                    m = re.search ('A[CM]_CONFIG_HEADER', str)
                    str = 0   ## don't want to expand str
                    if m:
                        headcmd = package.expand ('cd %(autodir)s && autoheader %(aclocal_opt)s', env=locals ())
                        break

                except IOError:
                    pass

            self.system (package.expand ('''
cd %(autodir)s && aclocal %(aclocal_opt)s
%(headcmd)s
cd %(autodir)s && autoconf %(aclocal_opt)s
''', locals ()), os_commands)
            if os.path.exists (package.expand ('%(srcdir)s/Makefile.am')):
                self.system (package.expand ('cd %(srcdir)s && automake --add-missing --foreign', locals ()), os_commands)

class AutogenMagic (ForcedAutogenMagic):
    def execute (self, os_commands):
        package = self.package
        if not os.path.exists (package.expand ('%(srcdir)s/configure')):
            if (os.path.exists (package.expand ('%(srcdir)s/configure.ac'))
                or os.path.exists (package.expand ('%(srcdir)s/configure.in'))
                or (not os.path.exists (package.expand ('%(srcdir)s/Makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/SConstruct')))):
                ForcedAutogenMagic.execute (self, os_commands)

class Os_commands:
    '''Encapsulate OS/File system commands

This enables proper logging and deferring and checksumming of commands.'''
    level = level

    def __init__ (self, log_file_name, verbose, dry_run=False, defer=False):
        self.verbose = verbose
        self.dry_run = dry_run
        self._defer = defer
        self._deferred_commands = list ()
        self.log_file_name = log_file_name
        self.log_file = open (self.log_file_name, 'a')
        self.log_file.write ('\n\n * Starting build: %s\n' %  now ())
        self.fakeroot_cmd = False

    def execute_deferred (self):
        a = self._deferred_commands
        self._deferred_commands = list ()
        for cmd in a:
            cmd.execute (self)
        assert self._deferred_commands == list ()

    def _execute (self, command, defer=None):
        if defer == None:
            defer = self._defer
        if defer:
            self._deferred_commands.append (command)
            return 0
        return command.execute (self)
        
    def command_checksum (self):
        return '0000'

    def fakeroot (self, s):
        self.fakeroot_cmd = s
        
    def system_one (self, cmd, env, ignore_errors, verbose=None, defer=None):
        '''Run CMD with environment vars ENV.'''
        if not verbose:
            verbose = self.verbose

        if self.fakeroot_cmd:
            cmd = re.sub ('''(^ *|['"();|& ]*)(fakeroot) ''',
                          '\\1%(fakeroot_cmd)s' % self.__dict__, cmd)
            cmd = re.sub ('''(^ *|['"();|& ]*)(chown|rm|tar) ''',
                          '\\1%(fakeroot_cmd)s\\2 ' % self.__dict__, cmd)


        # ' 
        
        return self._execute (System (cmd, ignore_errors=ignore_errors, verbose=verbose), defer=defer)

    def log (self, str, threshold, verbose=None, defer=None):
        # TODO: defer
        if not str:
            return
        if not verbose:
            verbose = self.verbose
        if verbose >= threshold:
            sys.stderr.write (str)
        if self.log_file:
            self.log_file.write (str)
            self.log_file.flush ()

    def action (self, str):
        self.log (str, level['action'], self.verbose)

    def stage (self, str, defer=None):
        return self._execute (Message (str), defer=defer)

    def error (self, str):
        self.log (str, level['error'], self.verbose)

    def info (self, str):
        self.log (str, level['info'], self.verbose)
              
    def command (self, str):
        self.log (str, level['command'], self.verbose)
              
    def debug (self, str):
        self.log (str, level['debug'], self.verbose)
              
    def warning (self, str):
        self.log (str, level['warning'], self.verbose)
              
    def harmless (self, str):
        self.log (str, level['harmless'], self.verbose)
              
    def system (self, cmd, env={}, ignore_errors=False, verbose=None, defer=None):
        '''Run os commands, and run multiple lines as multiple
commands.
'''
        if not verbose:
            verbose = self.verbose
        call_env = os.environ.copy ()
        call_env.update (env)

        # only log debugging stuf in log/* file if high log level
        if verbose >= self.level['debug']:
            keys = env.keys ()
            keys.sort()
            for k in keys:
                self.log ('%s=%s\n' % (k, env[k]), level['debug'], verbose, defer=defer)
            self.log ('export %s\n' % ' '.join (keys), level['debug'],
                      verbose, defer=defer)

        stat = 0
        for i in cmd.split ('\n'):
            if i:
                stat += self.system_one (i, call_env, ignore_errors, verbose=verbose, defer=defer)
        return stat

    def dump (self, *args, **kwargs):
        return self._execute (Dump (*args, **kwargs))
        
    def file_sub (self, *args, **kwargs):
        return self._execute (Substitute (*args, **kwargs))

    def read_file (self, *args, **kwargs):
        return self._execute (ReadFile (*args, **kwargs), defer=False)

    def read_pipe (self, cmd, ignore_errors=False, silent=False):
        if not silent:
            self.action ('Reading pipe: %s\n' % cmd)

        pipe = os.popen (cmd, 'r')
        output = pipe.read ()
        status = pipe.close ()

        # successful pipe close returns None
        if not ignore_errors and status:
            raise Exception ('read_pipe failed')
        return output

    def shadow_tree (self, src, target):
        return self._execute (ShadowTree (src, target))

    def download_url (self, url, dest_dir, fallback=None):
        import misc
        self.action ('downloading %(url)s -> %(dest_dir)s\n' % locals ())

        # FIXME: where to get settings, fallback should be a user-definable list
	fallback = 'http://peder.xs4all.nl/gub-sources'

	try:
            misc._download_url (url, dest_dir, sys.stderr)
        except Exception, e:
	    if fallback:
	        fallback_url = fallback + url[url.rfind ('/'):]
 		self.action ('downloading %(fallback_url)s -> %(dest_dir)s\n'
		             % locals ())
	        misc._download_url (fallback_url, dest_dir, sys.stderr)
	    else:
	        raise e
	
