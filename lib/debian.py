import glob
import os
import re
import string
#
import cross
import download
import gup
import gub
import linux
import misc
import settings

from new import classobj
from new import instancemethod

mirror = 'http://ftp.de.debian.org/debian'

class Libc6 (gub.BinarySpec, gub.SdkBuildSpec):
    def untar (self):
        gub.BinarySpec.untar (self)
        # Ugh, rewire absolute names and symlinks.
        i = self.expand ('%(srcdir)s/lib64')
        if os.path.islink (i):
            s = os.readlink (i)
            if s.startswith ('/'):
                os.remove (i)
                os.symlink (s[1:], i)

    def patch (self):
        self.system ('cd %(srcdir)s && rm -rf usr/sbin/ sbin/ bin/ usr/bin')

class Libc6_dev (gub.BinarySpec, gub.SdkBuildSpec):
    def untar (self):
        gub.BinarySpec.untar (self)
        # FIXME: this rewiring breaks ld badly, it says
        #     i686-linux-ld: cannot find /home/janneke/bzr/gub/target/i686-linux/system/lib/libc.so.6 inside /home/janneke/bzr/gub/target/i686-linux/system/
        # although that file exists.  Possibly rewiring is not necessary,
        # but we can only check on non-linux platform.
        # self.file_sub ([(' /', ' %(system_root)s/')],
        #               '%(srcdir)s/root/usr/lib/libc.so')

        for i in ('pthread.h', 'bits/sigthread.h'):
            self.file_sub ([('__thread', '___thread')],
                           '%(srcdir)s/usr/include/%(i)s',
                           env=locals ())
            
        self.system ('rm -rf  %(srcdir)s/usr/include/asm/  %(srcdir)s/usr/include/linux ')
            
class Linux_kernel_headers (gub.BinarySpec, gub.SdkBuildSpec):
    def get_subpackage_names (self):
        return ['']

class Libdbi0_dev (gub.BinarySpec, gub.SdkBuildSpec):
    pass

class Gcc (cross.Gcc):
    def patch (self):
        cross.Gcc.patch (self)
        self.system ("""
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-4.1.1-ppc-unwind.patch
""")
        

    ## TODO: should detect whether libc supports TLS 
    def configure_command (self):
        return cross.Gcc.configure_command (self) + ' --disable-tls '

# http://ftp.de.debian.org/debian/pool/main/l/linux-kernel-headers/

def _get_cross_packages (settings,
                         guile_version, libc6_version, kernel_version):
    configs = []
    if not settings.platform.startswith ('linux'):
        configs = [linux.Guile_config (settings).with (version=guile_version),
                   linux.Python_config (settings).with (version='2.4.1'),]
    
    return [
        Libc6 (settings).with (version=libc6_version, strip_components=0,
                               mirror=download.glibc_deb, format='deb'),
        Libc6_dev (settings).with (version=libc6_version, strip_components=0,
                                   mirror=download.glibc_deb, format='deb'),
        Linux_kernel_headers (settings).with (version=kernel_version, strip_components=0,
                                              mirror=download.lkh_deb,
                                              format='deb'),
        
        cross.Binutils (settings).with (version='2.16.1', format='bz2', mirror=download.gnu),
        Gcc (settings).with (version='4.1.1',
                             mirror=download.gcc, format='bz2'),
        ] + configs

# FIXME: determine libc6_version, kernel_version from
# Packages/Dependency_resolver.
def get_cross_packages_stable (settings):
    guile_version = '1.6.7'
    libc6_version = '2.3.2.ds1-22sarge4'
    kernel_version = '2.5.999-test7-bk-17'
    return _get_cross_packages (settings,
                                guile_version, libc6_version, kernel_version)

# FIXME: determine libc6_version, kernel_version from
# Packages/Dependency_resolver.
def get_cross_packages_unstable (settings):
    guile_version = '1.8.0'
    libc6_version = '2.3.6.ds1-9'
    kernel_version = '2.6.18-3'
    return _get_cross_packages (settings,
                                guile_version, libc6_version, kernel_version)

def get_cross_packages (settings):
    if settings.debian_branch == 'stable':
        return get_cross_packages_stable (settings)
    return get_cross_packages_unstable (settings)

def change_target_package (p):
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
    # FIXME: should blacklist toplevel gub-builder.py argument iso lilypond
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
        'libstdc++-dev',
        'perl',
        'perl-modules',
        'perl-base',
        ]
    if d['Package'] in blacklist:
        d['Package'] += '::blacklisted'
    package_class = classobj (d['Package'], (gub.BinarySpec,), {})
    package = package_class (settings)
    package.name_dependencies = []
    if d.has_key ('Depends'):
        deps = map (string.strip,
              re.sub ('\([^\)]*\)', '',
                  d['Depends']).split (', '))
        # FIXME: BARF, ignore choices
        deps = filter (lambda x: x.find ('|') == -1, deps)
        # FIXME: how to handle Provides: ?
        # FIXME: BARF, fixup libc Provides
        deps = map (lambda x: re.sub ('libc($|-)', 'libc6\\1',
                       x), deps)
        # FIXME: ugh, skip some
        deps = filter (lambda x: x not in blacklist, deps)
        package.name_dependencies = deps

    def get_build_dependencies (self):
        return self.name_dependencies
    package.get_build_dependencies = instancemethod (get_build_dependencies,
                                                     package, package_class)
    package.ball_version = d['Version']
    package.url = mirror + '/' + d['Filename']
    package.format = 'deb'

    import repository
    package.vc_repository = repository.TarBall (settings.downloads,
                                                package.url,
                                                package.ball_version,
                                                strip_components=0)
    return package

## FIXME: c&p cygwin.py
class Dependency_resolver:
    def __init__ (self, settings):
        self.settings = settings
        self.packages = {}
        self.load_packages ()
        
    def grok_packages_file (self, file):
        for p in get_debian_packages (self.settings, file):
            self.packages[p.name ()] = p

    def load_packages (self):
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
