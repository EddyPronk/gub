import misc
import subprocess
import sys
import os
import shutil

def system (logger, cmd, env={}, ignore_errors=False):
    logger.write_log ('invoking %s\n' % cmd, 'command')

    proc = subprocess.Popen (cmd, bufsize=1, shell=True, env=env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True)

    for line in proc.stdout:
        logger.write_log (line, 'output')
    proc.wait ()

    if proc.returncode:
        m = 'Command barfed: %(cmd)s\n' % locals ()
        if not ignore_errors:
            logger.write_log (m, 'error')
            raise misc.SystemFailed (m)
        
    return proc.returncode


########
# logged aliases to misc.py
def logged_function(logger, function, *args, **kwargs):
    logger.write_multilevel_message(
        [('Running %s\n' % function.__name__, 'action'),
        ('Running %s: %s\n' % (function.__name__, repr(args)), 'command'),
        ('Running %s\n  %s\n  %s\n'
         % (function.__name__, repr(args), repr(kwargs)), 'debug')])

    return function (*args, **kwargs)

currentmodule = sys.modules[__name__] #ugh
for name, func in {'read_file': misc.read_file,
                   'file_sub': misc.file_sub,
                   'download_url': misc.download_url,
                   'dump_file': misc.dump_file,
                   'shadow':misc.shadow,
                   'chmod': os.chmod,
                   'makedirs': os.makedirs,
                   'copy2': shutil.copy2,
                   'remove': os.remove,
                   'symlink': os.symlink,
                   'rename': os.rename,
                   'read_pipe': misc.read_pipe}.items():

    def with_logging (func):
        def func_with_logging (logger, *args, **kwargs):
            val = logged_function(logger, func, *args, **kwargs)
            return val
        return func_with_logging
    currentmodule.__dict__[name] = with_logging (func)


def test ():
    import unittest
    import logging

    # This is not a unittest, it only serves as a smoke test

    class Test_loggedos (unittest.TestCase):
        def setUp (self):
            # Urg: global??
            self.logger = logging.set_default_log ('downloads/test/test.log', 0)
        def testSystem (self):
            self.assertRaises (misc.SystemFailed,
                               system (self.logger, 'cp %(src)s %(dest)s'))
            
    suite = unittest.makeSuite (Test_loggedos)
    unittest.TextTestRunner (verbosity=2).run (suite)

if __name__ == '__main__':
    test ()
