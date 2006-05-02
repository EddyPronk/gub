import subprocess
import sys
import os 
import time
import re
import stat

def now ():
    return time.asctime (time.localtime ())

class Os_commands:
    """

Encapsulate OS/File system commands for proper logging.

"""
    
    def __init__ (self, logfile):
        self.log_file = open (logfile, 'a')
        self.log_file.write ('\n\n * Starting build: %s\n' %  now ())


    ## TODO:
    ## capture complete output of CMD, by polling output, and copying to tty.
    def system_one (self, cmd, env, ignore_error):
        """

        Run CMD with environment vars ENV.
        
        """

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
        """

Write STR in the build log.

"""
        
        sys.stderr.write (str)
        if self.log_file:
            self.log_file.write (str)
            self.log_file.flush ()
        

    def system (self, cmd, env={}, ignore_error=False, verbose=False):
        """

Run os commands, and run multiple lines as multiple
commands.

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
        dir = os.path.split (name)[0]
        if not os.path.exists (dir):
            self.system ('mkdir -p %s' % dir)
        
        self.log_command ("Writing %s (%s)\n" % (name, mode))
        
        f = open (name, mode)
        f.write (str)
        f.close ()

        

    def file_sub (self, re_pairs, name, to_name=None,
                  must_succeed=False):


        """

Substitute RE_PAIRS in file NAME. if TO_NAME is specified, the output
is sent to there.

"""

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
        """Symlink files from SRC in TARGET recursively"""

        
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
