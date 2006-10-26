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
    def __init__ (self, settings, name):
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

        self.package_manager = gup.DependencyManager (
            self.installer_root,
            settings.os_interface,
            dbdir=self.installer_db,
            clean=True)

        self.package_manager.include_build_deps = False
        self.package_manager.read_package_headers (
            settings.expand ('%(gub_uploads)s/'  + name), 'HEAD')

        self.create ()

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

    def cygwin_patches_dir (self):
        cygwin_patches = self.package.expand ('%(srcdir)s/CYGWIN-PATCHES')
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

    def dump_hint (self, split, base_name):
        self.system ('mkdir -p %(installer_root)s/etc/hints')

        depends = self.package.get_dependency_dict ()[split]
        distro_depends = []
        for dep in depends:
            import cygwin
            if dep in cygwin.gub_to_distro_dict.keys ():
                distro_depends += cygwin.gub_to_distro_dict[dep]
            else:
                distro_depends += [dep]

        requires = ' '.join (sorted (distro_depends))
        print 'requires:' + requires
        external_source_line = ''
        file = self.expand ('%(sourcefiledir)s/%(base_name)s.hint',
                            locals ())
        if split:
            external_source_line = self.expand ('''
external-source: %(name)s''')
        try:
            ldesc = self.package.description_dict ()[split]
            sdesc = ldesc[:ldesc.find ('\n')]
        except:
            sdesc = self.expand ('%(name)s')
            flavor = 'executables'
            if split:
                sdesc += ' ' + split
                flavor = split
            ldesc = 'The %(name)s package for Cygwin - ' + flavor
        try:
            category = self.package.category_dict ()[split]
        except:
            if not split:
                caterory = 'utils'
            elif split == 'runtime':
                caterory = 'libs'
            else:
                caterory = split
        requires_line = ''
        if requires:
            requires_line = self.expand ('''
requires: %(requires)s''', locals ())
        hint = self.expand ('''sdesc: "%(sdesc)s"
ldesc: "%(ldesc)s"
category: %(category)s%(requires_line)s%(external_source_line)s
''', locals ())
        print 'dumping hint for: ' + split
        self.dump (hint,
                   '%(installer_root)s/etc/hints/%(base_name)s.hint',
                   env=locals ())

    def dump_readmes (self):
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
            readme = open (file).read ()
        else:
            readme = 'README for Cygwin %(name)s-%(version)s-%(build)s'
        readme = self.package.expand (readme, locals ()) # so_version

        self.dump (readme,
                   '%(installer_root)s/usr/share/doc/Cygwin/%(name)s-%(version)s-%(build)s.README')
        self.dump (readme,
                   '%(installer_root)s/usr/share/doc/%(name)s/README.Cygwin')



    def create (self):
        packs =  self.package_manager.get_all_packages ()
        for package in packs:
            self.cygwin_new_ball (package)

        self.cygwin_src_ball ()

        # FIXME: we used to have python code to generate a setup.ini
        # snippet from a package, in some package-manager class used
        # by gub and cyg-apt packaging...
        self.system ('''cd %(uploads)s/cygwin && %(downloads)s/genini $(find release -mindepth 1 -maxdepth 2 -type d) > setup.ini''')

    def strip_dir (self, dir):
        import misc
        misc.map_command_dir (self.expand (dir),
                              self.expand ('%(strip_command)s)'),
                              self.no_binary_strip,
                              self.no_binary_strip_extensions)

    def cygwin_new_ball (self, hdr):

        self.system ('''
rm -rf %(installer_root)s
mkdir -p %(installer_root)s
tar -C %(installer_root)s -zxf %(split_ball)s''', hdr)


        dependencies = [cygwin.gub_to_distro_dict.get (d, [d])
                        for d in hdr['dependencies_string'].split (';')]
        dependencies = sorted (reduce (lambda x,y: x+y, dependencies))
        dependencies_str = ' '.join (dependencies)
        
        (ldesc, sdesc) = self.description (hdr)
        hint = self.expand ('''
sdesc: "%(sdesc)s"
%(version)s-%(build)s
ldesc: "%(ldesc)s"
category: %(category)s
requires: %(dependencies_str)s
external_source: FIXME
''', locals ())
        print hint
        
    def cygwin_ball (self, hdr):
        split  = hdr['split_name']

        d = self.get_dict (split)
        base_name = d['base_name']
        ball_name = d['cyg_name'] + '.tar.bz2'
        hint = d['hint']
        package_name = d['package_name']

        d['ball_name'] = ball_name
        self.system ('''
rm -rf %(installer_root)s
mkdir -p %(installer_root)s
tar -C %(installer_root)s -zxf %(gub_uploads)s/%(gub_name)s
''', self.package.get_substitution_dict (d))
        
        self.dump_hint (split, base_name)

        if not split:
            self.dump_readmes ()
        self.cygwin_patches_dir ()

        # FIXME: unconditional strip
        for i in ('bin', 'lib'):
            dir = self.package.expand ('%(installer_root)s/usr/' + i,
                                  self.get_substitution_dict (d))
            if os.path.isdir (dir):
                self.strip_dir (dir)

        infodir = self.expand ('%(installer_root)s/usr/share/info')
        if os.path.isdir (infodir + '/' + package_name):
            self.package.system ('gzip %(infodir)s/%(package_name)s/*.info*',
                            locals ())

        elif os.path.isdir (infodir):
            self.package.system ('gzip %(infodir)s/*.info*', locals ())
        self.package.system ('''
rm -rf %(installer_root)s/usr/cross
mkdir -p %(cygwin_uploads)s/%(base_name)s
mkdir -p %(installer_root)s/usr/share/doc/%(base_name)s
rm -rf %(installer_root)s/license*
rmdir %(installer_root)s/bin || true
rmdir %(installer_root)s/etc || true
rmdir %(installer_root)s/usr/bin || true
rm -rf %(installer_root)s/usr/etc/relocate
rmdir %(installer_root)s/usr/etc || true
rmdir %(installer_root)s/usr/lib || true
rmdir %(installer_root)s/usr/share/doc/%(base_name)s || true
rmdir %(installer_root)s/usr/share/doc || true
rmdir %(installer_root)s/usr/share || true
rmdir %(installer_root)s/usr || true
cd %(installer_root)s && tar --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(base_name)s/%(ball_name)s *
cp -pv %(installer_root)s/etc/hints/%(hint)s %(cygwin_uploads)s/%(base_name)s/setup.hint
''',
                self.get_substitution_dict (d))

    def cygwin_src_ball (self):
        d = {}

        d['dir'] = self.expand ('%(installer_root)s-src')
        d['cyg_name'] = self.expand ('%(name)s-%(version)s-%(build)s', d)
        d['cyg_ball'] = d['cyg_name'] + '-src.tar.bz2'
        d['cygwin_uploads'] = '%(gub_uploads)s/release'
        
        print self.expand ('''
rm -rf %(dir)s
mkdir -p %(dir)s
tar -C %(dir)s -zxf %(src_package_ball)s
mv %(dir)s/%(name)s-%(version)s %(dir)s/%(cyg_name)s
mkdir -p %(cygwin_uploads)s/%(name)s
tar -C %(dir)s --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(name)s/%(cyg_ball)s %(cyg_name)s
''', env=d)

def parse_command_line ():
    p = optparse.OptionParser ()
    p.usage = 'cygwin-packager.py [OPTION]... PACKAGE'
    p.add_option ('-b', '--build-number',
                  action='store', default='1', dest='build')
    (options, args) = p.parse_args ()
    if len (args) != 1:
        p.print_help ()
        sys.exit (2)
    return (options, args)

def main ():
    (options, commands)  = parse_command_line ()
    platform = 'cygwin'
    settings = settings_mod.get_settings (platform)
    settings.build = options.build

    # Barf
    settings.__dict__['cross_distcc_hosts'] = []
    settings.__dict__['native_distcc_hosts'] = []

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:' + PATH)

    Cygwin_package (settings, commands[0])
    
if __name__ == '__main__':
    main ()
