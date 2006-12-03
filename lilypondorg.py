#!/usr/bin/python

## interaction with lp.org down/upload area.

import os
import urllib
import re
import string
import sys
import optparse
import pickle

sys.path.insert (0, 'lib')

import versiondb

platforms = ['linux-x86',
             'linux-64',
             'darwin-ppc',
             'darwin-x86',
             'documentation',
             'freebsd-x86',
#             'freebsd6-x86',
#             'linux-arm',
             'mingw',
             'cygwin',
             ]

build_platform = {
	'darwin': 'darwin-ppc',
	'linux2': 'linux-x86',
}[sys.platform]

base_url = 'http://lilypond.org/download'


host_spec = 'hanwen@lilypond.org:/var/www/lilypond'
host_source_spec = host_spec + '/download'
host_binaries_spec = host_spec + '/download/binaries'
host_doc_spec = host_spec + '/doc'

formats = {
    'darwin-ppc': 'tar.bz2',
    'darwin-x86': 'tar.bz2',

    'linux-x86': 'sh',
    'linux-64': 'sh',
    'linux-arm': 'sh',

    'freebsd4-x86': 'sh',
    'freebsd6-x86': 'sh',
    'freebsd-x86': 'sh',

    'mingw': 'exe',

    'cygwin': 'tar.bz2',

    'documentation': 'tar.bz2',
    }

def system (c):
    print c
    if os.system (c):
        raise 'barf'

def upload_binaries (repo, version, version_db):
    build = version_db.get_next_build_number (version)
    
    version_str = '.'.join (['%d' % v for v in version])
    branch = repo.branch
#    if (version[1] % 2) == 0:
#        branch = 'lilypond_%d_%d' % (version[0], version[1])
#    if (version[1] % 2) == 0:
#        branch = 'stable-%d.%d' % (version[0], version[1])

    src_dests = []
    cmds = []

    ## ugh: 24 is hardcoded in repository.py
    committish = repo.git_pipe ('describe --abbrev=24 %(branch)s' % locals ()).strip ()
    commitishes = {}
    barf = False
    for platform in platforms:

        format = formats[platform]
        base = ('lilypond-%(version_str)s-%(build)d.%(platform)s.%(format)s'
                % locals ())
        bin = 'uploads/%(base)s' % locals ()

        if platform == 'cygwin':
            continue
        elif not os.path.exists (bin):
            print 'binary does not exist', bin
            barf = 1
        else:
            ## globals -> locals.
            host = host_binaries_spec 
            src_dests.append ((os.path.abspath (bin),
                               '%(host)s/%(platform)s' % locals ()))
            
        if platform != 'documentation' and os.path.exists (bin):
            branch = repo.branch
            hdr = pickle.load (open ('uploads/%(platform)s/lilypond-%(branch)s.%(platform)s.hdr' % locals ()))
            key = hdr['source_checksum']
            
            lst = commitishes.get (key, [])
            lst.append (platform)
            
            commitishes[key] = lst
        
        if (platform != 'documentation'
            and  not os.path.exists ('log/%s.test.pdf' % base)):
            print 'test result does not exist for %s' % base
            cmds.append ('python test-lily/test-binary.py %s'
                         % os.path.abspath (bin))
            barf = 1

    if len (commitishes) > 1 or (len (commitishes) == 1
                                 and commitishes.keys()[0] != committish):
        print 'uploading multiple versions'
        print '\n'.join (`x` for x in commitishes.items ())
        print 'repo:', committish
        
    src_tarball = "uploads/lilypond-%(version_str)s.tar.gz" % locals ()
    src_tarball = os.path.abspath (src_tarball)
    
    if not os.path.exists (src_tarball):
        print "source tarball doesn't exist", src_tarball
        barf = True
    else:
        host = host_source_spec 
        majmin = '.'.join (['%d' % v for v in version[:2]])
        src_dests.append ((src_tarball, '%(host)s/v%(majmin)s' % locals ()))
        
    d = globals ().copy ()
    d.update (locals ())

    d['cwd'] = os.getcwd ()
    d['lilybuild'] = d['cwd'] + '/target/%(build_platform)s/build/lilypond-%(branch)s' % d
    d['lilysrc'] = d['cwd'] + '/target/%(build_platform)s/src/lilypond-%(branch)s' % d 
    
    test_cmd = r'''python %(cwd)s/test-lily/rsync-lily-doc.py \
  --upload %(host_doc_spec)s \
  %(lilybuild)s/out-www/web-root/''' % d
    
    cmds.append (test_cmd)

    cmds += ['rsync --delay-updates --progress %s %s'
             % tup for tup in src_dests]

    
    cmds.append ("rsync -v --recursive --delay-updates --progress uploads/cygwin/release/ %(host_binaries_spec)s/cygwin/release/" % globals ())



    description = repo.git_pipe ('describe --abbrev=39 %(branch)s' % locals()).strip ()
    
    git_tag = 'release/%(version_str)s-%(build)d' % locals () 
    git_tag_cmd = 'git --git-dir downloads/lilypond.git tag -a -m "build and upload" %(git_tag)s %(branch)s' % locals ()
    git_push_cmd = 'git --git-dir downloads/lilypond.git push ssh+git://git.sv.gnu.org/srv/git/lilypond.git/ refs/tags/%(git_tag)s:refs/tags/%(git_tag)s' % locals ()
    darcs_tag_cmd = 'darcs tag --patch "release %(version_str)s-%(build)d of lilypond %(description)s" ' % locals()


    cmds.append (git_tag_cmd)
    cmds.append (git_push_cmd)

    cmds.append (darcs_tag_cmd)
    
    print '\n\n'
    print '\n'.join (cmds);
    print '\n\n'
    if barf:
        raise Exception ('barf')

    for cmd in cmds:
        system (cmd)


def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage = """lilypondorg.py [OPTION]... COMMAND [PACKAGE]...

Commands:

upload x.y.z      - upload packages
nextbuild x.y.z   - get next build number
versions          - print versions
foobar            - print versions of dl.la.org
"""
    
    p.description = 'look around on lilypond.org'

    p.add_option ('--url', action='store',
                  dest='url',
                  default=base_url,
                  help='select base url')

    p.add_option ('--branch', action='store',
                  dest='branch',
                  default='origin',
                  help='select upload directory')

    p.add_option ('--repo-dir', action='store',
                  dest='repo_dir',
                  default='downloads/lilypond.git',
                  help='select repository directory')

    p.add_option ('--version-db', action='store',
                  dest='version_db',
                  default='uploads/lilypond.versions',
                  help='version database')
    
    p.add_option ('', '--upload-host', action='store',
                  dest='upload_host',
                  default=host_spec,
                  help='select upload directory')
    return p

def get_repository (options):
    ## do here, because also used in website generation.
    import repository
    dir = options.repo_dir.replace ('.git','')
    repo = repository.GitRepository (dir, 
                                     branch=options.branch)
    return repo

def main ():
    cli_parser = get_cli_parser ()
    (options, commands)  = cli_parser.parse_args ()

    global base_url, host_spec
    base_url = options.url
    host_spec = options.upload_host

    if not commands:
        cli_parser.print_help ()
        sys.exit (2)

    command = commands[0]
    commands = commands[1:]

    if command == 'upload':
        repo = get_repository (options)
        version = tuple (map (string.atoi, commands[0].split ('.')))
        version_db = versiondb.VersionDataBase (options.version_db)
        upload_binaries (repo, version, version_db)
    else:
        base_url = "http://download.linuxaudio.org/lilypond"
        print max_src_version_url ((2,9))
        print max_version_build ('documentation')
        print max_branch_version_build_url ((2, 6), 'linux-x86')
        print max_branch_version_build_url ((2, 9), 'linux-x86')

if __name__ == '__main__':
    main ()
