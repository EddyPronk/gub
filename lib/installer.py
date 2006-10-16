import os
import re
import time

import context
import darwintools
import gup
import targetpackage

from context import subst_method
from misc import *

def sort (lst):
    list.sort (lst)
    return lst

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
            'share/omf',
            ## 2.6 installer: leave c059*
            'share/gs/fonts/[a-bd-z]*',
            'share/gs/fonts/c[^0][^5][^9]*',
            'share/gs/Resource',                        
            ):

            self.system ('cd %(installer_root)s && rm -rf ' + delete_me, {'i': i })

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
        self.system ("mkdir %(installer_root)s/license/", ignore_error=True)
        self.system ("cp %(sourcefiledir)s/gub.license %(installer_root)s/license/README", ignore_error=True)
        
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
        
    def cygwin_patches_dir (self, spec):
        cygwin_patches = '%(srcdir)s/CYGWIN-PATCHES'
        # FIXME: how does this work?  Why do I sometimes need an
        # explicit expand?
        cygwin_patches = spec.expand (cygwin_patches)
        spec.system ('''
mkdir -p %(cygwin_patches)s
cp -pv %(installer_root)s/etc/hints/* %(cygwin_patches)s
cp -pv %(installer_root)s/usr/share/doc/%(name)s/README.Cygwin %(cygwin_patches)s || true
    ''',
                     self.get_substitution_dict (locals ()))

    def dump_hint (self, spec, split, base_name):
        # HUH?
        spec.system ('''
mkdir -p %(installer_root)s/etc/hints
''',
                     self.get_substitution_dict ())

        ### FIXME: this would require guile.py: def build_number ()
        ### like lilypond.py has
        ### Just use the overridden --buildnumber-file option.
        ###installer_build = spec.build_number ()
        installer_build = self.expand ('%(installer_build)s')

        # FIXME: lilypond is built from CVS, in which case version is lost
        # and overwritten by the CVS branch name.  Therefore, using
        # %(version)s in lilypond's hint file will not work.  Luckily, for
        # the lilypond package %(installer_version)s, is what we need.
        # Note that this breaks when building guile from cvs, eg.

        installer_version = spec.build_version ()

        # FIXME, this is the accidental build number of LILYPOND, which is
        # wrong to use for guile and other packages, but uh, individual
        # packages do not have a build number anymore...
        build = installer_build

        depends = spec.get_dependency_dict ()[split]
        distro_depends = []
        for dep in depends:
            import cygwin
            if dep in cygwin.gub_to_distro_dict.keys ():
                distro_depends += cygwin.gub_to_distro_dict[dep]
            else:
                distro_depends += [dep]

        requires = ' '.join (sort (distro_depends))
        print 'requires:' + requires
        external_source_line = ''
        file = (spec.settings.sourcefiledir + '/' + base_name + '.hint')
        if os.path.exists (file):
            hint = spec.expand (open (file).read (), locals ())
        else:
            if split:
                external_source_line = spec.expand ('''
external-source: %(name)s''',
                                                    locals ())
            requires_line = ''
            if requires:
                requires_line = spec.expand ('''
requires: %(requires)s''',
                                             locals ())
            hint = spec.expand ('''curr: %(installer_version)s-%(installer_build)s
sdesc: "%(name)s"
ldesc: "The %(name)s package for Cygwin."
category: misc%(requires_line)s%(external_source_line)s
''',
                                    locals ())
        spec.dump (hint,
                   '%(installer_root)s/etc/hints/%(base_name)s.hint',
                   env=self.get_substitution_dict (locals ()))

    def dump_readmes (self, spec):
        file = spec.expand (spec.settings.sourcefiledir
                            + '/%(name)s.changelog')
        if os.path.exists (file):
            changelog = open (file).read ()
        else:
            changelog = 'ChangeLog not recorded.'

        spec.system ('''
mkdir -p %(installer_root)s/usr/share/doc/Cygwin
mkdir -p %(installer_root)s/usr/share/doc/%(name)s
''',
                     self.get_substitution_dict (locals ()))

        ### FIXME: this would require guile.py: def build_number ()
        ### like lilypond.py has
        ### Just use the overridden --buildnumber-file option.
        ###installer_build = spec.build_number ()
        installer_build = self.expand ('%(installer_build)s')

        # FIXME: lilypond is built from CVS, in which case version is lost
        # and overwritten by the CVS branch name.  Therefore, using
        # %(version)s in lilypond's hint file will not work.  Luckily, for
        # the lilypond package %(installer_version)s, is what we need.
        # Note that this breaks when building guile from cvs, eg.

        installer_version = spec.build_version ()

        # FIXME, this is the accidental build number of LILYPOND, which is
        # wrong to use for guile and other packages, but uh, individual
        # packages do not have a build number anymore...
        build = installer_build

        file = spec.expand (spec.settings.sourcefiledir
                            + '/%(name)s.README', locals ())
        if os.path.exists (file):
            readme = spec.expand (open (file).read (), locals ())
        else:
            readme = spec.expand ('README for Cygwin %(name)s-%(installer_version)s-%(installer_build)s', locals ())

        spec.dump (readme,
                   '%(installer_root)s/usr/share/doc/Cygwin/%(name)s-%(installer_version)s-%(installer_build)s.README',
                   env=self.get_substitution_dict (locals ()))
        spec.dump (readme,
                   '%(installer_root)s/usr/share/doc/%(name)s/README.Cygwin',
                   env=self.get_substitution_dict (locals ()))

    # FIXME: 'build-installer' is NOT create.  package-installer is create.
    # for Cygwin, build-installer is FOO (installs all dependencies),
    # and strip-installer comes too early.
    def create (self):
        p = targetpackage.load_target_package (self.settings, self._name)
        for i in [''] + p.get_subpackage_names ():
            self.cygwin_ball (p, i)
        self.cygwin_src_ball (p)
        # FIXME: we used to have python code to generate a setup.ini
        # snippet from a package, in some package-manager class used
        # by gub and cyg-apt packaging...
        self.system ('''cd %(uploads)s/cygwin && %(downloads)s/genini $(find release -mindepth 1 -maxdepth 2 -type d) > setup.ini''')

    def get_dict (self, package, split):
        cygwin_uploads = '%(gub_uploads)s/release'
        package_name = self._name
        if not split:
            gub_ball = self.package_manager.package_dict (package_name) ['split_ball']
        else:
            cygwin_uploads += '/' + self.name ()
            import inspect
            gub_ball = self.package_manager.package_dict (package_name + '-' + split) ['split_ball']

        gub_name =  re.sub ('.*/', '', gub_ball)

	import misc
        branch = self.settings.lilypond_branch
        fixed_version_name = self.expand (re.sub ('-' + branch,
                                                  '-%(installer_version)s',
                                                  gub_name))
        t = misc.split_ball (fixed_version_name)
        print 'split: ' + `t`
        base_name = t[0]
        import cygwin
        if cygwin.gub_to_distro_dict.has_key (base_name):
            base_name = cygwin.gub_to_distro_dict[base_name][0]
        # strip last two dummy version entries: cygwin, 0
        # gub packages do not have a build number
        dir_name = base_name + '-' + '.'.join (map (misc.itoa, t[1][:-2]))
        cyg_name = dir_name + '-%(installer_build)s'
        # FIXME: not in case of -branch name
        dir_name = re.sub ('.cygwin.gu[pb]', '', gub_name)
        hint = base_name + '.hint'

        # FIXME: sane package installer root
        installer_root =  '%(targetdir)s/installer-%(base_name)s'
        self.get_substitution_dict ()['installer_root'] = installer_root
        self.get_substitution_dict ()['base_name'] = base_name

        infodir = '%(installer_root)s/usr/share/info' % locals ()

        # FIXME: Where does installer_root live?
        self.installer_root = installer_root
        self.base_name = base_name
        self.get_substitution_dict ()['installer_root'] = self.expand (installer_root, locals ())
        package.get_substitution_dict ()['installer_root'] = installer_root
        package.get_substitution_dict ()['base_name'] = base_name
        return locals ()
    
    def cygwin_ball (self, package, split):
        d = self.get_dict (package, split)
        base_name = d['base_name']
        ball_name =  d['cyg_name'] + '.tar.bz2'
        hint = d['hint']
        infodir = d['infodir'] 
        package_name = d['package_name']

        d['ball_name'] = ball_name
        package.system ('''
rm -rf %(installer_root)s
mkdir -p %(installer_root)s
tar -C %(installer_root)s -zxf %(gub_uploads)s/%(gub_name)s
''',
                self.get_substitution_dict (d))
        
        self.dump_hint (package, split, base_name)

        if not split:
            self.dump_readmes (package)
        self.cygwin_patches_dir (package)

        # FIXME: unconditional strip
        for i in ('bin', 'lib'):
            dir = package.expand ('%(installer_root)s/usr/' + i,
                                  self.get_substitution_dict (d))
            if os.path.isdir (dir):
                self.strip_binary_dir (dir)

        if os.path.isdir (infodir):
            package.system ('gzip %(infodir)s/*',
                            self.get_substitution_dict (d))
        if os.path.isdir (infodir + '/' + package_name):
            package.system ('gzip %(infodir)s/%(package_name)s/*',
                            self.get_substitution_dict (d))

        package.system ('''
rm -rf %(installer_root)s/usr/cross
mkdir -p %(cygwin_uploads)s/%(base_name)s
tar -C %(installer_root)s --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(base_name)s/%(ball_name)s .
cp -pv %(installer_root)s/etc/hints/%(hint)s %(cygwin_uploads)s/%(base_name)s/setup.hint
''',
                self.get_substitution_dict (d))

    def cygwin_src_ball (self, package):
        d = self.get_dict (package, '')
        ball_name =  d['cyg_name'] + '-src.tar.bz2'
        dir = self.expand ('%(installer_root)s-src')

        d['ball_name'] = ball_name
        d['dir'] = dir
        package.system ('''
rm -rf %(dir)s
mkdir -p %(dir)s
tar -C %(dir)s -zxf %(gub_uploads)s/%(gub_name_src)s
mv %(dir)s/%(dir_name)s %(dir)s/%(cyg_name)s
mkdir -p %(cygwin_uploads)s/%(base_name)s
tar -C %(dir)s --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(base_name)s/%(ball_name)s %(cyg_name)s
''',
                        self.get_substitution_dict (d))

    def name (self):
        return self._name

    def strip (self):
        return
        self.strip_binary_dir ('%(installer_root)s/usr/lib')
        self.strip_binary_dir ('%(installer_root)s/usr/bin')
        self.system ('gzip %(installer_root)s/usr/share/info/*')

def get_installer (settings, args=[]):

    installer_class = {
        'arm' : Shar,
        'darwin-ppc' : Darwin_bundle,
        'darwin-x86' : Darwin_bundle,
        'freebsd-x86' : Shar,
        'linux-x86' : Shar,
        'linux-64' : Shar,
        'mingw' : Nsis,
        'mipsel' : Shar,
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
    
    return installer_class[settings.platform] (settings)
