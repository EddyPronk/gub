import os
import re
import traceback
import inspect
import subprocess
import stat
import shutil
import glob

from gub import misc

class SerializedCommand:
    def __init__ (self):
        self.instantiation_traceback = traceback.extract_stack ()
    def execute (self, runner):
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

class UpdateSourceDir (SerializedCommand):
    def __init__ (self, buildspec):
        self.buildspec = buildspec

    def execute (self, runner):
        buildspec = self.buildspec 
        if not buildspec.source:
            return False
        if not buildspec.source.is_tracking ():
            buildspec.system ('rm -rf %(srcdir)s %(builddir)s %(install_root)s')

        if buildspec.source:
            buildspec.source.update_workdir (buildspec.expand ('%(srcdir)s'))

        # TODO: move this to Repository
        if (os.path.isdir (buildspec.expand ('%(srcdir)s'))):
            buildspec.system ('chmod -R +w %(srcdir)s', ignore_errors=True)
           
    def checksum (self, hasher):
        tracking = 'not tracking'
        if self.buildspec.source.is_tracking ():
            tracking  = 'tracking'

        hasher.append ('UpdateSourceDir(%s)' % tracking)
        
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

    def execute (self, runner):
        cmd = self.command
        ignore_errors = self.kwargs.get ('ignore_errors')
        runner.log ('invoking %s\n' % cmd, 'command')

        proc = subprocess.Popen (cmd,  bufsize=1, shell=True,
                                 env=self.kwargs.get ('env'),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)

        for line in proc.stdout:
            runner.log (line, 'output')
        proc.wait ()
        
        if proc.returncode:
            m = 'Command barfed: %(cmd)s\n' % locals ()
            if not ignore_errors:
                runner.error (m)
                raise misc.SystemFailed (m)
        return proc.returncode

class Copy (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.src)
        hasher.append (self.dest)
    def execute (self, runner):
        shutil.copy2 (self.src, self.dest)

class Chmod (SerializedCommand):
    def __init__ (self, file, mode):
        self.file = file
        self.mode = mode
    def execute (self, runner):
        os.chmod (self.file, self.mode)
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.file)
        hasher.append (str (self.mode))

class Func (SerializedCommand):
    def __init__ (self, func, *args):
        self.func = func
        self.args = args
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (self.func))
        hasher.append (repr (self.args))
    def execute (self, runner):
        return self.func (*self.args)

class Message (SerializedCommand):
    def __init__ (self, message, message_type):
        self.message = message
        self.message_type = message_type

    def execute (self, runner):
        runner.logger.write_log (self.message, self.message_type)
        
    def checksum (self, hasher):
        pass

class MapLocate (SerializedCommand):
    def __init__ (self, func, directory, pattern):
        self.func = func
        self.directory = directory
        self.pattern = pattern
    def execute (self, runner):
        return map (self.func,
                    runner.locate_files (self.directory, self.pattern))

    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (self.func))
        hasher.append (self.directory)
        hasher.append (self.pattern)

class ReadFile (SerializedCommand):
    def __init__ (self, file):
        self.file = file
    def execute (self, runner):
        runner.action ('Reading %(file)s\n' % self.__dict__)
        return file (self.file).read ()
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.file)

class ReadPipe (SerializedCommand):
    def __init__ (self, cmd, ignore_errors=False, silent=False):
        self.cmd = cmd
        self.ignore_errors = ignore_errors
        self.silent = silent
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.cmd)
        hasher.append (str (self.ignore_errors))
    def execute (self, runner):
        runner.action ('Reading %(cmd)s\n' % self.__dict__)
        pipe = os.popen (self.cmd, 'r')
        output = pipe.read ()
        status = pipe.close ()
        # successful pipe close returns None
        if not self.ignore_errors and status:
            raise Exception ('read_pipe failed')
        return output

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
    def execute (self, runner):
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

        runner.action ('Writing %s (%s)\n' % (name, mode))

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

    def execute (self, runner):
        (re_pairs, name) = self.args

        runner.action ('substituting in %s\n' % name)
        runner.command (''.join (map (lambda x: "'%s' -> '%s'\n" % x,
                                      re_pairs)))

        misc.file_sub (re_pairs, name, **self.kwargs)
        
class Conditional (SerializedCommand):
    def __init__ (self, predicate, true, false=None):
        SerializedCommand.__init__ (self)
        self.predicate = predicate
        self.true = true
        self.false = false
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (self.predicate))
        if self.true:
            self.true.checksum (hasher)
        if self.false:
            self.false.checksum (hasher)
    def execute (self, runner):
        if self.predicate ():
            return self.true.execute (runner)
        elif self.false:
            return self.false.execute (runner)

class ShadowTree (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
    def execute (self, runner):
        '''Symlink files from SRC in TARGET recursively'''
        self.shadow (self.src, self.dest, runner)
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (self.src)
        hasher.append (self.dest)
    def shadow (self, src, target, runner):
        target = os.path.abspath (target)
        src = os.path.abspath (src)
        runner.action ('Shadowing %s to %s\n' % (src, target))
        os.makedirs (target)
        (root, dirs, files) = os.walk (src).next ()
        for f in files:
            os.symlink (os.path.join (root, f), os.path.join (target, f))
        for d in dirs:
            self.shadow (os.path.join (root, d), os.path.join (target, d),
                         runner)

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

    def execute (self, runner):
        root = self.root
        suffix_dir = self.suffix_dir
        dest = self.dest

        globs = list ()
        for f in self.globs:
            f = re.sub ('/+', '/', f)
            if f.startswith ('/'):
                f = f[1:]
            for exp in glob.glob (os.path.join (self.root, f)):
                globs.append (exp.replace (root, './').replace ('//', '/'))
        if not globs:
            globs.append ('no-globs-for-%(dest)s' % locals ())

        _v = runner.verbose_flag ()
        cmd = 'tar -C %(root)s/%(suffix_dir)s --ignore-failed --exclude="*~"%(_v)s -zcf %(dest)s ' % locals ()
        cmd += ' '.join (globs)
        System (cmd).execute (runner)

# FIXME
class ForcedAutogenMagic (SerializedCommand):
    def __init__ (self, package):
        self.package = package
        SerializedCommand.__init__ (self)
    def system (self, cmd, runner):
        return System (cmd).execute (runner)
    def checksum (self, hasher):
        hasher.append (self.__class__.__name__)
        hasher.append (inspect.getsource (ForcedAutogenMagic.execute))
    def execute (self, runner):
        package = self.package
        autodir = None
        if not autodir:
            autodir = package.srcdir ()
        if os.path.isdir (os.path.join (package.srcdir (), 'ltdl')):
            self.system (package.expand ('rm -rf %(autodir)s/libltdl && cd %(autodir)s && libtoolize --force --copy --automake --ltdl',
                                         locals ()), runner)
        else:
            # fixme
            self.system (package.expand ('cd %(autodir)s && libtoolize --force --copy --automake',
                                         locals ()), runner)

        if os.path.exists (os.path.join (autodir, 'bootstrap')):
            self.system (package.expand ('cd %(autodir)s && ./bootstrap', locals ()), runner)
        elif os.path.exists (os.path.join (autodir, 'autogen.sh')):

            ## --noconfigure ??
            ## is --noconfigure standard for autogen?
            self.system (package.expand ('cd %(autodir)s && bash autogen.sh  --noconfigure',
                                         locals ()), runner)

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
''', locals ()), runner)
            if os.path.exists (package.expand ('%(srcdir)s/Makefile.am')):
                self.system (package.expand ('cd %(srcdir)s && automake --add-missing --foreign', locals ()), runner)

class AutogenMagic (ForcedAutogenMagic):
    def execute (self, runner):
        package = self.package
        if not os.path.exists (package.expand ('%(srcdir)s/configure')):
            if (os.path.exists (package.expand ('%(srcdir)s/configure.ac'))
                or os.path.exists (package.expand ('%(srcdir)s/configure.in'))
                or (not os.path.exists (packmessageage.expand ('%(srcdir)s/Makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/SConstruct')))):
                ForcedAutogenMagic.execute (self, runner)

