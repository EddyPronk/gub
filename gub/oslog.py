#!/usr/bin/python

"""
    Copyright (c) 2005--2007
    Jan Nieuwenhuizen <janneke@gnu.org>
    Han-Wen Nienhuys <hanwen@xs4all.nl>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import fnmatch
import os
import re
import stat
import subprocess
import sys
import time
import traceback
import inspect

from gub import misc

def now ():
    return time.asctime (time.localtime ())

level = {'quiet': 0,
         'error': 0,
         'stage': 0,
         'info': 1,
         'harmless': 2,
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
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)

class Nop (SerializedCommand):
    def execute (self):
        pass
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)

class System (SerializedCommand):
    def __init__ (self, c, **kwargs):
        SerializedCommand.__init__ (self)
        self.command = c
        self.kwargs = kwargs

    def __repr__ (self):
        return 'System (%s)' % repr (self.command)

    def checksum (self, hasher):
        hasher.append (self.command)
        # TODO: use env too.

    def execute (self, os_commands):
        cmd = self.command
        verbose = os_commands.verbose
        ignore_errors = self.kwargs.get ('ignore_errors')
        os_commands.log ('invoking %s\n' % cmd, level['command'], verbose)

        if os_commands.dry_run:
            return 0

        proc = subprocess.Popen (cmd,  bufsize=1, shell=True,
                                 env=self.kwargs.get ('env'),
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
            if not ignore_errors:
                os_commands.error (m)
                raise misc.SystemFailed (m)
        return proc.returncode

class Copy (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (src)
        hasher.append (dest)
    def execute (self, os_commands):
        import shutil
        shutil.copy2 (self.src, self.dest)

class Chmod (SerializedCommand):
    def __init__ (self, file, mode):
        self.file = file
        self.mode = mode
    def execute (self, os_commands):
        os.chmod (self.file, self.mode)
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.file)
        hasher.append (str(self.mode))

# FIXME: can't this be done a bit easier?
# why is this needed ? --hwn
#
# install_licence wants to check for several files if they exist.
# Because of the current implementation as a subst method, deferring
# breaked with infinate recursion when attepmting a simple
# implementation using func () or map_locate (), because those
# functions also calls subst.
#
# This is something I wanted to do earlier, this simple change
# allows to delete a number of build specifications and makes
# others more simple.  We want to get rid of as many build
# specifications as we can.  --jcn
class InstallLicense (SerializedCommand):
    def __init__ (self, name, srcdir, install_root, file):
        self.install_root = install_root
        self.name = name
        self.srcdir = srcdir
        self.install_root = install_root
        self.file = file
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
    def execute (self, os_commands):
        name = self.name
        srcdir = self.srcdir
        file = self.file
        install_root = self.install_root
        if type (self.file) == type (''):
            file = self.file % locals ()
        else:
            for file in self.file:
                file = file % locals ()
                if os.path.exists (file):
                    break
        os_commands.system ('''
mkdir -p %(install_root)s/license
cp %(file)s %(install_root)s/license/%(name)s
''' % locals ())

class Func (SerializedCommand):
    def __init__ (self, func):
        self.func = func
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (self.func))
    def execute (self, os_commands):
        return self.func ()

class Message (SerializedCommand):
    def __init__ (self, message, threshold, verbose):
        self.message = message
        self.threshold = threshold
        self.verbose = verbose
    def execute (self, os_commands):
        if not self.message:
            return 0
        if not self.verbose:
            self.verbose = os_commands.verbose
        if self.verbose >= self.threshold:
            sys.stderr.write (self.message)
        if os_commands.log_file:
            os_commands.log_file.write (self.message)
            os_commands.log_file.flush ()
    def checksum (self, hasher):
        pass

class MapLocate (SerializedCommand):
    def __init__ (self, func, directory, pattern):
        self.func = func
        self.directory = directory
        self.pattern = pattern
    def execute (self, os_commands):
        return map (self.func,
                    os_commands.locate_files (self.directory, self.pattern))

    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (self.func))
        hasher.append (self.directory)
        hasher.append (self.pattern)

class ReadFile (SerializedCommand):
    def __init__ (self, file):
        self.file = file
    def execute (self, os_commands):
        os_commands.action ('Reading %(file)s\n' % self.__dict__)
        return file (self.file).read ()
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.file)

class Dump (SerializedCommand):
    def __init__ (self, *args, **kwargs):
        SerializedCommand.__init__ (self)
        self.args = args
        self.kwargs = kwargs
    def __repr__ (self):
        return 'Dump (%s)' % repr (self.args)
    def checksum (self, hasher):
        str, name = self.args
        hasher.append (self.__class__.__name__)
        hasher.append (name)
        hasher.append (str)
    def execute (self, os_commands):
        str, name = self.args
        mode = self.kwargs.get ('mode', 'w')
        if not type (mode) == type (''):
            print 'MODE:', mode
            print 'STR:', str
            print 'NAME:', name
            assert type (mode) == type ('')

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
        return 'Substitute (%s)' % repr (self.args)

    def checksum (self, hasher):
        (re_pairs, name) = self.args
        hasher.append (self.__class__.__name__)
        hasher.append (name)
        for (src, dst) in re_pairs:
            hasher.append (src)
            hasher.append (dst)

    def execute (self, os_commands):
        (re_pairs, name) = self.args
        to_name = self.kwargs.get ('to_name')
        must_succeed = self.kwargs.get ('must_succeed')
#        use_re = self.kwargs.get ('use_re')
        # FIXME: kwargs approach is fragile, must check other
        # defaults.  use_re defaulted to True...
        use_re = True
        if self.kwargs.has_key ('use_re'):
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
            stat_info = os.stat (name)
            mode = stat.S_IMODE (stat_info[stat.ST_MODE])

            if not to_name:
                os_commands.action ('backing up: %(name)s\n' % locals ())
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
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (self.predicate))
        if self.child:
            self.child.checksum (hasher)
        if self.child_false:
            self.child_false.checksum (hasher)
    def execute (self, os_commands):
        if self.predicate():
            return self.child.execute (os_commands)
        elif self.child_false:
            return self.child_false.execute (os_commands)

class FilePredicateConditional (Conditional):
    def __init__ (self, name, predicate, child):
        SerializedCommand.__init__ (self)
        def pred():
            return predicate (name)
        self.predicate = pred
        self.child = child
    def exists (self):
        self.name

class ShadowTree (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
    def execute (self, os_commands):
        '''Symlink files from SRC in TARGET recursively'''
        self.shadow (self.src, self.dest, os_commands)
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.src)
        hasher.append (self.dest)
    def shadow (self, src, target, os_commands):
        target = os.path.abspath (target)
        src = os.path.abspath (src)
        os_commands.action ('Shadowing %s to %s\n' % (src, target))
        os.makedirs (target)
        (root, dirs, files) = os.walk (src).next ()
        for f in files:
            os.symlink (os.path.join (root, f), os.path.join (target, f))
        for d in dirs:
            self.shadow (os.path.join (root, d), os.path.join (target, d),
                         os_commands)

class PackageGlobs (SerializedCommand):
    def __init__ (self, root, suffix_dir, globs, dest):
        self.globs = globs
        self.root = root
        self.suffix_dir = suffix_dir
        self.dest = dest

    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (''.join (self.globs))
        hasher.append (self.root)
        hasher.append (self.suffix_dir)
        hasher.append (self.dest)

    def execute (self, os_commands):
        root = self.root
        suffix_dir = self.suffix_dir
        dest = self.dest

        import glob
        globs = list ()
        for f in self.globs:
            f = re.sub ('/+', '/', f)
            if f.startswith ('/'):
                f = f[1:]
            for exp in glob.glob (os.path.join (self.root, f)):
                globs.append (exp.replace (root, './').replace ('//', '/'))
        if not globs:
            globs.append ('no-globs-for-%(dest)s' % locals ())

        _v = os_commands.verbose_flag ()
        cmd = 'tar -C %(root)s/%(suffix_dir)s --ignore-failed --exclude="*~"%(_v)s -zcf %(dest)s ' % locals()
        cmd += ' '.join (globs)
        System (cmd).execute (os_commands)

# FIXME
class ForcedAutogenMagic (Conditional):
    def __init__ (self, package):
        self.package = package
        SerializedCommand.__init__ (self)

    def system (self, cmd, os_commands):
        return System (cmd).execute (os_commands)

    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (ForcedAutogenMagic.execute))

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
            if os.path.exists (package.expand ('%(system_prefix)s/share/aclocal')):
                aclocal_opt = '-I %(system_prefix)s/share/aclocal'

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
        self.start_marker = ' * Starting build: %s\n' %  now ()
        self.log_file.write ('\n\n' + self.start_marker)
        self.fakeroot_cmd = False

    def defer_execution (self, defer=True):
        self._defer = defer

    def execute_deferred (self):
        a = self._deferred_commands
        self._defer = False
        self._deferred_commands = list ()
        for cmd in a:
            cmd.execute (self)
        assert self._deferred_commands == list ()

    def checksum (self):
        # A visitor pattern versus simple return value, is that
        # handy/really necessary?
        hasher = list ()
        map (lambda x: x.checksum (hasher), self._deferred_commands)
        return '\n'.join (hasher)

    def _execute (self, command, defer=None):
        if defer == None:
            defer = self._defer
        if defer:
            self._deferred_commands.append (command)
            return 0
        return command.execute (self)

    def read_tail (self, size=10240, lines=100):
        return misc.read_tail (self.log_file_name, size, lines,
                               self.start_marker)

    def fakeroot (self, s):
        self.fakeroot_cmd = s

    def verbose_flag (self):
        if self.verbose >= level['output']:
            return ' -v'
        return ''

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
        return self._execute (System (cmd, env=env, ignore_errors=ignore_errors, verbose=verbose), defer=defer)

    def log (self, str, threshold, verbose=None, defer=None):
        return self._execute (Message (str, threshold, verbose), defer)

    def action (self, str, defer=None):
        self.log (str, level['action'], self.verbose, defer)

    def stage (self, str, defer=None):
        self.log (str, level['stage'], self.verbose, defer)

    def error (self, str, defer=None):
        self.log (str, level['error'], self.verbose, defer)

    def info (self, str, defer=None):
        self.log (str, level['info'], self.verbose, defer)

    def command (self, str, defer=None):
        self.log (str, level['command'], self.verbose, defer)

    def debug (self, str, defer=None):
        self.log (str, level['debug'], self.verbose, defer)

    def warning (self, str, defer=None):
        self.log (str, level['warning'], self.verbose, defer)

    def harmless (self, str, defer=None):
        self.log (str, level['harmless'], self.verbose, defer)

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
                stat += self.system_one (i, call_env, ignore_errors,
                                         verbose=verbose, defer=defer)
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
        self.action ('downloading %(url)s -> %(dest_dir)s\n' % locals (),
                     defer=False)

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

    def locate_files (self, directory, pattern,
                      include_dirs=True, include_files=True):
        directory = re.sub ( "/*$", '/', directory)
        results = list ()
        for (root, dirs, files) in os.walk (directory):
            relative_results = list ()
            if include_dirs:
                relative_results += dirs
            if include_files:
                relative_results += files
            results += [os.path.join (root, f)
                        for f in (fnmatch.filter (relative_results, pattern))]
        return results

    def map_locate (self, func, directory, pattern):
        return self._execute (MapLocate (func, directory, pattern))

    def copy (self, src, dest):
        return self._execute (Copy (src, dest))

    def func (self, f):
        return self._execute (Func (f))

    def chmod (self, file, mode):
        return self._execute (Chmod (file, mode))

    def install_license (self, name, srcdir, install_root, file):
        return self._execute (InstallLicense (name, srcdir, install_root, file))

