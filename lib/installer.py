import os
import re
import time

import context
import darwintools
import gup
import targetpackage

from context import subst_method
from misc import *

class Installer (context.Os_context_wrapper):
    def __init__ (self, settings):
        context.Os_context_wrapper.__init__ (self, settings)
        
        self.settings = settings
        self.strip_command = '%(cross_prefix)s/bin/%(target_architecture)s-strip' 
        self.no_binary_strip = []
        self.no_binary_strip_extensions = ['.la', '.py', '.def',
                                           '.scm', '.pyc']

        #WTF?
        self.installer_root = '%(targetdir)s/installer-%(lilypond_branch)s'
        self.installer_db = '%(targetdir)s/installer-%(lilypond_branch)s-dbdir'
        self.installer_uploads = settings.uploads
        self.installer_version = None
        self.installer_build = None
      
    @context.subst_method
    def name (self):
        return 'lilypond'

    @context.subst_method
    def version (self):
        return self.settings.installer_version

    def strip_prefixes (self):
        return ['', 'usr/']
        
    def strip_unnecessary_files (self):
        "Remove unnecessary cruft."

        delete_me = ''
        for p in self.strip_prefixes ():
            delete_me += p + '%(i)s '

        for i in (
            'bin/autopoint',
            'bin/glib-mkenums',
            'bin/guile-*',
            'bin/*-config',
            'bin/*gettext*',
            'bin/[cd]jpeg',
            'bin/envsubst*',
            'bin/glib-genmarshal*',
            'bin/gobject-query*',
            'bin/gspawn-win32-helper*',
            'bin/gspawn-win32-helper-console*',
            'bin/msg*',
            'bin/pango-querymodules*',
            'bin/xmlwf',
            'cross',
            'doc',
            'include',
            'info',
            'lib/gettext',
            'lib/gettext/hostname*',
            'lib/gettext/urlget*',
            'lib/glib-2.0/include/glibconfig.h',
            'lib/glib-2.0',
            'lib/libc.*',
            'lib/libm.*',
            'lib/pkgconfig',
            'lib/*~',
            'lib/*.a',
            'lib/python*/distutils/command/wininst-6*',
            'lib/python*/distutils/command/wininst-7.1*',
            'man',
            'share/doc',
            'share/guile/*/ice-9/debugger/',
            'share/gettext/intl',
            'share/ghostscript/*/{Resource,doc,examples}/',
            'share/gs/*/{Resource,doc,examples}/',
            'share/gtk-doc',
            'share/info',
            'share/fonts/',
            'share/man',
            'share/omf',
            'share/libtool/',

            # prune harder
            'lib/python*/bsddb',
            'lib/python*/compiler',
            'lib/python*/curses',
            'lib/python*/distutils',
            'lib/python*/email',
            'lib/python*/hotshot',
            'lib/python*/idlelib',
            'lib/python*/lib-old',
            'lib/python*/lib-tk',
            'lib/python*/logging',
            'lib/python*/test',
# xml2ly needs xml.dom
#                        'lib/python*/xml',
            'share/lilypond/*/make',
            'share/gettext',
            'usr/share/aclocal',
            'share/lilypond/*/tex',
            'share/lilypond/*/fonts/source',
# Keep svg fonts.  They are needed for usable/sharable svg output.
#                        'share/lilypond/*/fonts/svg',
            'share/lilypond/*/fonts/tfm',
            'share/lilypond/*/fonts/type1/feta[0-9]*pfa',
            'share/lilypond/*/fonts/type1/feta-braces-[a-z]*pfa',
            'share/lilypond/*/fonts/type1/parmesan*pfa',
            'share/locale',
            'share/omf',
            ## 2.6 installer: leave c059*
            'share/gs/fonts/[a-bd-z]*',
            'share/gs/fonts/c[^0][^5][^9]*',
            'share/gs/Resource',                        
            ):

            self.system ('cd %(installer_root)s && rm -rf ' + delete_me, {'i': i })
        self.system ('rm -f %(installer_root)s/usr/share/lilypond/*/fonts/*/fonts.cache-1')
        self.system ('fc-cache %(installer_root)s/usr/share/lilypond/*/fonts/*/')

    def strip_binary_file (self, file):
        self.system ('%(strip_command)s %(file)s', locals (), ignore_error = True)

    def strip_binary_dir (self, dir):
        if not os.path.isdir (dir % self.get_substitution_dict ()):
            raise ('warning: no such dir: '
               + dir % self.get_substitution_dict ())
        (root, dirs, files) = os.walk (dir % self.get_substitution_dict ()).next ()
        for f in files:
            if (os.path.basename (f) not in self.no_binary_strip
              and (os.path.splitext (f)[1]
                not in self.no_binary_strip_extensions)):
                self.strip_binary_file (root + '/' + f)

    def strip (self):
        self.strip_unnecessary_files ()
        self.strip_binary_dir ('%(installer_root)s/usr/lib')
        self.strip_binary_dir ('%(installer_root)s/usr/bin')

    def use_install_root_manager (self, manager):
        pass
    
    def create (self):
        pass
        
class Darwin_bundle (Installer):
    def __init__ (self, settings):
        Installer.__init__ (self, settings)
        self.strip_command += ' -S '
        self.darwin_bundle_dir = '%(targetdir)s/LilyPond.app'
        self.rewirer = darwintools.Rewirer (self.settings)
        
    def use_install_root_manager (self, package_manager):
        tarball = package_manager.package_dict ('darwin-sdk')['split_ball']
        self.package_manager = package_manager
        self.rewirer.set_ignore_libs_from_tarball (tarball)
        
    def create (self):
        Installer.create (self)
        
        osx_lilypad_version = self.package_manager.package_dict ('osx-lilypad')['version']
        
        self.rewirer.rewire_root (self.expand ('%(installer_root)s'))

        bundle_zip = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.%(platform)s.tar.bz2')
        self.system ('''
rm -f %(bundle_zip)s 
rm -rf %(darwin_bundle_dir)s
tar -C %(targetdir)s -zxf %(downloaddir)s/osx-lilypad-%(osx_lilypad_version)s.tar.gz
cp %(darwin_bundle_dir)s/Contents/Resources/subprocess.py %(installer_root)s/usr/share/lilypond/current/python/
cp -pR --link %(installer_root)s/usr/* %(darwin_bundle_dir)s/Contents/Resources/

''', locals ())
        self.file_sub (
            [('2.[0-9].[0-9]+-[0-9]',
             '%(installer_version)s-%(installer_build)s'),
            ('Build from .*',
             'Build from %s' % time.asctime()),
            ],
            '%(darwin_bundle_dir)s/Contents/Info.plist',
            env=locals (),
            must_succeed=True)
        
        self.system ('cd %(darwin_bundle_dir)s/../ && tar cjf %(bundle_zip)s LilyPond.app',
                     locals ())
        
        self.log_command ("Created %(bundle_zip)s\n", locals()) 
        
class Nsis (Installer):
    def __init__ (self, settings):
        Installer.__init__ (self, settings)
        self.strip_command += ' -g '
        self.no_binary_strip = ['gsdll32.dll', 'gsdll32.lib']

    def create (self):
        Installer.create (self)
        
        # FIXME: build in separate nsis dir, copy or use symlink
        installer = os.path.basename (self.expand ('%(installer_root)s'))
        
        self.file_sub ([                        
                        ('@LILYPOND_BUILD@', '%(installer_build)s'),
                        ('@LILYPOND_VERSION@', '%(installer_version)s'),

                        ## fixme:  JUNKME.
                        ('@ROOT@', '%(installer)s'),
                        ],
                       '%(nsisdir)s/lilypond.nsi.in',
                       #                               to_name='%(targetdir)s/lilypond.nsi',
                       to_name='%(targetdir)s/lilypond.nsi',
                       env=locals ())
        
        self.system ('cp %(nsisdir)s/*.nsh %(targetdir)s')
        self.system ('cp %(nsisdir)s/*.bat.in %(targetdir)s')
        self.system ('cp %(nsisdir)s/*.sh.in %(targetdir)s')
        self.system ('cd %(targetdir)s && makensis lilypond.nsi')

        final = 'lilypond-%(installer_version)s-%(installer_build)s.%(platform)s.exe'
        self.system ('mv %(targetdir)s/setup.exe %(installer_uploads)s/%(final)s', locals ())


class Linux_installer (Installer):
    def __init__ (self, settings):
        Installer.__init__ (self, settings)
        self.bundle_tarball = '%(targetdir)s/%(name)s-%(installer_version)s-%(installer_build)s.%(platform)s.tar.bz2'

    def strip_prefixes (self):
        return Installer.strip_prefixes (self)

    def create_tarball (self):
        self.system ('tar --owner=root --group=root -C %(installer_root)s -jcf %(bundle_tarball)s .', locals ())

def create_shar (orig_file, hello, head, target_shar):
    length = os.stat (orig_file)[6]

    tarflag = tar_compression_flag (orig_file)

    base_orig_file = os.path.split (orig_file)[1]
    script = open (head).read ()

    header_length = 0
    header_length = len (script % locals ()) + 1

    f = open (target_shar, 'w')
    f.write (script % locals())
    f.close ()

        
    cmd = 'cat %(orig_file)s >> %(target_shar)s' % locals ()
    print 'invoking ', cmd
    stat = os.system (cmd)
    if stat:
        raise 'create_shar() failed'
    os.chmod (target_shar, 0755)

class Shar (Linux_installer):
    def create (self):
        self.create_tarball ()
        
        target_shar = self.expand ('%(installer_uploads)s/%(name)s-%(installer_version)s-%(installer_build)s.%(platform)s.sh')

        head = self.expand ('%(sourcefiledir)s/sharhead.sh')
        tarball = self.expand (self.bundle_tarball)

        hello = self.expand ("version %(installer_version)s release %(installer_build)s")
        create_shar (tarball, hello, head, target_shar)
              
class Deb (Linux_installer):
    def create (self):
        self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(bundle_tarball)s', locals ())

class Rpm (Linux_installer):
    def create (self):
        self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(bundle_tarball)s', locals ())

class Cygwin_package (Installer):
    def __init__ (self, settings, name):
        # DUH
        #settings.set_distcc_hosts ({'cross_distcc_hosts': []})
        Installer.__init__ (self, settings)
        self.strip_command += ' -g '
        self._name = name
        settings.__dict__['cross_distcc_hosts'] = []
        settings.__dict__['native_distcc_hosts'] = []

    def use_install_root_manager (self, package_manager):
        self.package_manager = package_manager
        
    # FIXME: 'build-installer' is NOT create.  package-installer is create.
    # for Cygwin, build-installer is FOO (installs all dependencies),
    # and strip-installer comes too early.
    def create (self):
        p = targetpackage.load_target_package (self.settings,
                           self._name)
        self.cygwin_ball (p, '')
        for i in p.get_subpackage_names ():
            self.cygwin_ball (p, i)
        self.cygwin_src_ball (p)

    def cygwin_ball (self, package, split):
        cygwin_uploads = '%(gub_uploads)s/release'
        package_name = self._name
        if not split:
            # gub_name = package['split_ball']
            gub_name = self.package_manager.package_dict (package_name) ['split_ball']
        else:
            cygwin_uploads += '/' + self.name ()
            import inspect
            gub_name = self.package_manager.package_dict (package_name + '-' + split) ['split_ball']

        gub_name = re.sub ('.*/', '', gub_name)
        # FIXME: fixup broken split names
        package_prefixed_gub_name = gub_name
        gub_name = re.sub ('guile-libguile', 'libguile', gub_name)
        
        print 'gub_name: ' + gub_name

        base_name = re.sub ('-%\(version\)s.*', '', gub_name)
        ball_name = re.sub ('\.%\(platform\)s.*',
                  '-%(installer_build)s.tar.bz2',
                  gub_name)

        # FIXME: version and platform are expanded now?
        base_name = re.sub ('-[0-9].*', '', gub_name)
        ball_name = re.sub ('\.cygwin.*',
                  '-%(installer_build)s.tar.bz2',
                  gub_name)

        # URG urg urgurg
        b = self.settings.lilypond_branch
        # FIXME, package lilypond has gub_name='lilypond-<BRANCH>
        # but lilypond-doc has gub_name='%(name)s-doc-<BRANCH>'
        g = package.expand (gub_name)
        if (g.startswith ('lilypond-' + b)
          or g.startswith ('lilypond-doc-' + b)):
            base_name = re.sub ('-' + b +'.*', '', g)
            ball_name = re.sub ('-' + b + '.*',
                      '-%(installer_version)s-%(installer_build)s.tar.bz2',
                  g)
        hint = base_name + '.hint'
        # FIXME: sane package installer root
        self.installer_root = '%(targetdir)s/installer-%(base_name)s'

        dir = self.expand ('%(installer_root)s-' + base_name)
        installer_root = self.expand ('%(installer_root)s')
        package.system ('''
rm -rf %(dir)s
mkdir -p %(dir)s
tar -C %(dir)s -zxf %(gub_uploads)s/%(package_prefixed_gub_name)s
''',
                locals ())
        # FIXME: unconditional strip
        for i in ('bin', 'lib'):
            d = package.expand ('%(dir)s/usr/' + i, locals ())
            if os.path.isdir (d):
                self.strip_binary_dir (d)
        infodir = package.expand ('%(dir)s/usr/share/info', locals ())
        if os.path.isdir (infodir):
            package.system ('gzip %(infodir)s/*', locals ())
        package.system ('''
rm -rf %(dir)s/usr/cross
mkdir -p %(cygwin_uploads)s/%(base_name)s
tar -C %(dir)s --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(base_name)s/%(ball_name)s .
cp -pv %(installer_root)s-%(package_name)s/etc/hints/%(hint)s %(cygwin_uploads)s/%(base_name)s/setup.hint
''',
                locals ())

    def cygwin_src_ball (self, package):
        cygwin_uploads = '%(gub_uploads)s/release'
        package_name = self._name
        gub_name = self.package_manager.package_dict (package_name) ['split_ball']
        gub_name = re.sub ('.*/', '', gub_name)
        base_name = re.sub ('-%\(version\)s.*', '', gub_name)
        dir_name = re.sub ('\.%\(platform\)s.*', '', gub_name)

        # FIXME: version and platform are expanded now?
        base_name = re.sub ('-[0-9].*', '', gub_name)
        dir_name = re.sub ('\.cygwin.*', '', gub_name)
        cyg_name = dir_name + '-%(installer_build)s'

        # FIXME: sane package installer root
        self.installer_root = '%(targetdir)s/installer-%(base_name)s'

        # URG urg urgurg
        b = self.settings.lilypond_branch
        if gub_name.startswith ('lilypond-' + b):
            base_name = re.sub ('-' + b + '.*', '', gub_name)
            dir_name = re.sub ('.cygwin.gub', '', gub_name)
            cyg_name = re.sub ('-' + b + '.*',
                     '-%(installer_version)s-%(installer_build)s',
                     gub_name)
        ball_name = cyg_name + '-src.tar.bz2'
        dir = self.expand ('%(installer_root)s-src')
        package.system ('''
rm -rf %(dir)s
mkdir -p %(dir)s
tar -C %(dir)s -zxf %(gub_uploads)s/%(gub_name_src)s
mv %(dir)s/%(dir_name)s %(dir)s/%(cyg_name)s
mkdir -p %(cygwin_uploads)s/%(base_name)s
tar -C %(dir)s --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(base_name)s/%(ball_name)s %(cyg_name)s
''',
                locals ())

    def name (self):
        return self._name

    def strip (self):
        return
        self.strip_binary_dir ('%(installer_root)s/usr/lib')
        self.strip_binary_dir ('%(installer_root)s/usr/bin')
        self.system ('gzip %(installer_root)s/usr/share/info/*')

def get_installer (settings, args=[]):

    ## UGH : creating 6 instances of installer ?!
    installers = {
        'arm' : Shar (settings),
        'darwin-ppc' : Darwin_bundle (settings),
        'darwin-x86' : Darwin_bundle (settings),
        'freebsd' : Shar (settings),
        'linux' : Shar (settings),
        'mingw' : Nsis (settings),
        'mipsel' : Shar (settings),
    }

    if settings.platform == 'cygwin':
        ##
        ## FIXME: should have distinction between
        ##
        ## Installer_builder (platform specific, 1 per platform)
        ## and Installer_packager (nsis, shar; more per platform)
        ## 
        
        return Cygwin_package (settings, args[0])
        return None
        return map (lambda x:
                    Cygwin_package (settings, x), args)
    
    return installers[settings.platform]
