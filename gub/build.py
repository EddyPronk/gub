import pickle
import os
import re
import sys
import inspect

#
from gub import misc
from gub import context
from gub import guppackage
from gub import logging
from gub import loggedos
from gub import commands

class Build (context.RunnableContext):
    '''How to build a piece of software

    TODO: move all non configure-make-make install stuff from
    UnixBuild here
    '''

    need_source_tree = False
    source = ''
    branch = ''

    def __init__ (self, settings, source):
        context.RunnableContext.__init__ (self, settings)
        self.source = source
        self.settings = settings
        self.source.connect_logger (logging.default_logger)
        
    def connect_command_runner (self, runner):
        if runner:
            self.source.connect_logger (runner.logger)
        return context.RunnableContext.connect_command_runner (self, runner)

    @context.subst_method
    def checksum_file (self):
        return '%(packages)s/%(name)s%(vc_branch_suffix)s.checksum'
    
    def nop (self):
        pass
    def stages (self):
        return list ()
    def apply_patch (self, name):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/%(name)s
''', locals ())
    def build (self):
        available = dict (inspect.getmembers (self, callable))
        stages = self.stages ()
        tainted = False
        for stage in stages:
            if (not available.has_key (stage)):
                continue

            if self.is_done (stage, stages.index (stage)):
                tainted = True
                continue

            self.runner.stage (' *** Stage: %s (%s, %s)\n'
                               % (stage, self.name (),
                                  self.settings.platform))

            if (stage == 'package' and tainted):
                msg = self.expand ('''This compile has previously been interrupted.
To ensure a repeatable build, this will not be packaged.

Use

rm %(stamp_file)s

to force rebuild, or

--force-package

to skip this check.
''')
                logging.error (msg)
                #FIXME: throw exception.  this plays nice with
                # buildrunner and with bin/gub, so check that.
                sys.exit (1)
            try:
                (available[stage]) ()
            except misc.SystemFailed, e:
                # A failed patch will leave system in unpredictable state.
                if stage == 'patch':
                    self.system ('rm %(stamp_file)s')
                raise e

            if stage != 'clean':
                self.set_done (stage, stages.index (stage))

class UnixBuild (Build):
    '''Build a source package the traditional Unix way

    Based on the traditional configure; make; make install, this class
    tries to do everything including autotooling and libtool fooling.  '''
    
    def __init__ (self, settings, source):
        Build.__init__ (self, settings, source)
        self._dependencies = None
        self._build_dependencies = None
        self.split_packages = []
        self.so_version = '1'

    def stages (self):
        return ['untar', 'patch',
                'configure', 'compile', 'install',

                # see bin/gub TODO
                #'src_package',
                'package', 'clean']

    @context.subst_method
    def LD_PRELOAD (self):
        return '%(gubdir)s/librestrict/librestrict.so'
    
    def get_substitution_dict (self, env={}):
        dict = {
            'CPATH': '',
            'CPLUS_INCLUDE_PATH': '',
            'C_INCLUDE_PATH': '',
            'LIBRARY_PATH': '/empty-means-cwd-in-feisty',
            }
        dict.update (env)
        d = context.RunnableContext.get_substitution_dict (self, dict).copy ()
        return d
          
    def class_invoke_version (self, klas, name):
        name_version = name + '_' + self.version ().replace ('.', '_')
        if klas.__dict__.has_key (name_version):
            klas.__dict__[name_version] (self)

    def download (self):
        self.source.download ()

    def get_repodir (self):
        return self.settings.downloads + '/' + self.name ()
    
    def get_conflict_dict (self):
        """subpackage -> list of confict dict."""
        return {'': [], 'devel': [], 'doc': [], 'runtime': []}
  
    def get_dependency_dict (self):
        """subpackage -> list of dependency dict."""
        # FIMXE: '' always depends on runtime?
        return {'': [], 'devel': [], 'doc': [], 'runtime': [], 'x11': []}
  
    def force_sequential_build (self):
        """Set to true if package can't handle make -jX """
        return False
    
    @context.subst_method
    def name (self):
        file = self.__class__.__module__
        file = re.sub ('_xx_', '++', file)
        file = re.sub ('_x_', '+', file)
        return file

    @context.subst_method
    def pretty_name (self):
        name = self.__class__.__name__
        name = re.sub ('__.*', '', name)
        return name
    
    @context.subst_method
    def file_name (self):
        return self.source.file_name ()

    @context.subst_method
    def source_checksum (self):
        return self.source.checksum ()

    def license_file (self):
        return ['%(srcdir)s/COPYING',
                '%(srcdir)s/COPYING.LIB',
                '%(srcdir)s/LICENSE',
                '%(srcdir)s/LICENCE',]
    
    @context.subst_method
    def basename (self):
        return misc.ball_basename (self.file_name ())

    @context.subst_method
    def packaging_suffix_dir (self):
        return ''

    @context.subst_method
    def full_version (self):
        return self.version ()

    @context.subst_method
    def build_dependencies_string (self):
        deps = sorted (self.get_build_dependencies ())
        return ';'.join (deps)

    # FIXME: move version/branch/tracking macramee to Repository
    @context.subst_method
    def ball_suffix (self):
        # FIXME: ball suffix is also used by %(srcdir)s
        # for tracking repositories, the name of the source and
        # build dir must stay the same.
        if self.source.is_tracking ():
            return self.vc_branch_suffix ()
        return '-' + self.source.version ()

    @context.subst_method
    def vc_branch (self):
        return self.source.full_branch_name ()
    
    @context.subst_method
    def vc_branch_suffix (self):
        b = self.vc_branch ()
        if b:
            b = '-' + b
        return b
        
    @context.subst_method
    def version (self):
        return self.source.version ()

    @context.subst_method
    def name_version (self):
        return '%s-%s' % (self.name (), self.version ())

    @context.subst_method
    def srcdir (self):
        return '%(allsrcdir)s/%(name)s%(ball_suffix)s'

    @context.subst_method
    def builddir (self):
        return '%(allbuilddir)s/%(name)s%(ball_suffix)s'

    @context.subst_method
    def install_root (self):
        return '%(installdir)s/%(name)s-%(version)s-root'

    @context.subst_method
    def install_prefix (self):
        return '%(install_root)s%(prefix_dir)s'

    @context.subst_method
    def install_command (self):
        return '''make %(makeflags)s DESTDIR=%(install_root)s install'''

    @context.subst_method
    def configure_binary (self):
        return '%(srcdir)s/configure'
    
    @context.subst_method 
    def configure_command (self):
        return '%(configure_binary)s --prefix=%(install_prefix)s'

    @context.subst_method
    def compile_command (self):
        return 'make %(makeflags)s '

    @context.subst_method
    def native_compile_command (self):
        c = 'make'

        job_spec = ' '
        if (not self.force_sequential_build ()
            and self.settings.cpu_count_str != '1'):

            job_spec += ' -j%s ' % self.settings.cpu_count_str

        c += job_spec
        return c


    @context.subst_method
    def src_package_ball (self):
        return '%(src_package_uploads)s/%(name)s%(ball_suffix)s-src.%(platform)s.tar.gz'

    @context.subst_method
    def src_package_uploads (self):
        return '%(packages)s'

    @context.subst_method
    def stamp_file (self):
        return '%(statusdir)s/%(name)s-%(version)s-%(source_checksum)s'

    @context.subst_method
    def makeflags (self):
        return ''
    
    def get_stamp_file (self):
        stamp = self.expand ('%(stamp_file)s')
        return stamp

    def is_done (self, stage, stage_number):
        f = self.get_stamp_file ()
        if os.path.exists (f):
            return int (open (f).read ()) >= stage_number
        return False

    def set_done (self, stage, stage_number):
        self.dump ('%(stage_number)d' % locals (), self.get_stamp_file (), 'w')

    def autoupdate (self):
        self.runner._execute (commands.AutogenMagic (self))

    def configure (self):
        self.system ('''
mkdir -p %(builddir)s || true
cd %(builddir)s && %(configure_command)s
''')

    def broken_install_command (self):
        """For packages that do not honor DESTDIR.
        """

        # FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
        # so, must also ./configure that way
        return misc.join_lines ('''make %(makeflags)s install
bindir=%(install_prefix)s/bin
aclocaldir=%(install_prefix)s/share/aclocal
datadir=%(install_prefix)s/share
exec_prefix=%(install_prefix)s
gcc_tooldir=%(install_prefix)s
includedir=%(install_prefix)s/include
infodir=%(install_prefix)s/share/info
libdir=%(install_prefix)s/lib
libexecdir=%(install_prefix)s/lib
mandir=%(install_prefix)s/share/man
prefix=%(install_prefix)s
sysconfdir=%(install_prefix)s/etc
tooldir=%(install_prefix)s
''')

    def kill_libtool_installation_test (self, logger, file):
        loggedos.file_sub (logger, [(r'if test "\$inst_prefix_dir" = "\$destdir"; then',

                                     'if false && test "$inst_prefix_dir" = "$destdir"; then')],
                           file, must_succeed=True)
        
    def update_libtool (self):
        def update (logger, file):
            new = self.expand ('%(system_prefix)s/bin/libtool')
            if not os.path.exists (new):
                logger.write_log ('Cannot update libtool: no such file: %(new)s' % locals (), 'error')
                raise Exception ('barf')

            loggedos.system (logger, 'cp %(new)s %(file)s' % locals())
            self.kill_libtool_installation_test (logger, file)
            loggedos.system (logger, 'chmod 755  %(file)s' %locals ())

        self.map_locate (update, '%(builddir)s', 'libtool')

    def install (self):
        '''Install package into %(install_root).

        Any overrides should follow this command, since it will erase the old
        install_root first.

        FIXME: this is partly totally broken, some overrides need to
        be done BEFORE the rest of the install stage.  We need to
        figure out some clean way to plug something in between the
        automatic cleaning, and the rest of the install.'''
        
        self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
rm -f %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/share/info/dir %(install_root)s%(packaging_suffix_dir)s/%(prefix_dir)s/cross/info/dir %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/info/dir
''')
        self.install_license ()
        self.libtool_installed_la_fixups ()

    def install_license (self):
        def install (logger, lst):
            for file in lst:
                if os.path.exists (file):
                    cmd = self.expand ('''
mkdir -p %(install_root)s/license
cp %(file)s %(install_root)s/license/%(name)s
''', locals ())
                    loggedos.system(logger, cmd)
                    return

        # wtf is misc.lst ?
        self.func (install, map (self.expand, misc.lst(self.license_file ())))

    def libtool_installed_la_fixups (self):
        def installed_la_fixup (logger, la):
            (dir, base) = os.path.split (la)
            base = base[3:-3]
            dir = re.sub (r"^\./", "/", dir)

            loggedos.file_sub (logger, [(''' *-L *[^\"\' ][^\"\' ]*''', ''),
                    (self.expand('''( |=|\')(/[^ ]*usr/lib|%(targetdir)s.*)/lib([^ \'/]*)\.(a|la|so)[^ \']*'''),
                    '\\1-l\\3 '),
                    ('^old_library=.*',
                     self.expand("""old_library='lib%(base)s.a'""", env=locals())),
                    ],
                   la)
            if self.settings.platform.startswith ('mingw'):
                
                loggedos.file_sub (logger, [('library_names=.*',
                                 self.expand("library_names='lib%(base)s.dll.a'", env=locals()))],
                               la)
                
        self.map_locate (installed_la_fixup, '%(install_root)s', 'lib*.la')

    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s')

    def patch (self):
        if self.__class__.__dict__.get ('patches'):
            misc.appy_or_map (self.apply_patch, self.__class__.patches)
        # FIXME: should not misuse patch for auto stuff

        # We cannot easily move this to 'autoupdate' stage now,
        # because some packages depend on this brokennes by redefining
        # patch () to avoid auto-updating.
        self.autoupdate ()

    def rewire_symlinks (self):
        def rewire (logger, file):
            if os.path.islink (file):
                s = os.readlink (file)
                if s.startswith ('/') and self.settings.system_root not in s:
                    new_dest = os.path.join (self.settings.system_root, s[1:])
                    loggedos.remove (logger, file)
                    loggedos.symlink (logger, new_dest, file)

        self.map_locate (rewire, '%(install_root)s', '*',
                         silent=True)

    def package (self):
        self.rewire_symlinks ()
        ps = self.get_packages ()
        for p in ps:
            p.create_tarball ()
            p.dump_header_file ()
            p.clean ()
        self.system ('rm -rf %(install_root)s')
        
    def get_build_dependencies (self):
        return []

    def get_subpackage_definitions (self):
	prefix_dir = self.settings.prefix_dir
        d = {
            'base': [prefix_dir + '/share'],
            'common': [prefix_dir + '/share'],
            'devel': [
            prefix_dir + '/bin/*-config',
            prefix_dir + '/include',
            prefix_dir + '/cross/bin',
            prefix_dir + '/cross/include',
            prefix_dir + '/cross/lib',
            prefix_dir + '/cross/libexec',
            prefix_dir + '/cross/' + self.settings.target_architecture,
            prefix_dir + '/share/aclocal',
            prefix_dir + '/lib/lib*.a',
            prefix_dir + '/lib/pkgconfig',
            ],
            'doc': [
            prefix_dir + '/share/doc',
            prefix_dir + '/share/gtk-doc',
            prefix_dir + '/share/info',
            prefix_dir + '/share/man',
            prefix_dir + '/cross/info',
            prefix_dir + '/cross/man',
            ],
            'runtime': ['/lib', prefix_dir + '/lib', prefix_dir + '/share'],
            'x11': [prefix_dir + '/X11', prefix_dir + '/X11R6'],
            '' : ['/'],
            }
        return d
    
    def get_subpackage_names (self):
        return ['devel', 'doc', '']

    # FIXME: when only patched in via MethodOverride, the real descr_dict,
    # category_dict are not pickled and cygwin packaging fails
    def description_dict (self):
        return {}
    def category_dict (self):
        return {}

    def get_packages (self):
        defs = dict (self.get_subpackage_definitions ())

        ps = []

        conflict_dict = self.get_conflict_dict ()
        dep_dict = self.get_dependency_dict ()
        descr_dict = self.description_dict ()
        category_dict = self.category_dict ()
        
        for sub in self.get_subpackage_names ():
            filespecs = defs[sub]
            
            p = guppackage.GupPackage (self.runner)
            # FIXME: feature envy -> GupPackage constructor/factory
            p._file_specs = filespecs

            p.set_dict (self.get_substitution_dict (), sub)

            conflict_str = ';'.join (conflict_dict.get (sub, []))
            if p._dict.has_key ('conflicts_string'):
                conflict_str = p._dict['conflicts_string'] + ';' + conflict_str
            p._dict['conflicts_string'] = conflict_str

            dep_str = ';'.join (dep_dict.get (sub, []))
            if p._dict.has_key ('dependencies_string'):
                dep_str = p._dict['dependencies_string'] + ';' + dep_str
            p._dict['dependencies_string'] = dep_str

	    # FIXME make generic: use cross.get_subpackage_dict_methods () or similar.
            desc_str = descr_dict.get (sub, '')
            p._dict['description'] = desc_str

            cat_str = category_dict.get (sub, '')
            p._dict['category'] = cat_str
            
            ps.append (p)

        return ps
    
    def src_package (self):
        # URG: basename may not be source dir name, eg,
        # package libjpeg uses jpeg-6b.  Better fix at untar
        # stage?
        dir_name = re.sub (self.expand ('%(allsrcdir)s/'), '',
                           self.expand ('%(srcdir)s'))
        _v = '' #self.os_interface.verbose_flag ()
        self.system ('''
tar -C %(allsrcdir)s --exclude "*~" --exclude "*.orig"%(_v)s -zcf %(src_package_ball)s %(dir_name)s
''',
                     locals ())

    def clean (self):
        self.system ('rm -rf  %(stamp_file)s %(install_root)s', locals ())
        if self.source.is_tracking ():
            # URG
            return
        self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

    def untar (self):
        self.runner._execute (commands.UpdateSourceDir (self))

    # used for cygwin. -- most probably broken due to deferred restructuring.
    def pre_install_smurf_exe (self):
        def un_exe (logger_why_already_in_self, file):
            base = os.path.splitext (file)[0]
# Hmm, cannot (yet) use our nice Runner/logged os interface (again)?
# This should have been fixed already?                
# gur, Must manually expand and pass logger...
#            self.runner.system ('mv %(file)s %(base)s', locals ())
            loggedos.system (logger_why_already_in_self, self.expand ('mv %(file)s %(base)s', locals ()))
        self.map_locate (no_exe, '%(builddir)s', '*.exe')

    def post_install_smurf_exe (self):
        def add_exe (logger_why_already_in_self, file):
            if (not os.path.islink (file)
                and not os.path.splitext (file)[1]
# Hmm, cannot (yet) use our nice Runner/logged os interface (again)?
# This should have been fixed already?                
#                and self.runner.read_pipe ('file -b %(i)s', locals ()).startswith ('MS-DOS executable PE')):
#                self.runner.system ('mv %(i)s %(file)s.exe', locals ())
#    and self.runner.read_pipe ('file -b %(i)s', locals ()).startswith ('MS-DOS executable PE')):
#AttributeError: 'NoneType' object has no attribute 'read_pipe'
# gur, Must manually expand and pass logger...
                and loggedos.read_pipe (logger_why_already_in_self, self.expand ('file -b %(file)s', locals ())).startswith ('MS-DOS executable PE')):
                loggedos.system (logger_why_already_in_self, self.expand ('mv %(file)s %(file)s.exe', locals ()))
        self.map_locate (add_exe, '%(install_root)s/bin', '*')
        self.map_locate (add_exe, '%(install_prefix)s/bin', '*')

    def install_readmes (self):
        cmd = self.system ('''
mkdir -p %(install_prefix)s/share/doc/%(name)s
''')
        
        def copy_readme (logger_why_already_in_self, file):
            if (os.path.isfile (file)
                and not os.path.basename (file).startswith ('Makefile')
                and not os.path.basename (file).startswith ('GNUmakefile')):
# Hmm, cannot (yet) use our nice Runner/logged os interface (again)?
# This should have been fixed already?                
#                self.runner.system ('cp %(file)s %(install_prefix)s/share/doc/%(name)s', locals ())
# gur, Must manually expand and pass logger...
                loggedos.system (logger_why_already_in_self, self.expand ('cp %(file)s %(install_prefix)s/share/doc/%(name)s', locals ()))

        self.map_locate (copy_readme, '%(srcdir)s', '[A-Z]*')

    def build_version (self):
        "the version in the shipped package."
        # FIXME: ugly workaround needed for lilypond package...
        return '%(version)s'

class BinaryBuild (UnixBuild):
    def stages (self):
        return ['untar', 'install', 'package', 'clean']
    def install (self):
        self.system ('mkdir -p %(install_root)s')
        _v = '' #self.os_interface.verbose_flag ()
        self.system ('tar -C %(srcdir)s -cf- . | tar -C %(install_root)s%(_v)s -p -xf-', env=locals ())
        self.libtool_installed_la_fixups ()
    def get_subpackage_names (self):
        # FIXME: splitting makes that cygwin's gettext + -devel subpackage
        # gets overwritten by cygwin's gettext-devel + '' base package
        return ['']

class NullBuild (UnixBuild):
    """Placeholder for downloads """
    def stages (self):
        return ['patch', 'install', 'package', 'clean']
    def patch (self):
        # FIXME: urg, only for disabling autotooling
        pass
    def get_subpackage_names (self):
        return ['']
    def install (self):
        self.system ('mkdir -p %(install_root)s')

class SdkBuild (NullBuild):
    def stages (self):
        return ['untar', 'patch', 'install', 'package', 'clean']
    def install_root (self):
        return self.srcdir ()
