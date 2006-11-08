#! /usr/bin/python

import optparse
import os
import sys

sys.path.insert (0, 'lib/')

import context
import gup
import settings as settings_mod
import misc
import cygwin

class Cygwin_package (context.Os_context_wrapper):
    def __init__ (self, settings, name, branch):
        context.Os_context_wrapper.__init__ (self, settings)
        self.settings = settings
        self._name = name

        # FIXME: c&p
        self.strip_command \
            = '%(cross_prefix)s/bin/%(target_architecture)s-strip' 
        self.no_binary_strip = []
        self.no_binary_strip_extensions = ['.la', '.py', '.def',
                                           '.scm', '.pyc']

        self.installer_root = settings.expand ('%(targetdir)s/installer-' + name) 
        self.installer_db = settings.expand ('%(targetdir)s/installer-' + name + '-dbdir')
        self.installer_uploads = settings.uploads
        self.cygwin_uploads = settings.expand ('%(gub_uploads)s/release')

        self.package_manager = gup.DependencyManager (
            self.installer_root,
            settings.os_interface,
            dbdir=self.installer_db,
            clean=True)

        self.package_manager.include_build_deps = False
        self.package_manager.read_package_headers (
            settings.expand ('%(gub_uploads)s/'  + name), branch)

        p = self.package_manager.get_all_packages ()[0]
        if not self.settings.build:
            self.settings.build = self.build_number (p)
        self.create ()

    def build_number (self, package):
        import versiondb
        version_file = '%(uploads)s/%(name)s.versions' % package
        db = versiondb.VersionDataBase (version_file)
        version = '%(full_version)s' % package
        v = tuple (map (int, version.split ('.')))
        b = db.get_next_build_number (v)
        return ('%d' % b)

    def create (self):
        packs = self.package_manager.get_all_packages ()
        for package in packs:
            self.re_ball (package)
        self.re_src_ball ()

        # FIXME: we used to have python code to generate a setup.ini
        # snippet from a package, in some package-manager class used
        # by gub and cyg-apt packaging...
        self.system ('''cd %(uploads)s/cygwin && %(downloads)s/genini $(find release -mindepth 1 -maxdepth 2 -type d) > setup.ini''')

    def re_ball (self, hdr):
        cyg_split = cygwin.gub_to_distro_dict.get (hdr['split_name'],
                                                   [hdr['split_name']])[0]
        main_p = hdr['name'] == hdr['split_name']
        subdir = ''
        if not main_p:
            subdir = '/' + cyg_split

        subload = self.expand ('%(cygwin_uploads)s/%(name)s%(subdir)s', locals ())
        ball = self.expand ('%(subload)s/%(cyg_split)s-%(version)s-%(build)s.tar.bz2', locals ())

        self._untar ('%(installer_root)s', '%(split_ball)s' % hdr)
        self.dump_hint (hdr, self.expand ('%(installer_root)s/etc/hints/%(cyg_split)s.hint', locals ()))
        self.dump_readmes (hdr)
        self._CYGWIN_PATCHES_dir ()
        self.remove_cruft ()
        self.binary_strip ()
        self.infodir ()
        self._tar ('%(installer_root)s', ball, '*', locals ())
        self.dump_hint (hdr, '%(subload)s/setup.hint' % locals ())

    def re_src_ball (self):
        dir = self.expand ('%(installer_root)s-src')
        cyg_dir = self.expand ('%(name)s-%(version)s-%(build)s', locals ())
        gub_dir = self.expand ('%(name)s%(ball_suffix)s')
        cyg_ball = cyg_dir + '-src.tar.bz2'
        ball = (self.expand ('%(cygwin_uploads)s/%(name)s/') + '%(cyg_ball)s'
                % locals ())

        #self._untar (dir, '%(src_package_ball)s')
        self._untar (dir, self.expand ('%(src_package_ball)s'))
        self._mv ('%(dir)s/%(gub_dir)s', '%(dir)s/%(cyg_dir)s', locals ())
        self._tar (dir, ball, cyg_dir)

    def get_substitution_dict (self, env={}):

        env = env.copy ()
        env.update (self.package_manager.get_all_packages ()[0])
        
        d = context.Os_context_wrapper.get_substitution_dict (self, env=env)
        return d
    
    @context.subst_method
    def name (self):
        return self._name
    
    @context.subst_method
    def build (self):
        return self.settings.build

    def _CYGWIN_PATCHES_dir (self):
        cygwin_patches = self.expand ('%(srcdir)s/CYGWIN-PATCHES')
        self.system ('''
mkdir -p %(cygwin_patches)s
cp -pv %(installer_root)s/etc/hints/* %(cygwin_patches)s
cp -pv %(installer_root)s/usr/share/doc/%(name)s/README.Cygwin %(cygwin_patches)s || true
    ''', locals ())

    def description (self, hdr):
        desc = hdr['description']
        short = ''
        if not desc:
            ## do something
            #short = ldesc[:ldesc.find ('\n')]
            pass
        else:
            short = desc.split ('\n')[0]

        return (short, desc)

    def get_readme (self, hdr):
        file = self.expand ('%(sourcefiledir)s/%(name)s.changelog')
        if os.path.exists (file):
            changelog = open (file).read ()
        else:
            changelog = 'ChangeLog not recorded.'

        self.system ('''
mkdir -p %(installer_root)s/usr/share/doc/Cygwin
mkdir -p %(installer_root)s/usr/share/doc/%(name)s
''')

        file = self.expand ('%(sourcefiledir)s/%(name)s.README')
        if os.path.exists (file):
            readme = self.expand (open (file).read (), locals ())
        else:
            readme = 'README for Cygwin %(name)s-%(version)s-%(build)s'
        readme = self.expand (readme, hdr)
        return readme

    def strip_dir (self, dir):
        import misc
        misc.map_command_dir (self.expand (dir),
                              self.expand ('%(strip_command)s'),
                              self.no_binary_strip,
                              self.no_binary_strip_extensions)

    def get_hint (self, hdr):
        dependencies = [cygwin.gub_to_distro_dict.get (d, [d])
                        for d in hdr['dependencies_string'].split (';')]
        dependencies = sorted (reduce (lambda x,y: x+y, dependencies))
        dependencies_str = ' '.join (dependencies)
        
        (sdesc, ldesc) = self.description (hdr)

        requires_line = ''
        if dependencies_str:
            requires_line = '''
requires: %(dependencies_str)s''' % locals ()

        external_source_line = ''
        main_p = hdr['name'] == hdr['split_name']
        if not main_p:
            external_source_line = self.expand ('''
external-source: %(name)s''')

        if not sdesc:
            sdesc = self.expand ('%(name)s')
            if not main_p:
                sdesc += ' ' + hdr['sub_name']

        if not ldesc:
            flavor = 'executables'
            if not main_p:
                flavor = hdr['sub_name']
            ldesc = 'The %(name)s package for Cygwin - ' + flavor

        category = hdr['category']
        if not category:
            if main_p:
                category = 'utils'
            elif hdr['sub_name'] == 'runtime':
                category = 'libs'
            else:
                category = hdr['sub_name']

        local_category = category
        hint = self.expand ('''sdesc: "%(sdesc)s"
ldesc: "%(ldesc)s"
category: %(local_category)s%(requires_line)s%(external_source_line)s
''', locals ())
        return hint

    def _untar (self, dir, ball, env={}):
        e = env.copy ()
        e.update (locals ())
        self.system ('''
rm -rf %(dir)s
mkdir -p %(dir)s
tar -C %(dir)s -zxf %(ball)s''', e)

    def _tar (self, dir, ball, content, env={}):
        ball_dir = os.path.dirname (ball)
        e = env.copy ()
        e.update (locals ())
        self.system ('''
mkdir -p %(ball_dir)s
cd %(dir)s && tar --owner=0 --group=0 -jcf %(ball)s %(content)s
''', e)

    def _mv (self, src, dst, env={}):
        e = env.copy ()
        e.update (locals ())
        self.system ('mv %(src)s %(dst)s', e)

    def remove_cruft (self):
        self.system ('''
find %(installer_root)s -name fonts.cache-1 -exec rm '{}' ';'
rm -rf %(installer_root)s/etc/hints
rm -rf %(installer_root)s/license*
rm -rf %(installer_root)s/usr/cross
rm -rf %(installer_root)s/usr/etc/relocate
rmdir %(installer_root)s/bin || true
rmdir %(installer_root)s/etc/postinstall || true
rmdir %(installer_root)s/etc || true
rmdir %(installer_root)s/usr/bin || true
rmdir %(installer_root)s/usr/etc || true
rmdir %(installer_root)s/usr/lib || true
rmdir %(installer_root)s/usr/share/doc/%(name)s || true
rmdir %(installer_root)s/usr/share/doc || true
rmdir %(installer_root)s/usr/share || true
rmdir %(installer_root)s/usr || true
''')

    def binary_strip (self):
        for i in ('bin', 'lib'):
            dir = self.expand ('%(installer_root)s/usr/%(i)s', locals ())
            if os.path.isdir (dir):
                self.strip_dir (dir)

    def dump_hint (self, hdr, name):
        hint = self.get_hint (hdr)
        self.dump (hint, name, env=locals ())

    def dump_readmes (self, hdr):
        main_p = hdr['name'] == hdr['split_name']
        if main_p:
            readme = self.get_readme (hdr)
            self.dump (readme,
                       '%(installer_root)s/usr/share/doc/Cygwin/%(name)s-%(version)s-%(build)s.README')
            self.dump (readme,
                       '%(installer_root)s/usr/share/doc/%(name)s/README.Cygwin')

    def infodir (self):
        infodir = self.expand ('%(installer_root)s/usr/share/info')
        if os.path.isdir (infodir + '/' + self._name):
            self.system ('gzip %(infodir)s/%(name)s/*.info*', locals ())
        elif os.path.isdir (infodir):
            self.system ('gzip %(infodir)s/*.info*', locals ())

def parse_command_line ():
    p = optparse.OptionParser ()
    p.description = 'Grand Unified Builder - create cygwin packages.'
    p.usage = 'cygwin-packager.py [OPTION]... PACKAGE'
    p.add_option ('-b', '--build-number',
                  action='store', default=None, dest='build')

    p.add_option ('--branch',
                  action='store', dest='branch',
                  default="HEAD")
    (options, args) = p.parse_args ()
    if len (args) != 1:
        p.print_help ()
        sys.exit (2)
    return (options, args)

def main ():
    (options, commands)  = parse_command_line ()
    platform = 'cygwin'
    settings = settings_mod.get_settings (platform)
    # We want to be able to specify a build number for cygwin packages
    # that are not distributed on lp.org
    settings.build = options.build

    # Barf
    settings.__dict__['cross_distcc_hosts'] = []
    settings.__dict__['native_distcc_hosts'] = []

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(local_prefix)s/bin:' + PATH)

    Cygwin_package (settings, commands[0], options.branch)
    
if __name__ == '__main__':
    main ()
