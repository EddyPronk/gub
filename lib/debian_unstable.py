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

mirror = 'http://ftp.de.debian.org/debian'

## FIXME FIXME 
def xxxget_cross_packages (settings):
    p = gup.DependencyManager (settings.system_root, settings.os_interface)
    url = mirror + '/dists/unstable/main/binary-i386/Packages.gz'
    
    # FIXME: download/offline
    downloaddir = settings.downloaddir
    file = settings.downloaddir + '/Packages'
    if not os.path.exists (file):
        misc.download_url (url, self.expand ('%(downloaddir)s'))
        os.system ('gunzip  %(file)s.gz' % locals ())

        ## FIXME. names
    return filter (lambda x: x.name () not in names, p.get_packages (file))

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
    blacklist = ['lilypond']
    if d['Package'] in blacklist:
        d['Package'] += '_blacklisted'
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
        blacklist = ('perl', 'perl-modules', 'perl-base')
        deps = filter (lambda x: x not in blacklist, deps)
        package.name_dependencies = deps

    ## FIXME.    
    # package.name_build_dependencies = []
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
