import os
import shutil
import subprocess
import sys
#
from gub import logging
from gub import misc

########
# logged aliases to misc.py
def logged_function (logger, function, *args, **kwargs):
    if not isinstance (logger, logging.AbstractCommandLogger):
        raise Exception ('NOT a logger:' + str (logger))
    logger.write_multilevel_message (
        [('Running %s\n' % function.__name__, 'action'),
         ('Running %s: %s\n' % (function.__name__, repr (args)), 'command'),
         ('Running %s\n  %s\n  %s\n'
          % (function.__name__, repr (args), repr (kwargs)), 'debug')])
    return function (*args, **kwargs)

class Operations(object):
    mapping = {'read_file': misc.read_file,
               'file_sub': misc.file_sub,
               'download_url': misc.download_url,
               'dump_file': misc.dump_file,
               'shadow':misc.shadow,
               'chmod': os.chmod,
               'makedirs': os.makedirs,
               'copy2': shutil.copy2,
               'remove': os.remove,
               'link': os.link,
               'symlink': os.symlink,
               'rename': os.rename,
               'read_pipe': misc.read_pipe}

    def __getattr__(self, name):
        return self.mapping[name]

class DryOperations(Operations):
    def download_url (self, original_url, dest_dir):
        pass

class Module(object):
    def __init__ (self, wrapped):
        self.wrapped = wrapped
        self.impl = Operations()

    def __getattr__ (self, name):
        def with_logging (func):
            def func_with_logging (logger, *args, **kwargs):
                val = logged_function (logger, func, *args, **kwargs)
                return val
            return func_with_logging
        return with_logging(getattr(self.impl, name))
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            return 'default'

    def dry_run (self):
        self.impl = DryOperations()
        
    def system (self, logger, cmd, env=os.environ, ignore_errors=False):
        # UGH, FIXME:
        # There is loggedos usage that defies any PATH settings
        tools_bin_dir = os.path.join (os.getcwd (), 'target/tools/root/usr/bin')
        if not tools_bin_dir in env.get ('PATH', ''):
            env['PATH'] = tools_bin_dir + misc.append_path (env.get ('PATH', ''))
            env['SHELLOPTS'] = 'physical'
            logger.write_log ('COMMAND defies PATH: ' + cmd + '\n', 'command')

        logger.write_log ('invoking %(cmd)s\n' % locals (), 'command')
        proc = subprocess.Popen (cmd, bufsize=0, shell=True, env=env,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)

        line = proc.stdout.readline ()
        while line:
            if sys.version.startswith ('2'):
                logger.write_log (line, 'output')
            else:
                logger.write_log (line.decode (sys.stdout.encoding), 'output')
            line = proc.stdout.readline ()
        proc.wait ()

        if proc.returncode:
            m = 'Command barfed: %(cmd)s\n' % locals ()
            logger.write_log (m, 'error')
            if not ignore_errors:
                raise misc.SystemFailed (m)
        return proc.returncode

sys.modules[__name__] = Module(sys.modules[__name__])

def test ():
    import unittest
    from gub import logging

    # This is not a unittest, it only serves as a smoke test

    class Test_loggedos (unittest.TestCase):
        def setUp (self):
            # Urg: global??
            self.logger = logging.set_default_log ('downloads/test/test.log', 5)
            self.loggedos = Module('loggedos')
        def testDumpFile (self):
            self.loggedos.dump_file (self.logger, 'boe', 'downloads/test/a')
            self.assert_ (os.path.exists ('downloads/test/a'))
        def testSystem (self):
            self.assertRaises (Exception,
                               self.loggedos.system, self.logger, 'cp %(src)s %(dest)s')
            
    suite = unittest.makeSuite (Test_loggedos)
    unittest.TextTestRunner (verbosity=2).run (suite)

if __name__ == '__main__':
    test ()
