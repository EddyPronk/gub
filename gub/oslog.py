import subprocess
import sys
import os
import time
import re
import stat

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

class Os_commands:
    level = level

    '''Encapsulate OS/File system commands for proper logging.'''

    def __init__ (self, log_file_name, verbose):
        self.verbose = verbose
        self.log_file_name = log_file_name
        self.log_file = open (self.log_file_name, 'a')
        self.log_file.write ('\n\n * Starting build: %s\n' %  now ())
        self.fakeroot_cmd = False

        # ARRRGH no python doc on Feisty?
        if 0: #for i in level.keys ():
            def __log (this, message):
                this.log (message, level[i], this.verbose)
            misc.bind_method (__log, self)
            self.i = self.__log

    def fakeroot (self, s):
        self.fakeroot_cmd = s
        
    ## TODO:
    ## capture complete output of CMD, by polling output, and copying to tty.
    def system_one (self, cmd, env, ignore_errors, verbose=None):
        '''Run CMD with environment vars ENV.'''

        if not verbose:
            verbose = self.verbose

        if self.fakeroot_cmd:
            cmd = re.sub ('''(^ *|['"();|& ]*)(chown|fakeroot|rm|tar) ''',
                          '\\1%(fakeroot_cmd)s\\2 ' % self.__dict__, cmd)

        self.log ('invoking %s\n' % cmd, level['command'], verbose)

        proc = subprocess.Popen (cmd, bufsize=1, shell=True, env=env,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)

        while proc.poll () is None:
            line = proc.stdout.readline ()
            self.log (line, level['output'], verbose)
            # FIXME: how to yield time slice in python?
            time.sleep (0.0001)

        line = proc.stdout.readline ()
        while line:
            self.log (line, level['output'], verbose)
            line = proc.stdout.readline ()
        if proc.returncode:
            m = 'Command barfed: %(cmd)s\n' % locals ()
            self.error (m)
	    if not ignore_errors:
        	raise misc.SystemFailed (m)

        return 0

    def log (self, str, threshold, verbose=None):
        if not str:
            return
        if not verbose:
            verbose = self.verbose
        if verbose >= threshold:
            sys.stderr.write (str)
        if self.log_file:
            self.log_file.write (str)
            self.log_file.flush ()

    # FIXME
    def action (self, str):
        self.log (str, level['action'], self.verbose)

    def stage (self, str):
        self.log (str, level['stage'], self.verbose)

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
              
    def system (self, cmd, env={}, ignore_errors=False, verbose=None):
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
                self.log ('%s=%s\n' % (k, env[k]), level['debug'], verbose)
            self.log ('export %s\n' % ' '.join (keys), level['debug'],
                      verbose)

        for i in cmd.split ('\n'):
            if i:
                self.system_one (i, call_env, ignore_errors, verbose=verbose)
        return 0

    def dump (self, str, name, mode='w'):
        dir = os.path.split (name)[0]
        if not os.path.exists (dir):
            self.system ('mkdir -p %s' % dir)

        self.action ('Writing %s (%s)\n' % (name, mode))

        f = open (name, mode)
        f.write (str)
        f.close ()

    def file_sub (self, re_pairs, name, to_name=None,
                  must_succeed=False, use_re=True):
        '''Substitute RE_PAIRS in file NAME.
If TO_NAME is specified, the output is sent to there.
'''

        self.action ('substituting in %s\n' % name)
        self.command (''.join (map (lambda x: "'%s' -> '%s'\n" % x,
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
                self.system ('mv %(name)s %(name)s~' % locals ())
                to_name = name
            h = open (to_name, 'w')
            h.write (t)
            h.close ()
            os.chmod (to_name, mode)

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
        '''Symlink files from SRC in TARGET recursively'''

        target = os.path.abspath (target)
        src = os.path.abspath (src)

        self.action ('Shadowing %s to %s\n' % (src, target))
        os.makedirs (target)
        (root, dirs, files) = os.walk (src).next ()
        for f in files:
            os.symlink (os.path.join (root, f), os.path.join (target, f))
        for d in dirs:
            self.shadow_tree (os.path.join (root, d), os.path.join (target, d))

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
	
