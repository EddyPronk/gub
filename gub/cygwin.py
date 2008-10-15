import os
import re
import inspect

from new import classobj
from new import instancemethod
#
from gub import build
from gub import misc
from gub import targetbuild

def untar_cygwin_src_package_variant2 (self, file_name, split=False):
    '''Unpack this unbelievably broken version of Cygwin source packages.

foo[version][-split]-x.y.z-b.tar.bz2 contains
foo[-split]-x.y.z.tar.[bz2|gz] and foo[version]-x.y.z-b.patch
(and optionally foo[version]-x.y.z-b.patch2 ...).
foo-x.y.z.tar.[bz2|gz] contains foo-x.y.z.  The patch contains patches
against all foo split source balls, so applying it may fail partly and
complain about missing files.'''

    file_name = self.expand (file_name)
    unpackdir = os.path.dirname (self.expand (self.srcdir ()))
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
rm -rf %(unpackdir)s/%(base)s
tar -C %(unpackdir)s %(flags)s %(downloads)s/%(file_name)s
''',
                 locals ())
    tgz = 'tar.bz2'
# WTF?  self.expand is broken here?
# relax, try not making typos:
#    if not os.path.exists (self.expand ('%(unpackdir)s/%(second_tarball)s.%(tgz)s',
#                                        locals ())):
    if not os.path.exists (unpackdir + '/' + second_tarball + '.' + tgz):
        flags = '-zxf'
        tgz = 'tar.gz'
    self.system ('''
tar -C %(unpackdir)s %(flags)s %(unpackdir)s/%(second_tarball)s.%(tgz)s
''',
                 locals ())
    if split:
        return
    if m.group (2):
        patch = re.sub (ball_re, '\\1\\2\\4\\5.patch', base)
    else:
        patch = re.sub (ball_re, '\\1\\4\\5.patch', base)
    print 'patch: ' + patch
    print 'scrdir: ', self.expand ('%(srcdir)s')
    self.system ('''
cd %(unpackdir)s && mv %(second_tarball_contents)s %(base)s
cd %(srcdir)s && patch -p1 -f < %(unpackdir)s/%(patch)s || true
''',
                 locals ())

def libpng12_fixup (self):
    self.system ('cd %(system_prefix)s/lib && ln -sf libpng12.a libpng.a')
    self.system ('cd %(system_prefix)s/include && ln -sf libpng12/png.h .')
    self.system ('cd %(system_prefix)s/include && ln -sf libpng12/pngconf.h .')

mirror = 'http://mirrors.kernel.org/sourceware/cygwin'

def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['cross/gcc', 'freetype-config', 'python-config']

def change_target_package (package):
    from gub import cross
    cross.change_target_package (package)

    available = dict (inspect.getmembers (package, callable))

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

    def install (whatsthis):
        package.post_install_smurf_exe ()
        package.install_readmes ()

    package.install = misc.MethodOverrider (package.install, install)

    def category_dict (d):
        default = {
            '': 'Utils',
            'devel': 'Devel',
            'doc': 'Doc',
            'runtime': 'Libs',
            'x11': 'X11',
            }
        full = default.copy ()
        full.update (d)
        for i in package.get_subpackage_names ():
            if not full.get (i):
                full[i] = full['']
        return full

    package.category_dict = misc.MethodOverrider (package.category_dict,
                                                  category_dict)

    def description_dict (d):
        # FIXME: fairly uninformative description for packages,
        # unlike, eg, guile-devel.  This is easier, though.
        def get_subpackage_doc (split):
            flavor = package.category_dict ()[split]
            doc = package.__class__.__doc__
            if not doc:
                doc = misc.get_from_parents (package.__class__, '__doc__')
            if not doc:
                doc = '\n'
            return (doc.replace ('\n', ' - %(flavor)s\n', 1) % locals ())

        for i in package.get_subpackage_names ():
            if not d.get (i):
                d[i] = get_subpackage_doc (i)
        return d

    package.description_dict = misc.MethodOverrider (package.description_dict,
                                                     description_dict)

    ## TODO : get_dependency_dict

    # FIXME: why do cross packages get here too?
    if isinstance (package, cross.CrossToolsBuild):
        return package

    targetbuild.change_target_dict (package, {
            'DLLTOOL': '%(toolchain_prefix)sdlltool',
            'DLLWRAP': '%(toolchain_prefix)sdllwrap',
            'LDFLAGS': '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api',
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
    package_class = classobj (name, (build.BinaryBuild,), {})
    from gub import repository
    source = repository.TarBall (settings.downloads,
                                 os.path.join (mirror,
                                               dict['install'].split ()[0]),
                                 dict['version'],
                                 strip_components=0)
    package = package_class (settings, source)
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
ghostscript_source = [
    'ghostscript',
    'ghostscript-doc',
    'ghostscript-x11',
    ]
fontconfig_source = [
    'fontconfig',
    'libfontconfig1',
    'libfontconfig-devel',
    'fontconfig-devel',
    ]
freetype_source = [
    'freetype2',
    'libfreetype26',
    'libfreetype2-devel',
    ]
libtool_source = [
    'libltdl3',
    'libtool',
    'libtool1.5',
    ]

# FIXME: c&p debian.py
class Dependency_resolver:
    def __init__ (self, settings):
        self.settings = settings
        self.packages = {}
#        self.source = fontconfig_source + freetype_source + guile_source + libtool_source
        self.source = fontconfig_source + ghostscript_source + guile_source + libtool_source
        self.load_packages ()

    def grok_setup_ini (self, file, skip=[]):
        for p in get_cygwin_packages (self.settings, file, skip):
            self.packages[p.name ()] = p
    def load_packages (self):
        url = mirror + '/setup.ini'

        # FIXME: download/offline update
        file = self.settings.downloads + '/setup.ini'
        if not os.path.exists (file):
            misc.download_url (url, self.settings.downloads,
                               local=['file://%s' % self.settings.downloads],

                               )
            # arg
            # self.file_sub ([('\':"', "':'")], file)
            s = open (file).read ()
            open (file, 'w').write (s.replace ('\':"', "':'"))
        self.grok_setup_ini (file, self.source)

        # support one extra tools setup.ini, that overrides the default
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
