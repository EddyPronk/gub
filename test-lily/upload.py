#!/usr/bin/python

## interaction with lp.org down/upload area.

import os
import urllib
import re
import string
import sys
import optparse
import pickle


def argv0_relocation ():
    import os, sys
    bindir = os.path.abspath (os.path.dirname (sys.argv[0]))
    prefix = os.path.dirname (bindir)
    sys.path.insert (0, prefix)

argv0_relocation ()

from gub import versiondb
from gub import misc

platforms = ['linux-x86',
             'linux-64',
             'linux-ppc',
             'darwin-ppc',
             'darwin-x86',
             'documentation',
             'test-output',
             'freebsd-x86',
             'freebsd-64',
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
host_test_spec = host_spec + '/test' 

formats = {
    'darwin-ppc': 'tar.bz2',
    'darwin-x86': 'tar.bz2',

    'linux-x86': 'sh',
    'linux-64': 'sh',
    'linux-arm': 'sh',
    'linux-ppc': 'sh',

    'freebsd4-x86': 'sh',
    'freebsd6-x86': 'sh',
    'freebsd-x86': 'sh',
    'freebsd-64': 'sh',

    'mingw': 'exe',

    'cygwin': 'tar.bz2',

    'documentation': 'tar.bz2',
    'test-output': 'tar.bz2',
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
    cmds = ['chgrp -R lilypond uploads/lilypond*',
            "chmod -R g+rw uploads/lilypond*",
            'chmod 4775 `find uploads/cygwin/release -type d`']


    d = globals ().copy ()
    d.update (locals ())

    d['cwd'] = os.getcwd ()
    d['lilybuild'] = d['cwd'] + '/target/%(build_platform)s/gubfiles/build/lilypond-%(branch)s' % d
    d['lilysrc'] = d['cwd'] + '/target/%(build_platform)s/gubfiles/src/lilypond-%(branch)s' % d 

    ## ugh: 24 is hardcoded in repository.py
    committish = repo.git_pipe ('describe --abbrev=24 %(branch)s' % locals ()).strip ()
    regularized_committish = committish.replace ("/", '-')
    
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
            
        if (platform not in ('documentation', 'test-output')
             and os.path.exists (bin)):
            branch = repo.branch
            hdr = pickle.load (open ('uploads/%(platform)s/lilypond-%(branch)s.%(platform)s.hdr' % locals ()))
            key = hdr['source_checksum']
            
            lst = commitishes.get (key, [])
            lst.append (platform)
            
            commitishes[key] = lst
        
        if (platform not in ('documentation', 'test-output')
            and  not os.path.exists ('log/%s.test.pdf' % base)):
            print 'test result does not exist for %s' % base
            cmds.append ('python test-lily/test-binary.py %s'
                         % os.path.abspath (bin))
            barf = 1

    if len (commitishes) > 1 or (len (commitishes) == 1
                                 and commitishes.keys()[0] != regularized_committish):
        print 'uploading multiple versions'
        print '\n'.join (`x` for x in commitishes.items ())
        print 'repo:', `regularized_committish`
        
    src_tarball = "uploads/lilypond-%(version_str)s.tar.gz" % locals ()
    src_tarball = os.path.abspath (src_tarball)
    
    if not os.path.exists (src_tarball):
        print "source tarball doesn't exist", src_tarball
        barf = True
    else:
        host = host_source_spec 
        majmin = '.'.join (['%d' % v for v in version[:2]])
        src_dests.append ((src_tarball, '%(host)s/sources/v%(majmin)s' % locals ()))
        
    test_cmd = r'''python %(cwd)s/test-lily/rsync-lily-doc.py \
  --upload %(host_doc_spec)s \
  --version-file %(lilybuild)s/out/VERSION \
  %(lilybuild)s/out-www/online-root/''' % d
    
    cmds.append (test_cmd)
    if tuple(version[:2]) > (2,10):
        test_cmd = r'''python %(cwd)s/test-lily/rsync-test.py \
  --upload %(host_test_spec)s \
  --version-file %(lilybuild)s/out/VERSION \
  %(lilybuild)s/out-www/online-root/''' % d
        cmds.append (test_cmd)

    cmds += ['rsync --delay-updates --progress %s %s'
             % tup for tup in src_dests]


    ## don't do cygwin .
    ##    cmds.append ("rsync -v --recursive --delay-updates --progress uploads/cygwin/release/ %(host_binaries_spec)s/cygwin/release/" % globals ())



    description = repo.git_pipe ('describe --abbrev=39 %(branch)s' % locals()).strip ()
    
    git_tag = 'release/%(version_str)s-%(build)d' % locals () 
    git_tag_cmd = 'git --git-dir downloads/lilypond.git tag -m ""  -a %(git_tag)s %(branch)s' % locals ()
    git_push_cmd = 'git --git-dir downloads/lilypond.git push ssh+git://git.sv.gnu.org/srv/git/lilypond.git/ refs/tags/%(git_tag)s:refs/tags/%(git_tag)s' % locals ()
    gub_tag_cmd = 'git tag "gub-release-lilypond-%(version_str)s-%(build)d" -m "release of lilypond %(description)s (%(version_str)s-%(build)d)" ' % locals()

    cmds.append (git_tag_cmd)
    cmds.append (git_push_cmd)

    cmds.append (gub_tag_cmd)
    cmds.append ('make -f lilypond.make update-versions')

    return cmds


def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage = """lilypondorg.py [OPTION]... COMMAND [PACKAGE]...

Commands:

upload x.y.z      - upload packages
"""
    
    p.description = 'look around on lilypond.org'

    p.add_option ('--url', action='store',
                  dest='url',
                  default=base_url,
                  help='select base url')

    p.add_option ('--branch', action='store',
                  dest='branch',
                  default='master',
                  help='select upload directory')

    p.add_option ('--execute', action='store_true',
                  dest='execute',
                  default=False,
                  help='execute the commands.')

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
    from gub import repository
    dir = options.repo_dir.replace ('.git','')
    repo = repository.Git (dir, 
                                     branch=options.branch)
    return repo

def main ():
    cli_parser = get_cli_parser ()
    (options, commands)  = cli_parser.parse_args ()

    global base_url, host_spec
    base_url = options.url
    host_spec = options.upload_host

    repo = get_repository (options)

    version_dict = misc.grok_sh_variables_str (repo.get_file_content ('VERSION'))
    version_tup = tuple (map (version_dict.get, ('MAJOR_VERSION', 'MINOR_VERSION', 'PATCH_LEVEL')))
    version_tup = tuple (map (int, version_tup))
    
    version_db = versiondb.VersionDataBase (options.version_db)
    cmds = upload_binaries (repo, version_tup, version_db)

    if options.execute:
        cmds = [c for c in cmds if 'test-binary' not in c]
        for cmd in cmds:
            system (cmd)
    else:
        print '\n\n'
        print '\n'.join (cmds);
        print '\n\n'

if __name__ == '__main__':
    main ()
