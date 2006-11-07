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
        self.strip_command \
            = '%(cross_prefix)s/bin/%(target_architecture)s-strip' 
        self.no_binary_strip = []
        self.no_binary_strip_extensions = ['.la', '.py', '.def', '.scm', '.pyc']

        self.installer_root = settings.targetdir + '/installer-%s' % settings.lilypond_branch
        self.installer_db = self.installer_root + '-dbdir'
        self.installer_uploads = settings.uploads
        self.installer_version = None
        self.installer_build = None
        self.checksum = '0000'
        
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
            'share/omf',
            ## 2.6 installer: leave c059*
            'share/gs/fonts/[a-bd-z]*',
            'share/gs/fonts/c[^0][^5][^9]*',
            'share/gs/Resource',                        
            ):

            self.system ('cd %(installer_root)s && rm -rf ' + delete_me, {'i': i })

    def strip_dir (self, dir):
        import misc
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
        self.system ("mkdir %(installer_root)s/license/", ignore_errors=True)
        self.system ("cp %(sourcefiledir)s/gub.license %(installer_root)s/license/README", ignore_errors=True)

    def write_checksum (self):
        open (self.expand ('%(installer_root)s.checksum'), 'w').write (self.checksum)


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
        installer_version = self.settings.installer_version
        installer_build = self.settings.installer_build
        
        bundle_zip = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.%(platform)s.tar.bz2', locals ())
        self.system ('''
rm -f %(bundle_zip)s 
rm -rf %(darwin_bundle_dir)s
tar -C %(targetdir)s -zxf %(downloads)s/osx-lilypad-%(osx_lilypad_version)s.tar.gz
cp %(darwin_bundle_dir)s/Contents/Resources/subprocess.py %(installer_root)s/usr/share/lilypond/current/python/
cp -pR --link %(installer_root)s/usr/* %(darwin_bundle_dir)s/Contents/Resources/
mkdir -p %(darwin_bundle_dir)s/Contents/Resources/license/
cp -pR --link %(installer_root)s/license*/* %(darwin_bundle_dir)s/Contents/Resources/license/
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
        self.write_checksum ()
        
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

        root = self.expand ('%(installer_root)s')
        files = [re.sub (root, '', f).replace ('/', '\\')
                 for f in self.locate_files (root, '*')]

        self.dump ('\r\n'.join (files) + '\r\n',
                   '%(installer_root)s/files.txt',
                   expand_string=False)

        PATH = os.environ['PATH']
        os.environ['PATH'] = self.expand ('%(local_prefix)s/bin:' + PATH)


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
        self.system ('tar --owner=0 --group=0 -C %(installer_root)s -jcf %(bundle_tarball)s .', locals ())
        
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
        self.create_tarball ()
        
        target_shar = self.expand ('%(installer_uploads)s/%(name)s-%(installer_version)s-%(installer_build)s.%(platform)s.sh')

        head = self.expand ('%(sourcefiledir)s/sharhead.sh')
        tarball = self.expand (self.bundle_tarball)

        hello = self.expand ("version %(installer_version)s release %(installer_build)s")
        create_shar (tarball, hello, head, target_shar)
        self.write_checksum ()
        
class Deb (Linux_installer):
    def create (self):
        self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(bundle_tarball)s', locals ())

class Rpm (Linux_installer):
    def create (self):
        self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(bundle_tarball)s', locals ())


def get_installer (settings, args=[]):

    installer_class = {
        'arm' : Shar,
        'darwin-ppc' : Darwin_bundle,
        'darwin-x86' : Darwin_bundle,
        'freebsd-x86' : Shar,
        'freebsd4-x86' : Shar,
        'freebsd6-x86' : Shar,
        'linux-x86' : Shar,
        'linux-64' : Shar,
        'mingw' : Nsis,
        'mipsel' : Shar,
    }

    return installer_class[settings.platform] (settings)
