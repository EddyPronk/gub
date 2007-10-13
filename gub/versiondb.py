#!/usr/bin/env python

"""
    Copyright (c) 2005--2007
    Jan Nieuwenhuizen <janneke@gnu.org>
    Han-Wen Nienhuys <hanwen@xs4all.nl>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write toth e Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import re
import urllib
import string
import pickle
import optparse
import os


def get_url_versions (url):
    print url
    opener = urllib.URLopener ()
    index = opener.open (url).read ()

    versions = []
    def note_version (m):
        name = m.group (2)
        version = tuple (map (int,  m.group (3).split ('.')))
        build = 0
        build_url = url + re.sub ("(HREF|href)=", '', m.group (0))
        build_url = build_url.replace ('"', "")

        # disregard buildnumber for src tarball.
        if m.group (4):
            build = int (m.group (5))

        versions.append ((name, version, build, build_url))

        return ''

    # [^0-9] is to force that version no is not swalled by name. Check this for cygwin libfoo3
    # packages
    re.sub (r'(HREF|href)="(.*[^0-9])-([0-9.]+)(-([0-9]+))?\.[0-9a-z-]+\.[.0-9a-z-]+"', note_version, index)

    return versions

class VersionDataBase:
    def __init__ (self, file_name, platforms):
        self._db = {}
        self.file_name = file_name
        self.platforms = platforms
        if os.path.exists (file_name):
            self.read ()

    def platforms (self):
        return self._db.keys ()

    def get_sources_from_url (self, url):

        ## ugh: should follow urls in the index.
        directories = ['v0.0', 'v0.1', 'v1.0', 'v1.1', 'v1.2', 'v1.3',
                       'v1.4', 'v1.5', 'v1.6', 'v1.7', 'v1.8', 'v1.9',
                       'v2.0', 'v2.1', 'v2.2', 'v2.3', 'v2.4', 'v2.5',
                       'v2.6', 'v2.7', 'v2.8', 'v2.9', 'v2.10', 'v2.11']

        sources = []
        for d in directories:
            # FIXME: this / is necessary to prevent 301 redirection
            u = '%(url)ssources/%(d)s/' % locals ()
            sources += get_url_versions (u)
        self._db['source'] = sources

    def get_binaries_from_url (self, url):
        package = os.path.basename (os.path.splitext (self.file_name)[0])
        for p in self.platforms:
            if p == 'source':
                continue

            u = '%(url)sbinaries/%(p)s/' % locals ()

            if p == 'cygwin':
                u += 'release/%(package)s/' % locals ()

            try:
                self._db[p] = get_url_versions (u)
            except IOError, x:
                print 'problem loading', u
                sys.path.insert ('gub')
                import misc
                print misc.exception_string (x)
                continue

    def write (self):
        open (self.file_name,'w').write (pickle.dumps ((self.platforms,
                                                        self._db)))

    def read (self):
        (self.platforms,
         self._db) = pickle.loads (open (self.file_name).read ())

    ## UI functions:
    def get_next_build_number (self, version_tuple):
        assert (type (version_tuple) == type (()))
        sub_db = {}
        for platform in self.platforms:
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
                  dest='dbfile',
                  help='Pickle of version dict',
                  default='uploads/lilypond.versions')

    p.add_option ('--url', action='store',
                  dest='url',
                  default='http://lilypond.org/download/',
                  help='download url')

    p.add_option ('--download', action='store_true',
                  dest='download',
                  default=False,
                  help='download new versions')

    p.add_option ('--no-sources', action='store_false',
                  dest='do_sources',
                  default=True,
                  help='do not look for versions of sources')

    p.add_option ('--build-for', action='store',
                  dest='version',
                  default='',
                  help='print build number for version')

    p.add_option ('--test', action='store_true',
                  dest='test',
                  default=False,
                  help='self test')

    p.add_option ('--platforms', action='store',
                  dest='platforms',
                  default='',
                  help='platforms to inspect; space separated')

    return p

def main ():
    cli_parser = get_cli_parser ()
    (options, files) = cli_parser.parse_args ()

    if options.url and not options.url.endswith ('/'):
        options.url += "/"

    options.platforms = re.sub ('[, ]+', ' ', options.platforms)
    if not options.platforms:
        sys.stderr.write ("need --platforms definition")
        barf

    db = VersionDataBase (options.dbfile, options.platforms)
    db.platforms = options.platforms.split (' ')

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

        ##ugh
        if options.do_sources:
            db.get_sources_from_url (options.url)

        db.get_binaries_from_url (options.url)
        db.write ()

    if options.version:
        v = tuple (map (int, options.version.split ('.')))
        print db.get_next_build_number (v)


if __name__ == '__main__':
    main ()
