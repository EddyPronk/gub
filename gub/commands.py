import glob
import inspect
import os
import re
import traceback
# import md5

from gub import misc
from gub import loggedos

class SerializedCommand:
    def __init__ (self):
        self.instantiation_traceback = traceback.extract_stack ()
        self.is_checksummed = True
        
    def execute (self, logger):
        raise NotImplemented
    
    def get_source (self):
        return ''.join (traceback.format_list (self.instantiation_traceback))

    def checksum (self, hasher):
        hasher (self.__class__.__name__)

class Nop (SerializedCommand):
    def __init__ (self):
        self.is_checksummed = False
    def execute (self):
        pass
    def checksum (self, hasher):
        pass

class UpdateSourceDir (SerializedCommand):
    def __init__ (self, buildspec):
        self.buildspec = buildspec

    def execute (self, logger):
        buildspec = self.buildspec 
        if not buildspec.source:
            return False
        if not buildspec.source.is_tracking ():
            command = buildspec.expand ('rm -rf %(srcdir)s %(builddir)s %(install_root)s')
            loggedos.system (logger, command)

        if buildspec.source:
            buildspec.source.update_workdir (buildspec.expand ('%(srcdir)s'))

        # TODO: move this to Repository
        if (os.path.isdir (buildspec.expand ('%(srcdir)s'))):
            cmd = buildspec.expand ('chmod -R +w %(srcdir)s')
            loggedos.system (logger, cmd, ignore_errors=True)
           
    def checksum (self, hasher):
        tracking = 'not tracking'
        if self.buildspec.source.is_tracking ():
            tracking  = 'tracking'

        hasher ('UpdateSourceDir(%(tracking)s)' % locals ())
        
class System (SerializedCommand):
    def __init__ (self, c, env={}, ignore_errors=False):
        SerializedCommand.__init__ (self)
        self.command = c
        self.env = env
        self.ignore_errors = ignore_errors
    def __repr__ (self):
        return 'System (%s)' % repr (self.command)
    def checksum (self, hasher):
        hasher (self.command)
        # TODO: use env too.
    def execute (self, logger):
#        return loggedos.system (logger, self.command, **self.kwargs)
        return loggedos.system (logger, self.command, env=self.env,
                                ignore_errors=self.ignore_errors)

class Copy (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (self.src)
        hasher (self.dest)
    def execute (self, logger):
        loggedos.copy2 (logger, self.src, self.dest)


class Func (SerializedCommand):
    def __init__ (self, func, *args):
        self.func = func
        self.args = args
    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (inspect.getsource (self.func))
        hasher (repr (self.args))
    def execute (self, logger):
        return self.func (logger, *self.args)

class Message (SerializedCommand):
    def __init__ (self, message, message_type):
        self.message = message
        self.message_type = message_type
        self.is_checksummed = False
    def execute (self, logger):
        logger.write_log (self.message, self.message_type)
        
    def checksum (self, hasher):
        pass

class MapLocate (SerializedCommand):
    def __init__ (self, func, directory, pattern,
                  must_happen=False, silent=False):
        self.func = func
        self.directory = directory
        self.pattern = pattern
        self.must_happen = must_happen
        self.silent = silent

    def execute (self, logger):
        files = misc.locate_files (self.directory, self.pattern)
        if self.must_happen and files == []:
            logger.write_log ('did not find files matching pattern')
            raise 'MapLocate failed'

        # huh, what is silent?
        func = self.func.__name__
        if self.silent:
            dir = self.directory
            pattern = self.pattern
            count = len (files)
            logger.write_log ('Mapping %(func)s () over %(dir)s/%(pattern)s (%(count)d files)\n' % locals (), 'action')
            
        for file_name in files:
            if not self.silent:
                logger.write_log ('Applying %(func)s () to %(file_name)s\n' % locals (), 'action')
            self.func (logger, file_name)

    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (inspect.getsource (self.func))
        hasher (self.directory)
        hasher (self.pattern)

class Dump (SerializedCommand):
    def __init__ (self, *args, **kwargs):
        SerializedCommand.__init__ (self)
        self.args = args
        self.kwargs = kwargs
    def __repr__ (self):
        return 'Dump (%s)' % repr (self.args)
    def checksum (self, hasher):
        str, name = self.args
        hasher (self.__class__.__name__)
        hasher (name)
# this keeps builds log a lot smaller, but not handy for development.
#        hasher (md5.md5 (str).hexdigest ())
        hasher (str)
    def execute (self, logger):
        str, name = self.args

        kwargs = self.kwargs
        mode = 'w'
        if 'mode' in self.kwargs:
          mode = kwargs['mode']
          del kwargs['mode']
          
        loggedos.dump_file (logger, str, name, mode, **kwargs)


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
        hasher (self.__class__.__name__)
        hasher (name)
        for (src, dst) in re_pairs:
            hasher (src)
            hasher (dst)

    def execute (self, logger):
        (re_pairs, name) = self.args

        loggedos.file_sub (logger, re_pairs, name, **self.kwargs)
        
class Conditional (SerializedCommand):
    def __init__ (self, predicate, true_command, false_command=None):
        SerializedCommand.__init__ (self)
        self.predicate = predicate
        self.true_command = true_command
        self.false_command = false_command
    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (inspect.getsource (self.predicate))
        if self.true_command:
            self.true_command.checksum (hasher)
        if self.false_command:
            self.false_command.checksum (hasher)
    def execute (self, logger):
        if self.predicate ():
            return self.true_command.execute (logger)
        elif self.false_command:
            return self.false_command.execute (logger)

class ShadowTree (SerializedCommand):
    def __init__ (self, src, dest):
        self.src = src
        self.dest = dest
    def execute (self, logger):
        '''Symlink files from SRC in TARGET recursively'''
        loggedos.shadow (logger, self.src, self.dest)
    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (self.src)
        hasher (self.dest)

class Chmod (SerializedCommand):
    def __init__ (self, *args):
        self.args = args
    def execute (self, logger):
        loggedos.chmod (logger, *self.args)
    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        map (hasher, map (str, self.args))

class PackageGlobs (SerializedCommand):
    def __init__ (self, root, suffix_dir, globs, dest):
        self.globs = globs
        self.root = root
        self.suffix_dir = suffix_dir
        self.dest = dest

    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (''.join (self.globs))
        hasher (self.root)
        hasher (self.suffix_dir)
        hasher (self.dest)

    def execute (self, logger):
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

        _v = logger.verbose_flag ()
        cmd = 'tar -C %(root)s/%(suffix_dir)s --ignore-failed --exclude="*~"%(_v)s -zcf %(dest)s ' % locals ()
        cmd += ' '.join (globs)
        loggedos.system (logger, cmd)

# FIXME
class ForcedAutogenMagic (SerializedCommand):
    def __init__ (self, package):
        self.package = package
        SerializedCommand.__init__ (self)
    def system (self, cmd, logger):
        return loggedos.system (logger, cmd)
    def checksum (self, hasher):
        hasher (self.__class__.__name__)
        hasher (inspect.getsource (ForcedAutogenMagic.execute))
    def execute (self, logger):
        package = self.package
        autodir = package.expand ('%(autodir)s')
        PATH = package.expand ('%(PATH)s')
        if os.path.exists (os.path.join (autodir, 'bootstrap')):
            self.system ('cd %(autodir)s && ./bootstrap' % locals (), logger)
        elif os.path.exists (os.path.join (autodir, 'bootstrap.sh')):
            self.system ('cd %(autodir)s && ./bootstrap.sh' % locals (), logger)
        elif os.path.exists (os.path.join (autodir, 'autogen.sh')):
            s = file ('%(autodir)s/autogen.sh' % locals ()).read ()
            noconfigure = ' --help'
            if '--noconfigure' in s:
                noconfigure = ' --noconfigure' + noconfigure
            self.system ('cd %(autodir)s && NOCONFIGURE=1 bash autogen.sh %(noconfigure)s' % locals (),
                         logger)
        else:
            libtoolize = misc.path_find (PATH, 'libtoolize')
            if libtoolize:
                s = file (libtoolize).read ()
                libtoolize = 'libtoolize --copy --force'
                # --automake is mandatory for libtool-1.5.2x, but breaks with libtool-2.2.x
                # --install is mandatory for libtool-2.2.x, but breaks with libtool-1.5.2x
                # mandatory means: so that config.guess, config.sub are refreshed iso removed
                if '--automake' in s:
                    libtoolize += ' --automake'
                if '--install' in s:
                    libtoolize += ' --install'
                if (os.path.isdir (os.path.join (autodir, 'ltdl'))
                    or os.path.isdir (os.path.join (autodir, 'libltdl'))):
                    libtoolize += ' --ltdl'
                self.system ('rm -rf %(autodir)s/libltdl %(autodir)s/ltdl && (cd %(autodir)s && %(libtoolize)s'
                             % locals (), logger)
            aclocal_opt = ''
            if os.path.exists (package.expand ('%(system_prefix)s/share/aclocal')):
                aclocal_opt = package.expand ('-I %(system_prefix)s/share/aclocal')

            headcmd = ''
            configure = ''
            for c in ('configure.in','configure.ac'):
                try:
                    str = file ('%(autodir)s/%(c)s' % locals ()).read ()
                    configure = c
                    m = re.search ('A[CM]_CONFIG_HEADER', str)
                    str = 0   ## don't want to expand str
                    if m:
                        headcmd = 'cd %(autodir)s && autoheader %(aclocal_opt)s' % locals ()
                        break
                except IOError:
                    pass
            if configure:
                self.system ('''
cd %(autodir)s && aclocal %(aclocal_opt)s
%(headcmd)s
cd %(autodir)s && autoconf %(aclocal_opt)s
''' % locals (), logger)
            if os.path.exists ('%(autodir)s/Makefile.am' % locals ()):
                self.system ('cd %(autodir)s && automake --add-missing --copy --foreign' % locals (), logger)

class AutogenMagic (ForcedAutogenMagic):
    def execute (self, logger):
        package = self.package
        if not os.path.exists (package.expand ('%(autodir)s/configure')):
            if (os.path.exists (package.expand ('%(autodir)s/configure.ac'))
                or os.path.exists (package.expand ('%(autodir)s/configure.in'))
                or (not os.path.exists (package.expand ('%(autodir)s/Makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/Makefile'))
                    and not os.path.exists (package.expand ('%(builddir)s/Makefile'))
                    and not os.path.exists (package.expand ('%(autodir)s/makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/makefile'))
                    and not os.path.exists (package.expand ('%(builddir)s/makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/makefile'))
                    and not os.path.exists (package.expand ('%(srcdir)s/SConstruct')))):
                ForcedAutogenMagic.execute (self, logger)

class CreateShar (SerializedCommand):
    def __init__ (self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def checksum (self, hasher):
        hasher (repr (('CreateShar', self.args, self.kwargs)))
        
    def execute (self, logger):
        (file, hello, head, shar) = self.args
        logger.write_log ('Creating shar file from %s\n' % repr (self.args), 'info') 
        length = os.stat (file)[6]
        base_file = os.path.split (file)[1]
        script = loggedos.read_file (logger, head)
        header_length = 0
        _z = misc.compression_flag (file)
        header_length = len (script % locals ()) + 1
        used_in_sharhead = '%(base_file)s %(hello)s %(header_length)s %(_z)s'
        used_in_sharhead % locals ()
        loggedos.dump_file (logger, script % locals (), shar)
        loggedos.system (logger, 'cat %(file)s >> %(shar)s' % locals ())
        loggedos.chmod (logger, shar, 0755)
        loggedos.system (logger, 'rm %(file)s' % locals ())

