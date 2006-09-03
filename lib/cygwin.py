import os
import re

from new import classobj
from new import instancemethod
#
import cross
import download
import gub
import gup
import mingw
import misc

# FIXME: setting binutil's tooldir and/or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils (cross.Binutils):
    def makeflags (self):
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def compile_command (self):
        return (cross.Binutils.compile_command (self)
                + self.makeflags ())
    def configure_command (self):
        return ( cross.Binutils.configure_command (self)
                 + ' --disable-werror ')

class W32api_in_usr_lib (gub.BinarySpec, gub.SdkBuildSpec):
    def get_build_dependencies (self):
        return ['w32api']
    def do_download (self):
        pass
    def untar (self):
        self.system ('mkdir -p %(srcdir)s/root/usr/lib')
        self.system ('''
tar -C %(system_root)s/usr/lib/w32api -cf- . | tar -C %(srcdir)s/root/usr/lib -xf-
''')

class Gcc (mingw.Gcc):
    def get_build_dependencies (self):
        return (mingw.Gcc.get_build_dependencies (self)
                + ['cygwin', 'w32api-in-usr-lib'])
    def makeflags (self):
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def compile_command (self):
        return (mingw.Gcc.compile_command (self)
                + self.makeflags ())

    def configure_command (self):
        return (mingw.Gcc.configure_command (self)
                + misc.join_lines ('''
--with-newlib
--enable-threads
'''))

class Gcc_core (Gcc):
    def untar (self):
        gxx_file_name = re.sub ('-core', '-g++',
                                self.expand (self.file_name ()))
        self.untar_cygwin_src_package_variant2 (gxx_file_name, split=True)
        self.untar_cygwin_src_package_variant2 (self.file_name ())

# download-only package
class Gcc_gxx (gub.NullBuildSpec):
    pass

mirror = 'http://mirrors.kernel.org/sourceware/cygwin'
def get_cross_packages (settings):
    import linux
    cross_packs = [
        #Binutils (settings).with (version='2.16.1', format='bz2'),
        Binutils (settings).with (version='2.17', format='bz2'),
        #Binutils (settings).with (version='20060817-1', format='bz2', mirror=download.cygwin),
        W32api_in_usr_lib (settings).with (version='1.0'),
        Gcc (settings).with (version='4.1.1', mirror=download.gcc_41, format='bz2'),
        #Gcc_core (settings).with (version='3.4.4-1', mirror=download.cygwin_gcc, format='bz2'),
        #Gcc_gxx (settings).with (version='3.4.4-1', mirror=download.cygwin_gcc, format='bz2'),
        linux.Python_config (settings).with (version='2.4.3'),
        ]

    return cross_packs

def change_target_packages (packages):
    cross.change_target_packages (packages)

    # FIXME: this does not work (?)
    for p in packages.values ():
        old_callback = p.get_build_dependencies
        p.get_build_dependencies = cross.MethodOverrider (old_callback,
                                                          lambda old_val, extra_arg: old_val + extra_arg, (['cygwin'],)).method
        
        # FIXME: why do cross packages get here too?
        if isinstance (p, cross.CrossToolSpec):
            continue
        gub.change_target_dict (p, {
            'DLLTOOL': '%(tool_prefix)sdlltool',
            'DLLWRAP': '%(tool_prefix)sdllwrap',
            'LDFLAGS': '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api',
            })

def get_cygwin_package (settings, name, dict):
    cross = [
        'base-passwd', 'bintutils',
        'gcc', 'gcc-core', 'gcc-g++',
        'gcc-mingw', 'gcc-mingw-core', 'gcc-mingw-g++',
        'gcc-runtime', 'gcc-core-runtime',
        ]
    cycle = ['base-passwd']
    # FIXME: this really sucks, should translate or something
    # There also is the problem that gub build-dependencies
    # use unsplit packages.
    gup_cygwin_name_clashes = [
        'libtool1.5', # 'libtool' in gup
        ]
    # FIXME: These packages are not needed for [cross] building,
    # but most should stay as distro's final install dependency.
    unneeded = [
        'bash',
        'autoconf', 'autoconf2.13', 'autoconf2.50', 'autoconf2.5',
        'automake', 'automake1.9',
        'coreutils',
        'ghostscript-base', 'ghostscript-x11',
        '-update-info-dir',
        'libguile12', 'libguile16', 'libguile17',
        'libxft', 'libxft1', 'libxft2',
        'libbz2-1',
        'perl',
        'tcltk',
        'x-startup-scripts',
        'xaw3d',
        'xorg-x11-bin-lndir',
        'xorg-x11-etc',
        'xorg-x11-fnts',
        'xorg-x11-libs-data',
        ]
    blacklist = cross + cycle + gup_cygwin_name_clashes + unneeded
    if name in blacklist:
        name += '::blacklisted'
    package_class = classobj (name, (gub.BinarySpec,), {})
    package = package_class (settings)
    package.name_dependencies = []
    if dict.has_key ('requires'):
        deps = re.sub ('\([^\)]*\)', '', dict['requires']).split ()
        deps = [x.strip ().lower ().replace ('_', '-') for x in deps]
        ##print 'gcp: ' + `deps`
        deps = filter (lambda x: x not in blacklist, deps)
        package.name_dependencies = deps

    def get_build_dependencies (self):
        return self.name_dependencies
    package.get_build_dependencies = instancemethod (get_build_dependencies,
                                                     package, package_class)
    package.ball_version = dict['version']
        
    package.url = (mirror + '/'
           + dict['install'].split ()[0])
    package.format = 'bz2'
    return package

## UGH.   should split into parsing  package_file and generating gub specs.
def get_cygwin_packages (settings, package_file):
    dist = 'curr'

    dists = {'test': [], 'curr': [], 'prev' : []}
    chunks = open (package_file).read ().split ('\n\n@ ')
    for i in chunks[1:]:
        lines = i.split ('\n')
        name = lines[0].strip ()
        name = name.lower ()
        packages = dists['curr']
        records = {
            'sdesc': name,
            'version': '0-0',
            'install': 'urg 0 0',
            }
        j = 1
        while j < len (lines) and lines[j].strip ():
            if lines[j][0] == '#':
                j = j + 1
                continue
            elif lines[j][0] == '[':
                packages.append (get_cygwin_package (settings, name,
                                                     records.copy ()))
                packages = dists[lines[j][1:5]]
                j = j + 1
                continue

            try:
                key, value = [x.strip () for x in lines[j].split (': ', 1)]
            except KeyError: ### UGH -> what kind of exceptino?
                print lines[j], package_file
                raise 'URG'
            if (value.startswith ('"')
              and value.find ('"', 1) == -1):
                while 1:
                    j = j + 1
                    value += '\n' + lines[j]
                    if lines[j].find ('"') != -1:
                        break
            records[key] = value
            j = j + 1
        packages.append (get_cygwin_package (settings, name, records))

    # debug
    names = [p.name() for p in dists[dist]]
    names.sort()

    return dists[dist]



class Cygwin_dependency_finder:
    def __init__ (self, settings):
        self.settings = settings
        self.packages = {}
        
    def download (self):
        url = mirror + '/setup.ini'
        # FIXME: download/offline
        downloaddir = self.settings.downloaddir

        file = self.settings.downloaddir + '/setup.ini'
        if not os.path.exists (file):
            misc.download_url (url, self.settings.downloaddir)

        pack_list = get_cygwin_packages (self.settings, file)
        for p in pack_list:
            self.packages[p.name ()] = p

        local_file = self.settings.uploads + '/cygwin/setup.ini'
        if os.path.exists (local_file):
            local_list = get_cygwin_packages (self.settings, local_file)
            for p in local_list:
                self.packages[p.name ()] = p

    def get_packages (self):
        return self.packages
        
cygwin_dep_finder = None

def init_cygwin_package_finder (settings):
    global cygwin_dep_finder
    cygwin_dep_finder = Cygwin_dependency_finder (settings)
    cygwin_dep_finder.download ()

def get_packages ():
    return cygwin_dep_finder.get_packages ()

def copy_readmes_buildspec (spec):
    spec.system ('''
mkdir -p %(install_root)s/usr/share/doc/%(name)s
''')
    import glob
    for i in glob.glob ('%(srcdir)s/[A-Z]*'
                        % spec.get_substitution_dict ()):
        import shutil
        if (os.path.isfile (i)
            and not i.startswith ('Makefile')
            and not i.startswith ('GNUmakefile')):
            shutil.copy2 (i, '%(install_root)s/usr/share/doc/%(name)s'
                          % spec.get_substitution_dict ())

def cygwin_patches_dir_buildspec (spec):
    cygwin_patches = '%(srcdir)s/CYGWIN-PATCHES'
    spec.system ('''
mkdir -p %(cygwin_patches)s
cp -pv %(install_root)s/etc/hints/* %(cygwin_patches)s
cp -pv %(install_root)s/usr/share/doc/Cygwin/* %(cygwin_patches)s
''',
                 locals ())


def dump_readme_and_hints (spec):
    file = spec.expand (spec.settings.sourcefiledir + '/%(name)s.changelog')
    if os.path.exists (file):
        changelog = open (file).read ()
    else:
        changelog = 'ChangeLog not recorded.'

    spec.system ('''
mkdir -p %(install_root)s/usr/share/doc/Cygwin
mkdir -p %(install_root)s/etc/hints
''')

    installer_build = spec.build_number ()

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

    file = spec.expand (spec.settings.sourcefiledir + '/%(name)s.README')
    if os.path.exists (file):
        readme = open (file).read ()
    else:
        readme = 'README for Cygwin %(name)s-%(installer_version)s-%(installer_build)s'
    spec.dump (readme,
               '%(install_root)s/usr/share/doc/Cygwin/%(name)s-%(installer_version)s-%(installer_build)s.README',
               env=locals ())

    # FIXME: get depends from actual split_packages

    ##for name in [spec.name ()] + spec.split_packages:
    ## FIXME split-names
    distro_depends = spec.get_distro_dependency_dict ()
    for name in distro_depends.keys ():
        depends = distro_depends[name]
        requires = ' '.join (depends)
        external_source = ''
        file = (spec.settings.sourcefiledir + '/' + name + '.hint')
        if os.path.exists (file):
            hint = spec.expand (open .read (file), locals ())
        else:
            if name == spec.expand ('%(name)s'):
                external_source = 'external-source: %(name)s'
            hint = spec.expand ('''curr: %(installer_version)s-%(installer_build)s
sdesc: "%(name)s"
ldesc: "The %(name)s package for Cygwin."
category: misc
requires: %(requires)s
%(external_source)s
''',
                                locals ())
        spec.dump (hint,
             '%(install_root)s/etc/hints/%(name)s.hint',
             env=locals ())
