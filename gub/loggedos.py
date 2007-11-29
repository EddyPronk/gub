import misc
import subprocess
import sys
import os
import shutil
import time

#FIXME:
# using **kwargs is scary: when called from spec as replacement for old
# self.system:
#
#   loggedos.system (logger, 'foo %(bar)s baz', locals ())
#
# this somehow silently fails: command is not expanded and no error is raised

# We cannot, however use the more safe:
#    def system (logger, cmd, env={}, ignore_errors=False):
# because we are being called from commands.py as:
#        return loggedos.system (logger, self.command,
#                                **self.kwargs)
# We *must* use kwargs.get here to get a sane ENV.  What to do?
# Probably we should expand the kwargs in commands.py:System, because
# *that* is the place that received the kwargs and knows about them.
# 
def system (logger, cmd, env={}, ignore_errors=False):
    logger.write_log ('invoking %s\n' % cmd, 'command')
    proc = subprocess.Popen (cmd, bufsize=1, shell=True, env=env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True)

    if 1:
        for line in proc.stdout:
            logger.write_log (line, 'output')
        proc.wait ()

        if proc.returncode:
            m = 'Command barfed: %(cmd)s\n' % locals ()
            if not ignore_errors:
                logger.write_log (m, 'error')
                raise misc.SystemFailed (m)

        return proc.returncode
    else: # WTF, this oldcode exhibits weird verbosity problem
        #different behaviour if run with -vvv?
        proc = subprocess.Popen (cmd, bufsize=1, shell=True, env=env,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)

        while proc.poll () is None:
            line = proc.stdout.readline ()
            #self.log (line, level['output'], verbose)
            logger.write_log (line, 'output')
            # FIXME: how to yield time slice in python?
            time.sleep (0.0001)

        line = proc.stdout.readline ()
        while line:
            #self.log (line, level['output'], verbose)
            logger.write_log (line, 'output')
            line = proc.stdout.readline ()
        if proc.returncode:
            m = 'Command barfed: %(cmd)s\n' % locals ()
            #self.error (m)
            logger.write_log (m, 'error')
	    if not ignore_errors:
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
            self.logger = logging.set_default_log ('downloads/test/test.log', 5)
        def testDumpFile (self):
            dump_file (self.logger, 'boe', 'downloads/test/a')
            self.assert_ (os.path.exists ('downloads/test/a'))
        def testSystem (self):
            self.assertRaises (Exception,
                               system, self.logger, 'cp %(src)s %(dest)s')
            
    suite = unittest.makeSuite (Test_loggedos)
    unittest.TextTestRunner (verbosity=2).run (suite)

if __name__ == '__main__':
    test ()
