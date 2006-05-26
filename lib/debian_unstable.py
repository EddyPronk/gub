import os
#
import cross
import gup

from new import classobj

mirror = 'http://ftp.de.debian.org/debian'

## FIXME FIXME 
def get_cross_packages (settings):
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
    return map (lambda j: get_debian_package (settings, j),
          open (package_file).read ().split ('\n\n')[:-1])

def get_debian_package (settings, description):
    s = description[:description.find ('\nDescription')]
    d = dict (map (lambda line: line.split (': ', 1),
           map (string.strip, s.split ('\n'))))
    package_class = classobj (d['Package'], (gub.Binary_package,), {})
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
