import string
from new import classobj
from new import instancemethod
#
from gub import build
from gub import misc

mirror = 'http://ftp.de.debian.org/debian'

# http://ftp.de.debian.org/debian/pool/main/l/linux-kernel-headers/

def get_cross_packages (settings):
    # obsolete
    return []

gcc_version = '4.1.1'
glibc_version='2.3.2.ds1-22sarge4'
linux_version = '2.5.999-test7-bk-17'
def get_cross_build_dependencies (settings):
    global gcc_version, glibc_version, linux_version
    #FIXME too late
    gcc_version = '4.1.1'
    if settings.debian_branch == 'stable':
        glibc_version='2.3.2.ds1-22sarge4'
        linux_version = '2.5.999-test7-bk-17'
    else:
        glibc_version='2.3.6.ds1-9'
        linux_version = '2.6.18-6'
    return ['cross/gcc', 'guile-config', 'python-config']

def change_target_package (p):
    from gub import cross
    cross.change_target_package (p)

def get_debian_packages (settings, package_file):
    if settings.verbose:
        print ('parsing: %s...' % package_file)
    return map (lambda j: get_debian_package (settings, j),
          open (package_file).read ().split ('\n\n')[:-1])

def get_debian_package (settings, description):
    s = description[:description.find ('\nDescription')]
    d = dict (map (lambda line: line.split (': ', 1),
           map (string.strip, s.split ('\n'))))
    # FIXME: should blacklist toplevel bin/gub argument iso lilypond
    blacklist = [
        'binutils',
        'cpp',
        'gcc-3.3',
        'cpp-3.3',
        'gcc',
        'gcc-3.4',
        'libgcc1',
        'libgcc1-3.4',
        'lilypond',
        'libstdc++6',
        'libstdc++-dev',
        'libtool',
        'perl',
        'perl-modules',
        'perl-base',
#        'pkg-config',
        ]
    if d['Package'] in blacklist:
        d['Package'] += '::blacklisted'
    package_class = classobj (d['Package'], (build.BinaryBuild,), {})
    from gub import repository
    package.with_vc (repository.TarBall (settings.downloads,
                                         os.path.join (mirror, d['Filename']),
                                         d['Version'],
                                         strip_components=0))
    package = package_class (settings)
    package.name_dependencies = []
    import re
    if d.has_key ('Depends'):
        deps = map (string.strip,
                    re.sub ('\([^\)]*\)', '', d['Depends']).split (', '))
        # FIXME: BARF, ignore choices
        deps = filter (lambda x: x.find ('|') == -1, deps)
        # FIXME: how to handle Provides: ?
        # FIXME: BARF, fixup libc Provides
        deps = map (lambda x: re.sub ('libc($|-)', 'libc6\\1', x), deps)
        deps = map (lambda x: re.sub ('liba52-dev', 'liba52-0.7.4-dev', x), deps)
        deps = map (lambda x: re.sub ('libpng12-0-dev', 'libpng12-dev', x), deps)
        # FIXME: ugh, skip some
        deps = filter (lambda x: x not in blacklist, deps)
        package.name_dependencies = deps

    def get_build_dependencies (self):
        return self.name_dependencies
    package.get_build_dependencies = instancemethod (get_build_dependencies,
                                                     package, package_class)
    pkg_name = d['Package']
    def name (self):
        return pkg_name
    package.name = instancemethod (name, package, package_class)
    return package

## FIXME: c&p cygwin.py
class Dependency_resolver:
    def __init__ (self, settings):
        self.settings = settings
        self.packages = {}
        self.load_packages ()

    def grok_packages_file (self, file):
        for p in get_debian_packages (self.settings, file):
            self.package_fixups (p)
            self.packages[p.name ()] = p

    def package_fixups (self, package):
        if package.name () == 'libqt4-dev':
            def untar (whatsthis):
                build.BinaryBuild.untar (package)
                for i in ('QtCore.pc', 'QtGui.pc', 'QtNetwork.pc'):
                    package.file_sub ([
                            ('includedir', 'deepqtincludedir'),
                            ('(-I|-L) */usr',
                             '''\\1%(system_prefix)s''' % locals ()),
                            ],
                                      '%(srcdir)s/usr/lib/pkgconfig/%(i)s',
                                      env=locals ())
            package.untar = misc.MethodOverrider (package.untar, untar)

    def load_packages (self):
        from gub import gup
        p = gup.DependencyManager (self.settings.system_root,
                                   self.settings.os_interface)
#        arch = settings.platform
#        if settings.platform == 'debian':
#            arch = 'i386'
	arch = self.settings.package_arch
        branch = self.settings.debian_branch
        packages_path = '/dists/%(branch)s/main/binary-%(arch)s/Packages.gz' \
                        % locals ()
        url = mirror + packages_path
        base = self.settings.downloads + '/Packages'
        file = '.'.join ((base, arch, branch))

        # FIXME: download/offline update
        import os
        if not os.path.exists (file):
            misc.download_url (url, self.settings.downloads)
            os.system ('gunzip  %(base)s.gz' % locals ())
            os.system ('mv %(base)s %(file)s' % locals ())
        self.grok_packages_file (file)

    def get_packages (self):
        return self.packages
        
dependency_resolver = None

def init_dependency_resolver (settings):
    global dependency_resolver
    dependency_resolver = Dependency_resolver (settings)

def debian_name_to_dependency_names (name):
    return dependency_resolver.get_dependencies (name)

def get_packages ():
    return dependency_resolver.get_packages ()

#FIXME: stable/unstable?
gub_to_distro_dict = {
    'fontconfig' : ['libfontconfig1'],
    'fontconfig-devel' : ['libfontconfig1-dev'],
    'freetype' : ['libfreetype6'],
    'freetype-devel' : ['libfreetype6-dev'],
    'gettext' : ['gettext'],
    'gettext-devel' : ['gettext'],
    'gmp-devel': ['libgmp3-dev'],
    'gmp-runtime': ['libgmp3'],
    'ghostscript': ['gs'],
    'guile-runtime' : ['guile-1.6-libs'],
    'libtool-runtime': ['libltdl3'],
    'libiconv-devel': ['libiconv2'],
    'pango': ['libpango1.0-0'],
    'python-devel': ['python2.4-dev'],
    'python-runtime': ['python2.4'],
    }
