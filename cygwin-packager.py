#! /usr/bin/python

import optparse
import os
import sys

sys.path.insert (0, 'lib/')

import context
import gup
import cross
import settings as settings_mod
import misc
import targetpackage

def sort (lst):
    list.sort (lst)
    return lst

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

        self.installer_root = '%(targetdir)s/installer-%(name)s'
        self.installer_db = '%(targetdir)s/installer-%(name)s-dbdir'
        self.installer_uploads = settings.uploads

        self.package_manager = gup.DependencyManager (
            self.expand ('%(installer_root)s'),
            settings.os_interface,
            dbdir=self.expand ('%(installer_db)s'),
            clean=True)

        self.package_manager.include_build_deps = False
        self.package_manager.read_package_headers (
            self.expand ('%(gub_uploads)s/%(name)s'), 'HEAD')

        #def get_dep (x):
        #    return install_manager.dependencies (x)
    
        #package_names = gup.topologically_sorted (args, {},
        #                                          get_dep,
        #                                          None)

        self.create ()
      
    @context.subst_method
    def name (self):
        return self._name
    
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
        build_number = self.expand ('%(build_number)s')

        # FIXME: lilypond is built from CVS, in which case version is lost
        # and overwritten by the CVS branch name.  Therefore, using
        # %(version)s in lilypond's hint file will not work.  Luckily, for
        # the lilypond package %(installer_version)s, is what we need.
        # Note that this breaks when building guile from cvs, eg.

        installer_version = spec.build_version ()

        # FIXME, this is the accidental build number of LILYPOND, which is
        # wrong to use for guile and other packages, but uh, individual
        # packages do not have a build number anymore...
        build = build_number

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
        if split:
            external_source_line = spec.expand ('''
external-source: %(name)s''', locals ())
        try:
            ldesc = spec.description_dict ()[split]
            sdesc = ldesc[:ldesc.find ('\n')]
        except:
            sdesc = spec.expand ('%(name)s')
            flavor = 'executables'
            if split:
                sdesc += ' ' + split
                flavor = split
            ldesc = 'The %(name)s package for Cygwin - ' + flavor
        try:
            category = spec.category_dict ()[split]
        except:
            if not split:
                caterory = 'utils'
            elif split == 'runtime':
                caterory = 'libs'
            else:
                caterory = split
        requires_line = ''
        if requires:
            requires_line = spec.expand ('''
requires: %(requires)s''',
                                         locals ())
        hint = spec.expand ('''sdesc: "%(sdesc)s"
ldesc: "%(ldesc)s"
category: %(category)s%(requires_line)s%(external_source_line)s
''',
                                locals ())
        print 'dumping hint for: ' + split
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
        ###build_number = spec.build_number ()
        build_number = self.expand ('%(build_number)s')

        # FIXME: lilypond is built from CVS, in which case version is lost
        # and overwritten by the CVS branch name.  Therefore, using
        # %(version)s in lilypond's hint file will not work.  Luckily, for
        # the lilypond package %(installer_version)s, is what we need.
        # Note that this breaks when building guile from cvs, eg.

        installer_version = spec.build_version ()

        # FIXME, this is the accidental build number of LILYPOND, which is
        # wrong to use for guile and other packages, but uh, individual
        # packages do not have a build number anymore...
        build = build_number

        file = spec.expand (spec.settings.sourcefiledir
                            + '/%(name)s.README', locals ())
        if os.path.exists (file):
            readme = spec.expand (open (file).read (), locals ())
        else:
            readme = spec.expand ('README for Cygwin %(name)s-%(installer_version)s-%(build_number)s', locals ())

        spec.dump (readme,
                   '%(installer_root)s/usr/share/doc/Cygwin/%(name)s-%(installer_version)s-%(build_number)s.README',
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

        import re
        gub_name = re.sub ('.*/', '', gub_ball)

	import misc
        branch = 'HEAD'
        # Urg: other packages than lilypond can have a -BRANCH naming
        if package_name == 'texlive':
            branch = 'HEAD'
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
        cyg_name = dir_name + '-%(build_number)s'
        # FIXME: not in case of -branch name
        dir_name = re.sub ('.cygwin.gu[pb]', '', gub_name)
        hint = base_name + '.hint'

        # FIXME: sane package installer root
        installer_root = '%(targetdir)s/installer-%(base_name)s'
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
    
    def strip_dir (self, dir):
        import misc
        misc.map_command_dir (self.expand (dir),
                              self.expand ('%(strip_command)s)'),
                              self.no_binary_strip,
                              self.no_binary_strip_extensions)

    def cygwin_ball (self, package, split):
        d = self.get_dict (package, split)
        base_name = d['base_name']
        ball_name = d['cyg_name'] + '.tar.bz2'
        hint = d['hint']
        infodir = d['infodir'] % self.get_substitution_dict (d)
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
                self.strip_dir (dir)

        if os.path.isdir (infodir + '/' + package_name):
            package.system ('gzip %(infodir)s/%(package_name)s/*.info*',
                            locals ())
        elif os.path.isdir (infodir):
            package.system ('gzip %(infodir)s/*.info*', locals ())
        package.system ('''
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

    def cygwin_src_ball (self, package):
        d = self.get_dict (package, '')
        ball_name = d['cyg_name'] + '-src.tar.bz2'
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

def parse_command_line ():
    p = optparse.OptionParser ()
    p.usage = 'cygwin-packager.py [OPTION]... PACKAGE'
    p.add_option ('-b', '--build-number',
                  action='store', default='1', dest='build_number')
    p.add_option ('-v', '--version',
                  action='store', default='0.0.0', dest='version')
    (options, args) = p.parse_args ()
    if len (args) != 1:
        p.print_help ()
        sys.exit (2)
    return (options, args)

def main ():
    (options, commands)  = parse_command_line ()
    platform = 'cygwin'
    settings = settings_mod.get_settings (platform)
    settings.build_number = options.build_number
    settings.version = options.version

    # Barf
    settings.__dict__['cross_distcc_hosts'] = []
    settings.__dict__['native_distcc_hosts'] = []

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:' + PATH)

    Cygwin_package (settings, commands[0])
    
if __name__ == '__main__':
    main ()
