import os
import re
import inspect
import new
#
from gub.syntax import printf
from gub import build
from gub import context
from gub import cross
from gub import misc
from gub import repository
from gub import target
from gub import w32

def libpng12_fixup (self):
    self.system ('cd %(system_prefix)s/lib && ln -sf libpng12.a libpng.a')
    self.system ('cd %(system_prefix)s/include && ln -sf libpng12/png.h .')
    self.system ('cd %(system_prefix)s/include && ln -sf libpng12/pngconf.h .')

mirror = 'http://mirrors.kernel.org/sourceware/cygwin'

def get_cross_build_dependencies (settings):
    return ['cross/gcc', 'freetype-config', 'python-config']

def change_target_package (package):
    cross.change_target_package (package)
    w32.change_target_package (package)

    package.get_build_dependencies \
            = misc.MethodOverrider (package.get_build_dependencies,
                                    lambda d, extra: d + extra, (['cygwin'],))

    def cyg_defs (d):
        k = 'runtime'
        if k not in d:
            k = ''
        d[k].append ('/usr/bin/cyg*dll')
        d[k].append ('/etc/postinstall')
        return d

    package.get_subpackage_definitions \
        = misc.MethodOverrider (package.get_subpackage_definitions, cyg_defs)

    package.configure_command = (package.configure_command
                                 .replace ('--disable-static', '--enable-static'))

    def install (whatsthis):
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
        for i in package.subpackage_names:
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

        for i in package.subpackage_names:
            if not d.get (i):
                d[i] = get_subpackage_doc (i)
        return d

    package.description_dict = misc.MethodOverrider (package.description_dict,
                                                     description_dict)

def package_class (name, cygwin_spec, blacklist):
    cls = new.classobj (name, (build.BinaryBuild,), {})
    deps = []
    if 'requires' in cygwin_spec:
        deps = re.sub ('\([^\)]*\)', '', cygwin_spec['requires']).split ()
        #deps = [x.strip ().lower ().replace ('_', '-') for x in deps]
        deps = [x.strip () for x in deps]
        # URG, x11 introduces upcase *and* underscore in package name
        #deps = [x.replace ('libx11-6', 'libX11_6') for x in deps]
        #deps = [x.replace ('libxt', 'libXt') for x in deps]
        #deps = [x.replace ('libx11', 'libX11') for x in deps]
        deps = [x for x in deps if x not in blacklist]
    cls.name_dependencies = deps
    def get_build_dependencies (self):
        return self.name_dependencies
    cls.get_build_dependencies = get_build_dependencies
    @context.subst_method
    def name_func (self):
        return name
    cls.name = name_func
    return cls

def get_cygwin_package (settings, name, cygwin_spec, skip):
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
        'xorg-x11-devel',
        'xorg-x11-fnts',
        'xorg-x11-libs-data',
        ]
    blacklist = cross + cycle + skip + unneeded
    if name in blacklist:
        name += '::blacklisted'
    cls = package_class (name, cygwin_spec, blacklist)
    source = repository.TarBall (settings.downloads + '/cygwin',
                                 os.path.join (mirror,
                                               cygwin_spec['install'].split ()[0]),
                                 cygwin_spec['version'],
                                 strip_components=0)
    return cls (settings, source)

## UGH.   should split into parsing  package_file and generating gub specs.
def get_cygwin_packages (settings, package_file, skip=[]):
    dist = 'curr'

    dists = {'test': [], 'curr': [], 'prev' : []}
    chunks = open (package_file).read ().split ('\n\n@ ')
    for i in chunks[1:]:
        lines = i.split ('\n')
        name = lines[0].strip ()
        #name = name.lower ()
        name = name[0].lower () + name[1:]
        # URG, x11 introduces upcase *and* underscore in package name
        #name = name.replace ('libx11-6', 'libX11_6')
        #name = name.replace ('libx11_6', 'libX11_6')
        #name = name.replace ('libx11', 'libX11')
        #name = name.replace ('libxt', 'libXt')

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
                printf (lines[j], package_file)
                raise Exception ('URG')
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
    def __init__ (self, settings, todo):
        self.settings = settings
        if not os.path.exists (self.settings.downloads + '/cygwin'):
            os.makedirs (self.settings.downloads + '/cygwin')
        self.packages = {}
        self.source = libtool_source + list (map (misc.strip_platform, todo))
        self.load_packages ()

    def grok_setup_ini (self, file, skip=[]):
        for p in get_cygwin_packages (self.settings, file, skip):
            self.packages[p.name ()] = p
    def load_packages (self):
        url = mirror + '/setup.ini'

        # FIXME: download/offline update
        file = self.settings.downloads + '/cygwin/setup.ini'
        if not os.path.exists (file):
            misc.download_url (url, self.settings.downloads + '/cygwin',
                               local=['file://' + self.settings.downloads + '/cygwin'],
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

def init_dependency_resolver (settings, todo):
    global dependency_resolver
    dependency_resolver = Dependency_resolver (settings, todo)

def get_packages ():
    return dependency_resolver.get_packages ()

gub_to_distro_dict = {
    'cross/binutils': [],
    'cross/gcc': [],
    'cross/gcc-c++-runtime': [],
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
    'texlive-runtime': ['libkpathsea4'],
#    'libx11-6': ['libX11_6'],
    }
