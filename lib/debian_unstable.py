import os
import string
import re
#
import cross
import gup
import gub
import misc
import settings

from new import classobj
from new import instancemethod

mirror = 'http://ftp.de.debian.org/debian'

## FIXME FIXME: see mipsel.py, also fix arm.py
def get_cross_packages (settings):
    pass

def change_target_packages (packages):
    cross.change_target_packages (packages)


def get_debian_packages (settings, package_file):
    if settings.verbose:
        print ('reading packages file: %s' % package_file)
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

    return package

## FIXME: c&p cygwin.py
class Debian_dependency_finder:
    def __init__ (self, settings):
        self.settings = settings
        self.packages = {}
        
    def download (self, packages_path):
        p = gup.DependencyManager (self.settings.system_root,
                                   self.settings.os_interface)
        url = mirror + packages_path

        downloaddir = self.settings.downloaddir
        base = self.settings.downloaddir + '/Packages'
        file = base + '.' + self.settings.platform
        if not os.path.exists (file):
            misc.download_url (url, self.settings.downloaddir )
            os.system ('gunzip  %(base)s.gz' % locals ())
            os.system ('mv %(base)s %(file)s' % locals ())

        pack_list  = get_debian_packages (self.settings, file)
        for p in pack_list:
            self.packages[p.name()] = p

    def get_dependencies (self, name):
        return self.packages[name]
        
debian_dep_finder = None

def init_debian_package_finder (settings, packages_path):
    global debian_dep_finder
    debian_dep_finder  = Debian_dependency_finder (settings)
    debian_dep_finder.download (packages_path)
def debian_name_to_dependency_names (name):
    return debian_dep_finder.get_dependencies (name)
