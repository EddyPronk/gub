import re
import urllib
import string
import pickle
import optparse
import os

platforms = ['linux-x86',
             'linux-64',
             'linux-ppc',
             'darwin-ppc',
             'darwin-x86',
             'documentation',
             'freebsd-x86',
             'mingw',
             'cygwin',
             'source',
             ]

def get_url_versions (url):
    opener = urllib.URLopener ()
    index = opener.open (url).read ()

    versions = []
    def note_version (m):
        name = m.group (1)
        version = tuple (map (int,  m.group (2).split('.')))
        build = 0
        build_url = url + re.sub ("HREF=", '', m.group (0))
        build_url = build_url.replace ('"', "")
        
        # disregard buildnumber for src tarball. 
        if m.group(3):
            build = int (m.group (4))
            
        versions.append ((name, version, build, build_url))
        
        return ''

    # [^0-9] is to force that version no is not swalled by name. Check this for cygwin libfoo3  
    # packages
    re.sub (r'HREF="(.*[^0-9])-([0-9.]+)(-([0-9]+))?\.[0-9a-z-]+\.[.0-9a-z-]+"', note_version, index)

    return versions

class VersionDataBase:
    def __init__ (self, file_name):
        self._db = {}
        self.file_name = file_name
        if os.path.exists (file_name):
            self.read ()
            
    def platforms (self):
        return self._db.keys ()
    
    def get_sources_from_url (self, url):

        directories = ['v0.0', 'v0.1', 'v1.0', 'v1.1', 'v1.2', 'v1.3',
                       'v1.4', 'v1.5', 'v1.6', 'v1.7', 'v1.8', 'v1.9',
                       'v2.0', 'v2.1', 'v2.2', 'v2.3', 'v2.4', 'v2.5',
                       'v2.6', 'v2.7', 'v2.8', 'v2.9', 'v2.10', 'v2.11']

        sources = []
        for d in directories:
            u = '%(url)s%(d)s/' % locals ()
            sources += get_url_versions (u)
            
        self._db['source'] = sources


    def get_binaries_from_url (self, url):
        package = os.path.basename (os.path.splitext (self.file_name)[0])
        for p in platforms:
            if p == 'source':
                continue
            
            u = '%(url)sbinaries/%(p)s/' % locals ()
            
            if p == 'cygwin':
                u += 'release/%(package)s/' % locals ()
            self._db[p] = get_url_versions (u)

    def write (self):
        open (self.file_name,'w').write (pickle.dumps (self._db))

    def read (self):
        self._db = pickle.loads (open (self.file_name).read ())


    ## UI functions:
    def get_next_build_number (self, version_tuple):
        assert (type (version_tuple) == type (()))
        sub_db = {}
        for platform in platforms:
            sub_db[platform] = [0]
            if self._db.has_key (platform):
                sub_db[platform] = [buildnum
                                    for (name, version, buildnum, url)
                                    in self._db[platform]
                                    if version == version_tuple]
            
        return max (max (bs + [0]) for (p, bs) in sub_db.items ()) + 1

    def get_last_release (self, platform, version_tuple):
        candidates = [(v, b, url) for (name, v, b, url) in  self._db[platform]
                      if v[:len (version_tuple)] == version_tuple]
        candidates.append ( ((0,0,0), 0, '/dev/null' ))
        candidates.sort ()
        
        return candidates[-1]

def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage='''versiondb.py  [OPTION]... COMMAND [PACKAGE]...

Inspect lilypond.org download area, and write pickle of all version numbers.

'''
    p.description='Grand Unified Builder.  Specify --package-version to set build version'

    p.add_option ('--dbfile', action='store',
                  dest="dbfile",
                  help="Pickle of version dict",
                  default="uploads/lilypond.versions")
                  
    p.add_option ('--url', action='store',
                  dest='url',
                  default='http://lilypond.org/download/',
                  help='download url')

    p.add_option ('--download', action='store_true',
                  dest='download',
                  default=False,
                  help='download new versions')

    p.add_option ('--build-for', action='store',
                  dest='version',
                  default='',
                  help='print build number for version')

    p.add_option ('--test', action='store_true',
                  dest='test',
                  default=False,
                  help='self test')

    return p

def main ():
    cli_parser = get_cli_parser ()
    (options, files) = cli_parser.parse_args ()

    if options.url and not options.url.endswith ('/'):
        options.url += "/"

    db = VersionDataBase (options.dbfile)
    if options.test:
        print '2.9.28:', db.get_next_build_number ((2,9,28))
        print '2.8.2:', db.get_next_build_number ((2,8,2))
        print '2.9.28:', db.get_next_build_number ((2,9,28))
        print '2.8.2:', db.get_next_build_number ((2,8,2))
        print '2.10.0 next:', db.get_next_build_number ((2,10,0))
        
        print 'last mingw 2.9.26:', db.get_last_release ('mingw', (2,9,26))
        print 'last mingw 2.9:', db.get_last_release ('mingw', (2,9))
        print 'last mingw 2.9:', db.get_last_release ('mingw', (2,))
        print 'last source:', db.get_last_release ('source', ())
        return

    if options.download:
        db.get_sources_from_url (options.url)
        db.get_binaries_from_url (options.url)
        db.write ()

    if options.version:
        v = tuple (map (int, options.version.split ('.')))
        print db.get_next_build_number (v)
    
    
if __name__ == '__main__':
    main ()
