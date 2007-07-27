import os
import re
import time

from gub import context
from gub import darwin
from gub import gup
from gub import targetpackage

from context import subst_method
from misc import *

# UGH -  we don't have the package dicts yet.
# barf, this should be in config file, not in code
pretty_names = {
    'lilypond': 'LilyPond',
    'git': 'Git',
    }

class Installer (context.Os_context_wrapper):
    def __init__ (self, settings, name):
        context.Os_context_wrapper.__init__ (self, settings)
        
        self.settings = settings
        self.strip_command \
            = '%(cross_prefix)s/bin/%(target_architecture)s-strip' 
        self.no_binary_strip = []
        self.no_binary_strip_extensions = ['.la', '.py', '.def', '.scm', '.pyc']
        self.installer_uploads = settings.uploads
        self.checksum = '0000'

        self.name = name
        self.pretty_name = pretty_names.get (name, name)
        self.package_branch = settings.branch_dict[name]
        self.installer_root = (settings.targetdir
                               + '/installer-%s-%s' % (name,
                                                       self.package_branch))
        self.installer_checksum_file = self.installer_root + '.checksum'
        self.installer_db = self.installer_root + '-dbdir'


    def building_root_image (self):
        # FIXME: why are we removing these, we need these in a root image.
        # How to make a better check here?
        return (self.expand ('%(name)s').startswith ('root-image')
                or self.expand ('%(name)s').startswith ('phone'))

    @context.subst_method
    def version (self):
        return self.settings.installer_version

    def strip_prefixes (self):
        return ['', 'usr/']
        
    def strip_unnecessary_files (self):
        "Remove unnecessary cruft."

        globs = [
            'bin/autopoint',
            'bin/glib-mkenums',
            'bin/guile-*',
            'bin/*-config',
            'bin/*gettext*',
            'bin/gs??',
            'bin/gsdj500',
            'bin/dbftops',
            'bin/dvipdf',
            'bin/pf2afm',
            'bin/printafm',
            'bin/pv.sh',
            'bin/unix-lpr.sh',
            'bin/wftopfa',
            'bin/idle',
            'bin/font2c',
            'bin/fixmswrd.pl',
            'bin/dumphint',
            
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
            'share/omf',
            ## 2.6 installer: leave c059*
            'share/gs/fonts/[a-bd-z]*',
            'share/gs/fonts/c[^0][^5][^9]*',
            'share/gs/Resource',                        
# Urg: prune qt fonts, keep helvetica, fontdir
            'lib/fonts/[^hf]*',
            'share/mkspecs',
            'share/terminfo',
            ]

        # FIXME: why are we removing these, we need these in a root image.
        # How to make a better check here?
        if not self.building_root_image ():
            globs += [
            'lib/libc.*',
            'lib/libm.*',
            ]

        delete_me = ''
        for p in self.strip_prefixes ():
            delete_me += p + '%(i)s '

        for i in globs:
            # [^..] dash globbing is broken, {,} globbing is bashism
            self.system ("cd %(installer_root)s && bash -c 'rm -rf " + delete_me + "'", {'i': i }, locals ())

    def strip_dir (self, dir):
        from gub import misc
        misc.map_command_dir (self.expand (dir),
                              self.expand ('%(strip_command)s'),
                              self.no_binary_strip,
                              self.no_binary_strip_extensions)
        
    def strip (self):
        self.strip_unnecessary_files ()
        self.strip_dir ('%(installer_root)s/usr/bin')
        self.strip_dir ('%(installer_root)s/usr/lib')

    def use_install_root_manager (self, manager):
        pass
    
    def create (self):
        self.system ('mkdir %(installer_root)s/license', ignore_errors=True)
        self.system ('cp %(sourcefiledir)s/gub.license %(installer_root)s/license/README', ignore_errors=True)

    def write_checksum (self):
        open (self.expand ('%(installer_checksum_file)s'), 'w').write (self.checksum)


class DarwinRoot (Installer):
    def __init__ (self, settings):
        Installer.__init__ (self, settings)
        self.strip_command += ' -S '
        self.rewirer = darwin.Rewirer (self.settings)

    def use_install_root_manager (self, package_manager):
        tarball = package_manager.package_dict ('darwin-sdk')['split_ball']
        self.package_manager = package_manager
        self.rewirer.set_ignore_libs_from_tarball (tarball)

    def create (self):
        Installer.create (self)
        self.rewirer.rewire_root (self.expand ('%(installer_root)s'))
        
    
class DarwinBundle (DarwinRoot):
    def __init__ (self, settings):
        DarwinRoot.__init__ (self, settings)
        self.darwin_bundle_dir = '%(targetdir)s/LilyPond.app'
        
    def create (self):
        DarwinRoot.create (self)
        
        osx_lilypad_version = self.package_manager.package_dict ('osx-lilypad')['version']

        ## cpu_type = self.expand ('%(platform)s').replace ('darwin-', '')
        cpu_type = 'ppc'
        installer_version = self.settings.installer_version
        installer_build = self.settings.installer_build
        
        bundle_zip = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.%(platform)s.tar.bz2', locals ())
        self.system ('''
rm -f %(bundle_zip)s 
rm -rf %(darwin_bundle_dir)s
tar -C %(targetdir)s -zxf %(downloads)s/osx-lilypad-%(cpu_type)s-%(osx_lilypad_version)s.tar.gz
cp %(darwin_bundle_dir)s/Contents/Resources/subprocess.py %(installer_root)s/usr/share/lilypond/current/python/
cp -pR --link %(installer_root)s/usr/* %(darwin_bundle_dir)s/Contents/Resources/
mkdir -p %(darwin_bundle_dir)s/Contents/Resources/license/
cp -pR --link %(installer_root)s/license*/* %(darwin_bundle_dir)s/Contents/Resources/license/
''', locals ())
        self.file_sub (
            [('2.[0-9]+.[0-9]+-[0-9]',
             '%(installer_version)s-%(installer_build)s'),
            ('Build from .*',
             'Build from %s' % time.asctime()),
            ],
            '%(darwin_bundle_dir)s/Contents/Info.plist',
            env=locals (),
            must_succeed=True)

        majmin = '.'.join (installer_version.split ('.')[:2])
        self.file_sub (
            [('doc/v2.6/',
             'doc/v%(majmin)s/'),
            ],
            '%(darwin_bundle_dir)s/Contents/Resources/Credits.html',
            env=locals (),
            must_succeed=True)
        
        self.file_sub (
            [('2.6.0', installer_version),
            ],
            '%(darwin_bundle_dir)s/Contents/Resources/Welcome-to-LilyPond-MacOS.ly',
            env=locals ())
        
        self.system ('cd %(darwin_bundle_dir)s/../ && tar cjf %(bundle_zip)s LilyPond.app',
                     locals ())
        
        self.write_checksum ()
        
class MingwRoot (Installer):
    def __init__ (self, settings):
        Installer.__init__ (self, settings)
        self.strip_command += ' -g '
    
class Nsis (MingwRoot):
    def create (self):
        MingwRoot.create (self)
        
        # FIXME: build in separate nsis dir, copy or use symlink
        installer = os.path.basename (self.expand ('%(installer_root)s'))
        ns_dir = self.expand ('%(installer_db)s')

        self.dump (r'''
!define INSTALLER_VERSION "%(installer_version)s"
!define INSTALLER_BUILD "%(installer_build)s"
!define INSTALLER_OUTPUT_DIR "%(ns_dir)s"
!define ROOT "%(installer)s"
!define PRETTY_NAME "%(pretty_name)s"
!define CANARY_EXE "%(name)s"
!define NAME "%(name)s"

!addincludedir "${INSTALLER_OUTPUT_DIR}"
OutFile "${INSTALLER_OUTPUT_DIR}/setup.exe"
''',
                   '%(ns_dir)s/definitions.nsh',
                   env=locals ())
        
        self.system (r'''cp %(nsisdir)s/*.nsh %(ns_dir)s
cp %(nsisdir)s/*.nsi %(ns_dir)s
cp %(nsisdir)s/*.sh.in %(ns_dir)s''', locals ())

        root = self.expand ('%(installer_root)s')
        files = [f.replace (root, '').replace ('/', '\\')
                 for f in self.locate_files (root, '*')]

        self.dump ('\r\n'.join (files) + '\r\n',
                   '%(installer_root)s/files.txt',
                   expand_string=False)

        PATH = os.environ['PATH']
        PATH = '%(local_prefix)s/bin:' + PATH
        
        self.system ('cd %(targetdir)s && makensis -NOCD %(ns_dir)s/definitions.nsh %(ns_dir)s/%(name)s.nsi', locals ())

        final = '%(name)s-%(installer_version)s-%(installer_build)s.%(platform)s.exe'
        self.system ('mv %(ns_dir)s/setup.exe %(installer_uploads)s/%(final)s', locals ())


class Linux_installer (Installer):
    def __init__ (self, settings, name):
        Installer.__init__ (self, settings, name)
        self.settings.fakeroot_cache = ('%(installer_root)s/fakeroot.save'
                                        % self.__dict__)
        if self.building_root_image ():
            self.fakeroot (self.settings.fakeroot % self.settings.__dict__)
        self.bundle_tarball = '%(installer_uploads)s/%(name)s-%(installer_version)s-%(installer_build)s.%(platform)s.tar.bz2'

    def strip_prefixes (self):
        return Installer.strip_prefixes (self)

    def create_tarball (self, bundle_tarball):
        self.system ('tar --owner=0 --group=0 -C %(installer_root)s -jcf %(bundle_tarball)s .', locals ())

    def create (self):
        Installer.create (self)
        self.create_tarball (self.bundle_tarball)
        self.write_checksum ()

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
        Linux_installer.create (self)
        target_shar = self.expand ('%(installer_uploads)s/%(name)s-%(installer_version)s-%(installer_build)s.%(platform)s.sh')
        head = self.expand ('%(sourcefiledir)s/sharhead.sh')
        tarball = self.expand (self.bundle_tarball)
        hello = self.expand ("version %(installer_version)s release %(installer_build)s")
        create_shar (tarball, hello, head, target_shar)
        system ('rm %(tarball)s' % locals ())
        
def get_installer (settings, name):

    installer_class = {
        # TODO: ipkg/dpkg
        'debian' : Shar,
        'debian-arm' : Shar,
        'debian-mipsel' : Shar,
        
        'darwin-ppc' : DarwinBundle,
        'darwin-x86' : DarwinBundle,
        'freebsd-x86' : Shar,
        'freebsd4-x86' : Shar,
        'freebsd6-x86' : Shar,
        'freebsd-64' : Shar,
        'linux-arm-softfloat' : Shar,
        'linux-arm-vfp' : Linux_installer,
        'linux-x86' : Shar,
        'linux-64' : Shar,
        'linux-ppc' : Shar,
        'mingw' : Nsis,
#        'mingw' : MingwRoot,
    }

    installer = installer_class[settings.platform] (settings, name)
    return installer
