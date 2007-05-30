import os
import re

from new import classobj
from new import instancemethod
#
from gub import gubb
from gub import misc

def untar_cygwin_src_package_variant2 (self, file_name, split=False):
    '''Unpack this unbelievably broken version of Cygwin source packages.

foo[version][-split]-x.y.z-b.tar.bz2 contains
foo[-split]-x.y.z.tar.[bz2|gz] and foo[version]-x.y.z-b.patch
(and optionally foo[version]-x.y.z-b.patch2 ...).
foo-x.y.z.tar.[bz2|gz] contains foo-x.y.z.  The patch contains patches
against all foo split source balls, so applying it may fail partly and
complain about missing files.'''

    file_name = self.expand (file_name)
    from gub import misc
    t = misc.split_ball (file_name)
    print 'split: ' + `t`
    no_src = re.sub ('-src', '', file_name)
    base = re.sub ('\.tar\..*', '', no_src)
    # FIXME: use split iso custom ball_re macramee
    ball_re = '^([a-z]+)([.0-9]+)?(-[a-z+]+)?(.*)(-[0-9]+)'
    m = re.match (ball_re, base)
    if m.group (3):
        second_tarball = re.sub (ball_re, '\\1\\3\\4', base)
    else:
        second_tarball = re.sub (ball_re, '\\1\\4', base)
    print 'second_tarball: ' + second_tarball
    if split and m.group (3):
        second_tarball_contents = re.sub (ball_re, '\\1\\3\\4', base)
    else:
        second_tarball_contents = re.sub (ball_re, '\\1\\4', base)
    print 'second_tarball_contents: ' + second_tarball_contents
    flags = '-jxf'
    self.system ('''
rm -rf %(allsrcdir)s/%(base)s
tar -C %(allsrcdir)s %(flags)s %(downloads)s/%(file_name)s
''',
                 locals ())
    tgz = 'tar.bz2'
    if not os.path.exists (self.expand ('%s(allsrcdir)s/%(second_tarball)s.%(tgz)s',
                                        locals ())):
        flags = '-zxf'
        tgz = 'tar.gz'
    self.system ('''
tar -C %(allsrcdir)s %(flags)s %(allsrcdir)s/%(second_tarball)s.%(tgz)s
''',
                 locals ())
    if split:
        return
    if m.group (2):
        patch = re.sub (ball_re, '\\1\\2\\4\\5.patch', base)
    else:
        patch = re.sub (ball_re, '\\1\\4\\5.patch', base)
    print 'patch: ' + patch
    self.system ('''
cd %(allsrcdir)s && mv %(second_tarball_contents)s %(base)s
cd %(srcdir)s && patch -p1 -f < %(allsrcdir)s/%(patch)s || true
''',
                 locals ())

mirror = 'http://mirrors.kernel.org/sourceware/cygwin'

def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['cross/gcc', 'freetype-config', 'python-config']

def change_target_package (package):
    from gub import cross
    cross.change_target_package (package)
    package.get_build_dependencies \
            = misc.MethodOverrider (package.get_build_dependencies,
                                    lambda d, extra: d + extra, (['cygwin'],))

    def cyg_defs (d):
        k = 'runtime'
        if not d.has_key (k):
            k = ''
        d[k].append ('/usr/bin/cyg*dll')
        d[k].append ('/etc/postinstall')
        return d

    package.get_subpackage_definitions \
        = misc.MethodOverrider (package.get_subpackage_definitions, cyg_defs)

    def enable_static (d):
        return d.replace ('--disable-static', '--enable-static')

    package.configure_command \
        = misc.MethodOverrider (package.configure_command, enable_static)

    def install (whatsthis, lst):
	package = lst[0]
        package.post_install_smurf_exe ()
        package.install_readmes ()

    package.install \
        = misc.MethodOverrider (package.install, install, ([package],))

    ## TODO : get_dependency_dict
        
    # FIXME: why do cross packages get here too?
    if isinstance (package, cross.CrossToolSpec):
        return package
        
    gubb.change_target_dict (package, {
            'DLLTOOL': '%(tool_prefix)sdlltool',
            'DLLWRAP': '%(tool_prefix)sdllwrap',
            'LDFLAGS': '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api',
            })

def get_cygwin_package (settings, name, dict, skip):
    cross = [
        'base-passwd', 'bintutils',
        'gcc', 'gcc-core', 'gcc-g++',
        'gcc-mingw', 'gcc-mingw-core', 'gcc-mingw-g++',
        'gcc-runtime', 'gcc-core-runtime',
        ]
    cycle = ['base-passwd']
    # FIXME: These packages are not needed for [cross] building,
    # but most should stay as distro's final install dependency.
    unneeded = [
        'autoconf', 'autoconf2.13', 'autoconf2.50', 'autoconf2.5',
        'automake', 'automake1.9',
        'ghostscript-base', 'ghostscript-x11',
        '-update-info-dir',
        'libguile12', 'libguile16',
        'libxft', 'libxft1', 'libxft2',
        'libbz2-1',
        'perl',
        'tcltk',
        'x-startup-scripts',
        'xorg-x11-bin-lndir',
        'xorg-x11-etc',
        'xorg-x11-fnts',
        'xorg-x11-libs-data',
        ]
    blacklist = cross + cycle + skip + unneeded
    if name in blacklist:
        name += '::blacklisted'
    package_class = classobj (name, (gubb.BinarySpec,), {})
    package = package_class (settings)
    package.name_dependencies = []
    if dict.has_key ('requires'):
        deps = re.sub ('\([^\)]*\)', '', dict['requires']).split ()
        deps = [x.strip ().lower ().replace ('_', '-') for x in deps]

        deps = filter (lambda x: x not in blacklist, deps)
        package.name_dependencies = deps

    def get_build_dependencies (self):
        return self.name_dependencies
    package.get_build_dependencies = instancemethod (get_build_dependencies,
                                                     package, package_class)
    pkg_name = name
    def name (self):
        return pkg_name
    package.name = instancemethod (name, package, package_class)

    package.ball_version = dict['version']
    package.url = (mirror + '/' + dict['install'].split ()[0])
    package.format = 'bz2'
    from gub import repository
    package.vc_repository = repository.TarBall (settings.downloads,
                                                package.url,
                                                package.ball_version,
                                                strip_components=0)
    return package

## UGH.   should split into parsing  package_file and generating gub specs.
def get_cygwin_packages (settings, package_file, skip=[]):
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
                                                     records.copy (),
                                                     skip))
                packages = dists[lines[j][1:5]]
                j = j + 1
                continue

            try:
                key, value = [x.strip () for x in lines[j].split (': ', 1)]
            except:
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
        packages.append (get_cygwin_package (settings, name, records, skip))

    # debug
    names = [p.name () for p in dists[dist]]
    names.sort ()
    return dists[dist]

# FIXME: this really sucks, should translate or something
# There also is the problem that gub build-dependencies
# use unsplit packages.
guile_source = [
    'guile',
    'guile-devel',
    'libguile17',
    ]
fontconfig_source = [
    'fontconfig',
    'libfontconfig1',
    'libfontconfig-devel',
    'fontconfig-devel',
    ]
libtool_source = [
    'libltdl3',
    'libtool',
    'libtool1.5',
    ]

## FIXME: c&p debian.py
class Dependency_resolver:
    def __init__ (self, settings):
        self.settings = settings
        self.packages = {}
        self.source = fontconfig_source + guile_source + libtool_source
        self.load_packages ()
        
    def grok_setup_ini (self, file, skip=[]):
        for p in get_cygwin_packages (self.settings, file, skip):
            self.packages[p.name ()] = p

    def load_packages (self):
        url = mirror + '/setup.ini'

        # FIXME: download/offline update
        file = self.settings.downloads + '/setup.ini'
        if not os.path.exists (file):
            misc.download_url (url, self.settings.downloads)
            # arg
            # self.file_sub ([('\':"', "':'")], file)
            s = open (file).read ()
            open (file, 'w').write (s.replace ('\':"', "':'"))
        self.grok_setup_ini (file, self.source)

        # support one extra local setup.ini, that overrides the default
        local_file = self.settings.uploads + '/cygwin/setup.ini'
        if os.path.exists (local_file):
            ## FIXME: using the generated setup.ini to install the
            ## actual to be distributed cygwin packages with cygwin
            ## names does not work.
            ##
            ## After building gub installs the gub packages, using GUB
            ## naming.
            #self.grok_setup_ini (local_file)
            self.grok_setup_ini (local_file, self.source)

    def get_packages (self):
        return self.packages
        
dependency_resolver = None

def init_dependency_resolver (settings):
    global dependency_resolver
    dependency_resolver = Dependency_resolver (settings)

def get_packages ():
    return dependency_resolver.get_packages ()

gub_to_distro_dict = {
    'expat-devel': ['expat'],
    'fontconfig-runtime' : ['libfontconfig1'],
    'fontconfig-devel' : ['libfontconfig-devel'],
    'freetype' : ['freetype2'],
    'freetype-devel' : ['libfreetype2-devel'],
    'freetype-runtime' : ['libfreetype26'],
    'freetype2-devel' : ['libfreetype2-devel'],
    'freetype2-runtime' : ['libfreetype26'],
    'gettext' : ['libintl8', 'libintl3'],
    'gmp-devel': ['gmp'],
    'guile-runtime' : ['libguile17', 'libguile12'],
#    'libtool': ['libtool1.5'],
    'libtool-runtime': ['libltdl3'],
    'libiconv-devel': ['libiconv2'],
    'pango': ['pango-runtime'],
    'python-devel': ['python'],
    'python-runtime': ['python'],
    'texlive-devel': ['libkpathsea-devel'],
    'texlive-runtime': ['libkpathsea4']
    }
