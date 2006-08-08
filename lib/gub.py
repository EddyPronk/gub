# own
import cvs
import download
import glob
import misc
import locker

# sys
import pickle
import os
import re
import string
import subprocess
import sys
import md5

from context import *

class PackageSpec:
    "How to package part of an install_root."
    
    def __init__ (self, os_interface):
        self._dict = {}
        self._os_interface = os_interface
        self._file_specs = []
        self._dependencies = []
        
    def set_dict (self, dict, sub_name):
        self._dict = dict.copy ()
        self._dict['sub_name'] = sub_name
        
        if sub_name:
            sub_name = '-' + sub_name

        s = ('%(name)s' % dict) + sub_name

        branch = self.expand ('%(vc_branch)s')

        if branch:
            self._dict['vc_branch_suffix'] = '-' + branch
        else:
            self._dict['vc_branch_suffix'] = ''
            
        self._dict['split_name'] = s
        self._dict['split_ball'] = '%(gub_uploads)s/%(split_name)s-%(version)s.%(platform)s.gup' % self._dict
        self._dict['split_hdr'] = '%(gub_uploads)s/%(split_name)s%(vc_branch_suffix)s.%(platform)s.hdr' % self._dict

        deps =  ';'.join (self._dependencies)
        self._dict['dependencies_string'] = deps

    def expand (self, s):
        return s % self._dict
    
    def dump_header_file (self):
        hdr = self.expand ('%(split_hdr)s' )
        self._os_interface.dump (pickle.dumps (self._dict), hdr)
        
    def clean (self):
        for f in self._file_specs:
            base = self.expand ('rm -rf %(install_root)s/')
            self._os_interface.system (base + f)
            
    def create_tarball (self):
        cmd = 'tar -C %(install_root)s --ignore-failed --exclude="*~" -zcf %(split_ball)s '
        cmd += (' '.join ('$(cd %%(install_root)s && echo ./%s)'
                          % f for f in self._file_specs)).replace ('//','/')
        cmd = self.expand (cmd)
        self._os_interface.system (cmd)

    def dict (self):
        return self._dict

    def name (self):
        return "%(split_name)s" % self._dict
    
class BuildSpec (Os_context_wrapper):
    def __init__ (self, settings):
        Os_context_wrapper.__init__(self, settings)

        self.verbose = settings.verbose ()
        self.settings = settings
        self.url = ''
        self.has_source = True
        self._downloader = self.wget
        self._dependencies = None
        self._build_dependencies = None
        
        self.spec_checksum = '0000' 
        self.cross_checksum = '0000'
        
        # set to true for CVS releases
        self.track_development = False
        self.split_packages = []
        self.sover = '1'

    # urg: naming conflicts with module.
    def do_download (self):
        self._downloader ()

    def get_dependency_dict (self):
        """subpackage -> list of dependency dict."""
        
        return {'': []}
  
    def broken_for_distcc (self):
        """Set to true if package can't handle make -jX """
        return False
    
    def is_downloaded (self):
        if not self.has_source:
            return True
        
        name = self.expand ('%(downloaddir)s/%(file_name)s')
        return os.path.exists (name)
    
    def wget (self):
        if not self.is_downloaded ():
            misc.download_url (self.expand (self.url), self.expand ('%(downloaddir)s'))
            
    def cvs (self):

        
        dir = self.expand ('%(name)s-%(version)s')
        cvs_dest = self.expand ('%(downloaddir)s/%(dir)s' , locals ())
        timestamp_file = cvs_dest + '/.cvsup-timestamp'
        
        ## don't run CVS too often.
        import time
        time_window = 10
        if (os.path.exists (timestamp_file)
            and misc.file_mod_time (timestamp_file) > time.time () - time_window):
            return

        ## TODO: should use locking.
        if os.path.isdir (cvs_dest):
            open (timestamp_file, 'w').write ('changed')

        lock_file = self.expand ('%(downloaddir)s/%(name)s-%(version)s.lock')
        lock = locker.Locker (lock_file)
        url = self.expand (self.url)
        if not os.path.exists (cvs_dest):
            self.system ('''
cd %(downloaddir)s && cvs -d %(url)s -q co -d %(dir)s -r %(version)s %(name)s
''', locals ())
        else:
            self.system ('''
cd %(cvs_dest)s && cvs -q update -dAPr %(version)s
''', locals ())

        ## again: cvs up can take a long time.
        open (timestamp_file, 'w').write ('changed')

        self.touch_cvs_checksum (cvs_dest)

    def touch_cvs_checksum (self, cvs_dest):
        
        ## checksumming is necessary, otherwise
        ## we can have out-of-date files installed.
        cvs_dirs =  []
        for (base, dirs, files) in os.walk (cvs_dest):
            cvs_dirs += [os.path.join (base, d) for d in dirs
                         if d == 'CVS']
            
        checksum = md5.md5()
        for d in cvs_dirs:
            checksum.update (open (os.path.join (d, 'Entries')).read ())
        open (self.cvs_checksum_file (),'w').write (checksum.hexdigest ())

        
    @subst_method
    def name (self):
        file = self.__class__.__name__.lower ()
        file = re.sub ('__.*', '', file)
        file = re.sub ('_', '-', file)
        return file


    @subst_method
    def file_name (self):
        file = re.sub ('.*/([^/]+)', '\\1', self.url)
        return file

    def cvs_checksum_file (self):
        dir = '%s/%s-%s/' % (self.settings.downloaddir, self.name(),
                             self.version ())

        file = '%s/.cvs-checksum' % dir
        return file

    @subst_method
    def source_checksum (self):
        if not self.track_development:
            return '0000'
        
        file = self.cvs_checksum_file ()
        if os.path.exists (file):
            return open (file).read ()
    
        return '0000'
    
    @subst_method
    def basename (self):
        f = self.file_name ()
        f = re.sub ('.tgz', '', f)
        f = re.sub ('-src\.tar.*', '', f)
        f = re.sub ('\.tar.*', '', f)
        f = re.sub ('_%\(package_arch\)s.*', '', f)
        f = re.sub ('_%\(version\)s', '-%(version)s', f)
        return f

    @subst_method
    def vc_branch (self):
        if self.track_development:
            return '%(version)s'
        else:
            return ''

    @subst_method
    def full_version (self):
        return self.version ()

    @subst_method
    def build_dependencies_string (self):
        deps = self.get_build_dependencies ()
        return ';'.join (deps)

    @subst_method
    def version (self):
        return misc.split_version (self.ball_version)[0]

    @subst_method
    def name_version (self):
        return '%s-%s' % (self.name (), self.version ())

    @subst_method
    def srcdir (self):
        return self.settings.allsrcdir + '/' + self.basename ()

    @subst_method
    def builddir (self):
        return self.settings.allbuilddir + '/' + self.basename ()

    @subst_method
    def install_root (self):
        return '%(installdir)s/%(name)s-%(version)s-root'

    @subst_method
    def install_prefix (self):
        return self.install_root () + '/usr'

    @subst_method
    def install_command (self):
        return '''make DESTDIR=%(install_root)s install'''

    @subst_method
    def configure_command (self):
        return '%(srcdir)s/configure --prefix=%(install_prefix)s'

    @subst_method
    def compile_command (self):
        return 'make'

    @subst_method
    def native_compile_command (self):
        c = 'make'
        if (self.settings.native_distcc_hosts):
            jobs = '-j%d ' % (2*len (self.settings.native_distcc_hosts.split (' ')))

            ## do this a little complicated: we don't want a trace of
            ## distcc during configure.
            c = 'DISTCC_HOSTS="%s" %s %s' % (self.settings.native_distcc_hosts, c, jobs)
            c = 'PATH="%(native_distcc_bindir)s:$PATH" ' + c
            
        return c


    @subst_method
    def gub_name_src (self):
        return '%(name)s-%(version)s-src.%(platform)s.gub'

    @subst_method
    def gub_src_uploads (self):
        return '%(gub_uploads)s'

    @subst_method
    def stamp_file (self):
        return '%(statusdir)s/%(name)s-%(version)s'

    @subst_method
    def rsync_command (self):
        return "rsync --exclude CVS -v -a %(downloaddir)s/%(name)s-%(version)s/ %(srcdir)s"

    def get_stamp_file (self):
        stamp = self.expand ('%(stamp_file)s')
        return stamp

    def is_done (self, stage, stage_number):
        f = self.get_stamp_file ()
        if os.path.exists (f):
            return int (open (f).read ()) >= stage_number
        return False

    def set_done (self, stage, stage_number):
        open (self.get_stamp_file (),'w'). write ('%d' % stage_number) 

    def autoupdate (self, autodir=0):
        if not autodir:
            autodir = self.srcdir ()
        if os.path.isdir (os.path.join (self.srcdir (), 'ltdl')):
            self.system ('''
rm -rf %(autodir)s/libltdl
cd %(autodir)s && libtoolize --force --copy --automake --ltdl
''', locals ())
        else:
            self.system ('''
cd %(autodir)s && libtoolize --force --copy --automake
''', locals ())
        if os.path.exists (os.path.join (autodir, 'bootstrap')):
            self.system ('''
cd %(autodir)s && ./bootstrap
''', locals ())
        elif os.path.exists (os.path.join (autodir, 'autogen.sh')):
            self.system ('''
cd %(autodir)s && bash autogen.sh --noconfigure
''', locals ())
        else:
            self.system ('''
cd %(autodir)s && aclocal -I %(system_root)s/usr/share/aclocal
cd %(autodir)s && autoheader -I %(system_root)s/usr/share/aclocal
cd %(autodir)s && autoconf -I %(system_root)s/usr/share/aclocal
''', locals ())
            if os.path.exists (self.expand ('%(srcdir)s/Makefile.am')):
                self.system ('''
cd %(srcdir)s && automake --add-missing --foreign
''', locals ())


    def configure (self):
        self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

    def broken_install_command (self):
        """For packages that do not honor DESTDIR.
        """

        # FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
        # so, must also ./configure that way
        return misc.join_lines ('''make install
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

    def kill_libtool_installation_test (self, file):
        self.file_sub ([(r'if test "\$inst_prefix_dir" = "\$destdir"; then',
                         'if false && test "$inst_prefix_dir" = "$destdir"; then')],
                       file, must_succeed=True)
        
    def update_libtool (self):
        new_lt = self.expand ('%(system_root)s/usr/bin/libtool')

        if os.path.exists (new_lt):
            for lt in self.locate_files ('%(builddir)s', 'libtool'):
                self.system ('cp %(new_lt)s %(lt)s', locals ())
                self.kill_libtool_installation_test (lt)
                self.system ('chmod 755  %(lt)s', locals ())
        else:
            self.log_command ("Cannot update libtool without libtools in %(system_root)s/usr/bin/.")
            raise 'barf'

    def install (self):
        self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
rm -f %(install_root)s/usr/share/info/dir %(install_root)s/usr/cross/info/dir %(install_root)s/usr/info/dir
''')
        self.libtool_installed_la_fixups ()

    def libtool_installed_la_fixups (self):
        for la in misc.find (self.expand ('%(install_root)s'), '\.la$'):
            (dir, base) = os.path.split (la)
            base = base[3:-3]
            dir = re.sub (r"^\./", "/", dir)
            full_la = self.expand ("%(install_root)s/%(la)s", locals())

            self.file_sub ([(''' *-L *[^\"\' ][^\"\' ]*''', ''),
                    ('''( |=|\')(/[^ ]*usr/lib|%(targetdir)s.*)/lib([^ \'/]*)\.(a|la|so)[^ \']*''',
                    '\\1-l\\3 '),
                    ('^old_library=.*',
                    """old_library='lib%(base)s.a'"""),
                    ],
                   full_la, env=locals ())
            if self.settings.platform.startswith ('mingw'):
                self.file_sub ([('library_names=.*',
                                 "library_names='lib%(base)s.dll.a'")],
                               full_la, env=locals())

            # avoid using libs from build platform, by adding %(system_root)s
            self.file_sub ([('^libdir=.*',
                             """libdir='%(system_root)s/%(dir)s'"""),
                            ],
                           full_la, env=locals ())

    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s')

    # FIXME: should not misusde patch for auto stuff
    def patch (self):
        if not os.path.exists ('%(srcdir)s/configure' \
                   % self.get_substitution_dict ()):
            self.autoupdate ()

    @subst_method
    def is_sdk_package (self):
        return 'false'
    
    def package (self):
        ps = self.get_packages ()
        for p in ps:
            p.create_tarball ()
            p.dump_header_file ()
            p.clean ()
            
    def get_build_dependencies (self):
        return []

    def get_subpackage_definitions (self):
        return {'devel': ['/usr/include',
                          '/usr/cross/include',
                          '/usr/share/aclocal',
                          '/usr/lib/lib*.a',
                          '/usr/lib/pkgconfig',
                    ],
                'doc': ['/usr/share/doc',
                        '/usr/share/gtk-doc',
                        '/usr/share/info',
                        '/usr/share/man',
                        '/usr/cross/info',
                        '/usr/cross/man',
                        ],
                '': ['/'],
                }

    def get_subpackage_names (self):
        return ['devel','doc','']
    
    def get_packages (self):
        defs = dict (self.get_subpackage_definitions ())

        ps = []
        
        for sub in self.get_subpackage_names ():
            filespecs = defs[sub]
            
            p = PackageSpec (self.os_interface)
            if sub:
                p._dependencies = [self.expand ("%(name)s")]
                
            p._file_specs = filespecs
            p.set_dict (self.get_substitution_dict (), sub)
            ps.append (p)

        d = self.get_dependency_dict ()
        
        for p in ps: 
            name = p.expand ('%(sub_name)s')
            if not d.has_key (name):
                continue

            assert type (d[name]) == type([])
            deps = ';'.join (d[name])
            if p._dict['dependencies_string']:
                deps = ';' + deps
                
            p._dict['dependencies_string'] += deps

        return ps
    
    def src_package (self):
        # URG: basename may not be source dir name, eg,
        # package libjpeg uses jpeg-6b.  Better fix at untar
        # stage?
        dir_name = re.sub (self.expand ('%(allsrcdir)s/'), '',
                 self.expand ('%(srcdir)s'))
        self.system ('''
tar -C %(allsrcdir)s --exclude "*~" --exclude "*.orig"  -zcf %(gub_src_uploads)s/%(gub_name_src)s %(dir_name)s
''',
                     locals ())

    def clean (self):
        self.system ('rm -rf  %(stamp_file)s %(install_root)s', locals ())
        if self.track_development:
            return

        self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

    def _untar (self, dir):
        tarball = self.expand("%(downloaddir)s/%(file_name)s")
        if not os.path.exists (tarball):
            raise 'no such file: ' + tarball
        if self.format == 'deb':
            self.system ('''
mkdir -p %(srcdir)s
ar p %(tarball)s data.tar.gz | tar -C %(dir)s -zxf-
''',
                  locals ())
        else:
            flags = download.untar_flags (tarball)
            self.system ('''
tar -C %(dir)s %(flags)s %(tarball)s
''',
                  locals ())

    def untar (self):
        if self.track_development:
            ## cp options are not standardized.
            self.system (self.rsync_command ())
        else:
            self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
''')
            self._untar ('%(allsrcdir)s')

        self.system ('cd %(srcdir)s && chmod -R +w .')

    def with (self, version='HEAD', mirror=download.gnu,
              format='gz', 
              track_development=False
              ):
        
        self.format = format
        self.ball_version = version
        ball_version = version
        
        self.track_development = track_development
        self.url = mirror

        ## don't do substitution. We want to postpone
        ## generating the dict until we're sure it doesn't change.

        return self

class BinarySpec (BuildSpec):
    def untar (self):
        self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
''')
        self.system ('mkdir -p %(srcdir)s/root')
        self._untar ('%(srcdir)s/root')

    def configure (self):
        pass

    def patch (self):
        pass

    def compile (self):
        pass

    def install (self):
        
        """Install package into %(install_root). Any overrides should
        follow this command, since it will erase the old install_root first."""
        
        self.system ('mkdir -p %(install_root)s')
        _verbose = ''
        if self.verbose:
            _verbose = ' -v'
        self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s%(_verbose)s -xf-', env=locals ())
        self.libtool_installed_la_fixups ()

class NullBuildSpec (BuildSpec):
    """Placeholder for downloads """

    def compile (self):
        pass
    def configure (self):
        pass
    def install (self):
        self.system ('mkdir -p %(install_root)s')
    def untar (self):
        pass
    def patch (self):
        pass
    def src_package (self):
        pass

class SdkBuildSpec (NullBuildSpec):
    def untar (self):
        BuildSpec.untar (self)

    def get_subpackage_names (self):
        return ['']
    
    ## UGH: should store superclass names of each package.
    def is_sdk_package (self):
        return 'true'
    
    def install_root (self):
        return self.srcdir()

class Change_target_dict:
    def __init__ (self, package, override):
        self._target_dict_method = package.get_substitution_dict
        self._add_dict = override

    def target_dict (self, env={}):
        env_copy = env.copy()
        env_copy.update (self._add_dict)
        d = self._target_dict_method (env_copy)
        return d

    def append_dict (self, env= {}):
        d = self._target_dict_method ()
        for (k,v) in self._add_dict.items ():
            d[k] += v

        d.update (env)
        d = recurse_substitutions (d)
        return d

def change_target_dict (package, add_dict):
    """Override the get_substitution_dict() method of PACKAGE."""
    try:
        package.get_substitution_dict = Change_target_dict (package, add_dict).target_dict
    except AttributeError:
        pass

def append_target_dict (package, add_dict):
    """Override the get_substitution_dict() method of PACKAGE."""
    try:
        package.get_substitution_dict = Change_target_dict (package, add_dict).append_dict
    except AttributeError:
        pass

def get_base_package_name (name):
    name = re.sub ('-devel$', '', name)

    # breaks mingw dep resolution, mingw-runtime
    ##name = re.sub ('-runtime$', '', name)
    name = re.sub ('-doc$', '', name)
    return name
