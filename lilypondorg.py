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

platforms = ['linux-x86',
             'linux-64',
             'darwin-ppc',
             'darwin-x86',
             'documentation',
             'freebsd-x86',
#             'freebsd6-x86',
#             'linux-arm',
             'mingw']


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

    'mingw':'exe',

    'documentation': 'tar.bz2',
    }

def system (c):
    print c
    if os.system (c):
        raise 'barf'

def get_url_versions (url):
    opener = urllib.URLopener ()
    index = opener.open (url).read ()

    versions = []
    def note_version (m):
        version = tuple (map (string.atoi,  m.group (1).split('.')))
        build = 0
        build_url = url + re.sub ("HREF=", '', m.group (0))
        build_url = build_url.replace ('"', "")
        
        # disregard buildnumber for src tarball. 
        if m.group(2):
            build = string.atoi (m.group (2))
        versions.append ((version, build, build_url))
        
        return ''

    re.sub (r'HREF="lilypond-([0-9.]+)-?([0-9]+)?\.[0-9a-z-]+\.[.0-9a-z-]+"', note_version, index)
    
    return versions
    

def get_versions (platform):
    url = base_url
    return get_url_versions ('%(url)s/binaries/%(platform)s/'
                             % locals ())

def get_src_versions (maj_min_version):
    (maj_version, min_version) = maj_min_version
    url = base_url
    return get_url_versions ('%(url)s/v%(maj_version)d.%(min_version)d/' %  locals())

def get_max_builds (platform):
    vs = get_versions (platform)

    builds = {}
    for (version, build, url) in vs:
        if builds.has_key (version):
            build = max (build, builds[version][0])

        builds[version] = (build, url)

    return builds
    
def max_branch_version_build_url (branch, platform):
    vbs = get_versions (platform)

    vs = [v for (v,b,u) in vbs if v[0:2] == branch]
    vs.sort()
    try:
        max_version = vs[-1]
    except IndexError:
        max_version = (0,0,0)
        
    max_b = 0
    max_url = ''
    for (v, b, url) in get_versions (platform):
        if v == max_version:
            max_b = max (b, max_b)
            max_url = url

    return (max_version, max_b, max_url)

def max_version_build (platform):
    vbs = get_versions (platform)
    vs = [v for (v,b,u) in vbs]
    vs.sort()
    max_version = vs[-1]

    max_b = 0
    for (v,b,u) in get_versions (platform):
        if v == max_version:
            max_b = max (b, max_b)

    return (max_version, max_b)

def max_src_version_url (maj_min):
    vs = get_src_versions (maj_min)
    vs.sort()
    try:
        return (vs[-1][0], vs[-1][2])
    except:
        ## don't crash.
        return maj_min + (-1,)

def uploaded_build_number (version):
    platform_versions = {}
    build = 0
    for p in platforms:
        vs = get_max_builds (p)
        if vs.has_key (version):
            build = max (build, vs[version][0])

    return build

def upload_binaries (repo, version):
    build = uploaded_build_number (version) + 1
    version_str = '.'.join (['%d' % v for v in version])
    branch = 'HEAD'
    if (version[1] % 2) == 0:
        branch = 'lilypond_%d_%d' % (version[0], version[1])


    src_dests = []
    cmds = []

#    committish = repo.git_pipe ('log --max-count=1')
#    committish = re.search ('commit[ \t]+(.*)\n', committish).group (1) 
    
    committish = repo.git_pipe ('describe --abbrev=24')
    commitishes = {}
    barf = False
    for platform in platforms:
        format = formats[platform]
        
        base = 'lilypond-%(version_str)s-%(build)d.%(platform)s.%(format)s' % locals()
        bin = 'uploads/%(base)s' % locals()
        
        if not os.path.exists (bin):
            print 'binary does not exist', bin
            barf = 1
            
        else:
            ## globals -> locals.
            host = host_binaries_spec 
            src_dests.append((os.path.abspath (bin), '%(host)s/%(platform)s' % locals()))
            
        try:
            branch = 'origin'
            hdr = pickle.load (open ('uploads/%(platform)s/lilypond-%(branch)s.%(platform)s.hdr' % locals ()))
            key = hdr['source_checksum']
            
            lst = commitishes.get (key, [])
            lst.append (platform)
            
            commitishes[key] = lst
        except IOError:
            pass
        
        if (platform <> 'documentation'
            and  not os.path.exists ('log/%s.test.pdf' % base)):
            print 'test result does not exist for %s' % base
            cmds.append ('python test-lily/test-binary.py %s' % os.path.abspath (bin))
            
            barf = 1

        
    if len (commitishes) > 1 or commitishes.keys()[0] != committish:
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
        src_dests.append ((src_tarball, '%(host)s/v%(majmin)s' % locals ()) )
        


    d = globals().copy()
    d.update (locals())

    d['cwd'] = os.getcwd ()
    d['lilybuild'] = d['cwd'] + '/target/%(build_platform)s/build/lilypond-%(branch)s' % d
    d['lilysrc'] = d['cwd'] + '/target/%(build_platform)s/src/lilypond-%(branch)s' % d 
    
    test_cmd =r'''python %(cwd)s/test-lily/rsync-lily-doc.py \
  --upload %(host_doc_spec)s \
  %(lilybuild)s/out-www/web-root/''' % d
    
    cmds.append (test_cmd)

    cmds += ['rsync --delay-updates --progress %s %s' % tup for tup in src_dests]

    description = repo.git_pipe ('describe --abbrev=36')

    darcs_tag_cmd = 'darcs tag --patch "release %(version_str)s-%(build)d of committish %(description)s' % locals()
    git_tag_cmd = 'git --git-dir downloads/lilypond.git tag gub-%(version_str)s-%(build)d %(branch)s' % locals ()

    cmds.append (darcs_tag_cmd)
    cmds.append (git_tag_cmd)
    
    print '\n\n'
    print '\n'.join (cmds);
    print '\n\n'
    if barf:
        raise Exception ('barf')

    for cmd in cmds:
        system (cmd)

def read_build_versions ():
    branches = [(2,9), (2,8), (2,6)]
    version_builds = {}
    
    for branch in branches:
        branch_str = 'v' + '.'.join (['%d' % vc for vc in branch])
    
        for p in platforms:
            (v, b, url) = max_branch_version_build_url (branch, p)
        
            v = '.'.join (['%d' % vc for vc in v])
            version_builds[branch_str + '-' + p] = ('%s-%d' % (v,b), url)

        (version, url) =  max_src_version_url (branch)
        version_builds[branch_str + '-source'] = ('.'.join (['%d' % vc for vc in version]),
                                                  url)
    return version_builds

def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage="""lilypondorg.py [OPTION]... COMMAND [PACKAGE]...

Commands:

upload x.y.z      - upload packages
nextbuild x.y.z   - get next build number

"""
    p.description='look around on lilypond.org'

    p.add_option ('', '--url', action='store',
                  dest='url',
                  default=base_url,
                  help='select base url')

    
    p.add_option ('', '--branch', action='store',
                  dest='branch',
                  default='origin',
                  help='select upload directory')
    
    p.add_option ('', '--repo-dir', action='store',
                  dest='repo_dir',
                  default='downloads/lilypond.git',
                  help='select repository directory')
    
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

    command = commands[0]
    commands = commands[1:]

    
    if command == 'nextbuild':
        version = tuple (map (string.atoi, commands[0].split ('.')))
        print uploaded_build_number (version) + 1
    elif command == 'upload':
        repo = get_repository (options)
        version = tuple (map (string.atoi, commands[0].split ('.')))
        upload_binaries (repo, version)
    elif command == 'versions':
        d = read_build_versions ()
        for k in sorted(d.keys ()):
            print k, d[k] 
    else:
        base_url = "http://download.linuxaudio.org/lilypond"
        print max_src_version_url ((2,9))
        print max_version_build ('documentation')
        print max_branch_version_build_url ((2, 6), 'linux-x86')
        print max_branch_version_build_url ((2, 9), 'linux-x86')


if __name__ == '__main__':
    main()
        
