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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import md5
import os
import re
import sys
import time
import urllib

from gub import misc
from gub import locker
from gub import mirrors
from gub import oslog
from gub import tztime

class UnknownVcSystem (Exception):
    pass

class RepositoryException (Exception):
    pass

class RepositoryProxy:
    repositories = []
    def register (repository):
        RepositoryProxy.repositories.append (repository)
    register = staticmethod (register)

    def get_repository (dir, url, branch, revision):
        parameters = dict ()
        if url:
            url, parameters = misc.dissect_url (url)
            branch = parameters.get ('branch', branch)
            revision = parameters.get ('revision', revision)

            # FIXME/TODO: pass these nicely to create ()
            # possibly do dir,url,branch,revision also as dict or kwargs?
            module = parameters.get ('module', '')
            strip_components = parameters.get ('strip_components', 1)
            #patch = parameters.get ('patch')

        for i in RepositoryProxy.repositories:
            if i.check_url (i, url):
                return i.create (i, dir, url, branch, revision)
        file_p = 'file://'
        if url and url.startswith (file_p):
            url_dir = url[len (file_p):]
            for i in RepositoryProxy.repositories:
                if i.check_dir (i, url_dir):
                    # Duh, git says: fatal: I don't handle protocol 'file'
                    # return i.create (i, dir, url, branch, revision)
                    return i.create (i, dir, url_dir, branch, revision)
        for i in RepositoryProxy.repositories:
            if i.check_dir (i, dir):
                return i.create (i, dir, url, branch, revision)
        for i in RepositoryProxy.repositories:
            if i.check_suffix (i, url):
                return i.create (i, dir, url, branch, revision)
        for i in RepositoryProxy.repositories:
            if os.path.isdir (os.path.join (dir, '.gub' + i.vc_system)):
                d = misc.find_dirs (dir, '^' + i.vc_system)
                if d and i.check_dir (i, os.path.dirname (d[0])):
                    return i.create (i, dir, url, branch, revision)
        for i in RepositoryProxy.repositories:
            # FIXME: this is currently used to determine flavour of
            # downloads/lilypond.git.  But is is ugly and fragile;
            # what if I do brz branch foo foo.git?
            if i.check_suffix (i, dir):
                return i.create (i, dir, url, branch, revision)
        raise UnknownVcSystem ('Cannot determine source: url=%(url)s, dir=%(dir)s'
                           % locals ())
    get_repository = staticmethod (get_repository)

## Rename to Source/source.py?
class Repository: 
    vc_system = None
    tag_dateformat = '%Y-%m-%d_%H-%M-%S%z'

    def check_dir (rety, dir):
        return os.path.isdir (os.path.join (dir, rety.vc_system))
    check_dir = staticmethod (check_dir)

    def check_url (rety, url):
        vcs = rety.vc_system.replace ('_', '',).replace ('.', '').lower ()
        return url and (url.startswith (vcs + ':')
                        or url.startswith (vcs + '+'))
    check_url = staticmethod (check_url)

    def check_suffix (rety, url):
        return url and url.endswith (rety.vc_system)
    check_suffix = staticmethod (check_suffix)

    def create (rety, dir, source, branch='', revision=''):
        return rety (dir, source, branch, revision)
    create = staticmethod (create)

    def __init__ (self, dir, source):
        self.dir = os.path.normpath (dir)
        dir_vcs = self.dir + self.vc_system
        if not os.path.isdir (dir) and os.path.isdir (dir_vcs):
            # URG, Fixme, wtf?:
            sys.stderr.write('appending %s to checkout dir %s\n' % (self.vc_system, self.dir))
            self.dir = dir_vcs

        if not dir or dir == '.':
            dir = os.getcwd ()
            if os.path.isdir (os.path.join (dir, self.vc_system)):
                # Support user-checkouts: If we're already checked-out
                # HERE, use that as repository
                self.dir = dir
            else:
                # Otherwise, check fresh repository out under .gub.VC_SYSTEM
                self.dir = os.path.join (os.getcwd (), '.gub' + self.vc_system)
        self.source = source

        self.oslog = None
        # Fallbacks, this will go through oslog
        self.system = misc.system
        self._read_file = misc.read_file
        self.read_pipe = misc.read_pipe
        self.download_url = misc.download_url
        self.info = sys.stdout.write

    def set_oslog (self, oslog):
        # Fallbacks, this will go through oslog
        self.oslog = oslog
        self.system = oslog.system
        self._read_file = oslog.read_file
        self.read_pipe = oslog.read_pipe
        self.download_url = oslog.download_url
        self.info = oslog.info

    def canonical_branch (self):
        if self.is_tracking ():
            return self.branch.replace ('/', '-')
        return ''

    def file_name (self):
#        return re.sub ('.*/([^/]+)', '\\1', self.source)
        return os.path.basename (self.source)

    def download (self):
        pass

    def checksum (self):
        '''A checksum that characterizes the entire repository.

Typically a hash of all source files.'''

        return '0'

    def read_file (self, file_name):
        return ''

    def is_distributed (self):
        '''Whether repository is central or uses distributed repositories'''
        return True
    
    def is_tracking (self):
        '''Whether download will fetch newer versions if available'''
        return False
    
    def is_downloaded (self):
        '''Whether repository is available'''
        return False
    
    def update_workdir (self, destdir):
        '''Populate DESTDIR with sources of specified version/branch

Updating is preferably done by updating'''
        pass

    ## Version should be human-readable version.
    def version  (self):
        '''A human-readable revision number.

It need not be unique over revisions.'''
        return '0'

    def last_patch_date (self):
        '''Return timestamp of last patch'''
        return None

    def read_last_patch (self):
        '''Return a dict with info about the last patch'''
        return {'date': None, 'patch': None}

    def get_diff_from_tag (self, name):
        '''Return diff wrt to tag NAME'''
        None

    def get_diff_from_tag_base (self, name):
        '''Return diff wrt to last tag that starts with NAME'''
        tags = self.tag_list (name)
        tags.sort ()
        if tags:
            return self.get_diff_from_tag (tags[-1])
        return None

class TagDb:
    def __init__ (self, dir):
        import gdbm as dbmodule
        self.db = dbmodule.open (os.path.join (dir, 'tag.db'), 'c')
    def tag (self, name, repo):
        stamp = repo.last_patch_date ()
        if stamp:
            date = tztime.format (stamp)
            self.db[name + '-' + date] = date
    def tag_list (self, name):
        return map (lambda x: self.db[x], filter (lambda x: x.startswith (name),
                                                  self.db.keys ()))
    def get_diff_from_tag_base (self, name, repo):
        tags = self.tag_list (name)
        if tags:
            tags.sort ()
            return repo.get_diff_from_date (tztime.parse (tags[-1]))
        return None

class Version:
    def __init__ (self, version):
        self.dir = None
        self._version = version

    def download (self):
        pass

    def checksum (self):
        return self.version ()

    def is_tracking (self):
        return False

    def update_workdir (self, destdir):
        pass

    def version (self):
        return self._version

    def set_oslog (self, oslog):
        pass

#RepositoryProxy.register (Version)

class Darcs (Repository):
    vc_system = '_darcs'

    def create (rety, dir, source, branch='', revision=''):
        return Darcs (dir, source)
    create = staticmethod (create)
 
    def __init__ (self, dir, source=''):
        Repository.__init__ (self, dir, source)

    def darcs_pipe (self, cmd):
        dir = self.dir
        return self.read_pipe ('cd %(dir)s && darcs %(cmd)s' % locals ())

    def darcs (self, cmd):
        dir = self.dir
        return self.system ('cd %(dir)s && darcs %(cmd)s' % locals ())

    def get_revision_description (self):
        return self.darcs_pipe ('changes --last=1')
    
    def is_downloaded (self):
        return os.path.isdir (os.path.join (self.dir, self.vc_system))

    def download (self):
        source = self.source
        if not self.is_downloaded ():
            self.darcs ('pull -a %(source)s' % locals ())
        else:
            dir = self.dir
            self.system ('darcs get %(source)s %(dir)s' % locals ())
        
    def is_tracking (self):
        return True

    ## UGH.
    def xml_patch_name (self, patch):
        name_elts =  patch.getElementsByTagName ('name')
        try:
            return name_elts[0].childNodes[0].data
        except IndexError:
            return ''

    def checksum (self):
        import xml.dom.minidom
        xml_string = self.darcs_pipe ('changes --xml ')
        dom = xml.dom.minidom.parseString(xml_string)
        patches = dom.documentElement.getElementsByTagName('patch')
        patches = [p for p in patches if not re.match ('^TAG', self.xml_patch_name (p))]

        patches.sort ()
        release_hash = md5.new ()
        for p in patches:
            release_hash.update (p.toxml ())

        return release_hash.hexdigest ()        

    def update_workdir (self, destdir):
        self.system ('mkdir -p %(destdir)s' % locals ())
        dir = self.dir
        
        verbose = ''
        if self.oslog and self.oslog.verbose >= self.oslog.commands:
            verbose = 'v'
        vc_system = self.vc_system
        self.system ('rsync --exclude %(vc_system)s -a%(verbose)s %(dir)s/* %(destdir)s/' % locals())

    def read_file (self, file):
        dir = self.dir
        return self._read_file ('%(dir)s/%(file)s' % locals ())

RepositoryProxy.register (Darcs)
    
class TarBall (Repository):
    vc_system = '.tar'

    def create (rety, dir, source, branch='', revision=''):
        return TarBall (dir, source)
    create = staticmethod (create)

    def check_suffix (rety, url):
         return url and (url.endswith (rety.vc_system)
                         or url.endswith (rety.vc_system + '.gz')
                         or url.endswith (rety.vc_system + '.bz2')
                         # FIXME: DebianPackage should derive from TarBall,
                         # rather than extending it in place
                         or url.endswith ('.deb'))
    check_suffix = staticmethod (check_suffix)

    # TODO: s/url/source
    def __init__ (self, dir, url, version=None, strip_components=1):
        Repository.__init__ (self, dir, url)

        self.dir = dir
        if not os.path.isdir (self.dir):
            self.system ('mkdir -p %s' % self.dir)

        self._version = version
        if not version:
            #print misc.split_ball (url)
            x, v, f = misc.split_ball (url)
            self._version = '.'.join (map (str, v[:-1]))

        self.branch = None
        self.strip_components = strip_components
        
    def is_tracking (self):
        return False

    def _file_name (self):
        return re.search ('.*/([^/]+)$', self.source).group (1)
    
    def is_downloaded (self):
        name = os.path.join (self.dir, self._file_name  ())
        return os.path.exists (name)
    
    def download (self):
        if self.is_downloaded ():
            return
        self.download_url (self.source, self.dir)

    def checksum (self):
        from gub import misc
        return misc.ball_basename (self._file_name ())
    
    def update_workdir_deb (self, destdir):
        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)

        tarball = self.dir + '/' + self._file_name ()
        strip_components = self.strip_components
        self.system ('mkdir %s' % destdir)       
        _v = self.oslog.verbose_flag ()
        self.system ('ar p %(tarball)s data.tar.gz | tar -C %(destdir)s --strip-component=%(strip_components)d%(_v)s -zxf -' % locals ())
        
    def update_workdir_tarball (self, destdir):
        tarball = self.dir + '/' + self._file_name ()
        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)
        self.system ('mkdir %s' % destdir)       
        strip_components = self.strip_components
        _v = ''
        if self.oslog:  #urg, will be fixed when .source is mandatory
            _v = self.oslog.verbose_flag ()
        _z = misc.compression_flag (tarball)
        self.system ('tar -C %(destdir)s --strip-component=%(strip_components)d %(_v)s%(_z)s -xf %(tarball)s' % locals ())

    def update_workdir (self, destdir):
        if '.deb' in self._file_name () :
            self.update_workdir_deb (destdir)
        else:
            self.update_workdir_tarball (destdir)

    def version (self):
        from gub import misc
        return self._version

RepositoryProxy.register (TarBall)

class NewTarBall (TarBall):
    def __init__ (self, dir, mirror, name, ball_version, format='gz',
                  strip_components=1):
        TarBall.__init__ (self, dir, mirror % locals (), ball_version,
                          strip_components)

class Git (Repository):
    vc_system = '.git'
    patch_dateformat = '%a %b %d %H:%M:%S %Y %z'

    def __init__ (self, dir, source='', branch='', revision=''):
        Repository.__init__ (self, dir, source)

        self.checksums = {}
        self.local_branch = ''
        self.remote_branch = branch
        self.revision = revision

        self.repo_url_suffix = None
        if source:
            self.repo_url_suffix = re.sub ('.*://', '', source)

        if self.repo_url_suffix:
            # FIXME: logic copied foo times
            fileified_suffix = re.sub ('/', '-', self.repo_url_suffix)
            # FIXME: projection, where is this used?
            self.repo_url_suffix = '-' + re.sub ('[:+]+', '-', fileified_suffix)
        
        # FIXME: handle outside Git
        if ':' in branch:
            (self.remote_branch,
             self.local_branch) = tuple (branch.split (':'))

            self.local_branch = self.local_branch.replace ('/', '--')
            self.branch = self.local_branch
        elif source:
            self.branch = branch

            if branch:
                self.local_branch = branch + self.repo_url_suffix
                self.branch = self.local_branch
        else:
            self.branch = branch
            self.local_branch = branch

        # Wow, 15 lines of branch juggling.., what's going on here?
        # what if we just want to build a copy of
        # `git://git.kernel.org/pub/scm/git/git'.  Let's try `HEAD'
        if not self.local_branch:
            self.local_branch = 'HEAD'

    def version (self):
        return self.revision

    def is_tracking (self):
        return self.branch != ''
    
    def __repr__ (self):
        b = self.local_branch
        if not b:
            b = self.revision
        return '#<GitRepository %s#%s>' % (self.dir, b)

    def get_revision_description (self):
        return self.git_pipe ('log --max-count=1 %s' % self.local_branch)  

    def read_file (self, file_name):
        committish = self.git_pipe ('log --max-count=1 --pretty=oneline %(local_branch)s'
                                    % self.__dict__).split (' ')[0]
        m = re.search ('^tree ([0-9a-f]+)',
                       self.git_pipe ('cat-file commit %(committish)s'
                                      % locals ()))
        treeish = m.group (1)
        for f in self.git_pipe ('ls-tree -r %(treeish)s'
                                % locals ()).split ('\n'):
            (info, name) = f.split ('\t')
            (mode, type, fileish) = info.split (' ')
            if name == file_name:
                return self.git_pipe ('cat-file blob %(fileish)s ' % locals ())

        raise RepositoryException ('file not found')
        
    def get_branches (self):
        branch_lines = self.read_pipe (self.git_command ()
                                       + ' branch -l ').split ('\n')
        branches =  [b[2:] for b in branch_lines]
        return [b for b in branches if b]

    def git_command (self, dir, repo_dir):
        if repo_dir:
            repo_dir = '--git-dir %s' % repo_dir
        c = 'git %(repo_dir)s' % locals ()
        if dir:
            c = 'cd %s && %s' % (dir, c)
        return c
        
    def git (self, cmd, dir='', ignore_errors=False, repo_dir=''):
        if repo_dir == '' and dir == '':
            repo_dir = self.dir
        gc = self.git_command (dir, repo_dir)
        cmd = '%(gc)s %(cmd)s' % locals ()
        self.system (cmd, ignore_errors=ignore_errors)

    def git_pipe (self, cmd, ignore_errors=False, dir='', repo_dir=''):
        if repo_dir == '' and dir == '':
            repo_dir = self.dir
        gc = self.git_command (dir, repo_dir)
        return self.read_pipe ('%(gc)s %(cmd)s' % locals ())
        
    def is_downloaded (self):
        return os.path.isdir (self.dir)

    def download (self):
        repo = self.dir
        source = self.source
        revision = self.revision
        
        if not self.is_downloaded ():
            self.git ('--git-dir %(repo)s clone --bare -n %(source)s %(repo)s' % locals ())

            for (root, dirs, files) in os.walk ('%(repo)s/refs/heads/' % locals ()):
                for f in files:
                    self.system ('mv %s %s%s' % (os.path.join (root, f),
                                                 os.path.join (root, f),
                                                 self.repo_url_suffix))


                head = open ('%(repo)s/HEAD' % locals ()).read ()
                head = head.strip ()
                head += self.repo_url_suffix

                open ('%(repo)s/HEAD' % locals (), 'w').write (head)

            return

        if revision:
            contents = self.git_pipe ('ls-tree %(revision)s' % locals (),
                                      ignore_errors=True)

            if contents:
                return
            
            self.git ('--git-dir %(repo)s http-fetch -v -c %(revision)s' % locals ())

        refs = '%s:%s' % (self.remote_branch, self.branch)

        # FIXME: if source == None (for user checkouts), how to ask
        # git what parent url is?  `git info' does not work
        self.git ('fetch --update-head-ok %(source)s %(refs)s ' % locals ())
        self.checksums = {}

    def checksum (self):
        if self.revision:
            return self.revision
        
        branch = self.local_branch
        if self.checksums.has_key (branch):
            return self.checksums[branch]

        repo_dir = self.dir
        if os.path.isdir (repo_dir):
            ## can't use describe: fails in absence of tags.
            cs = self.git_pipe ('rev-list  --max-count=1 %(branch)s' % locals ())
            cs = cs.strip ()
            self.checksums[branch] = cs
            return cs
        else:
            return 'invalid'

    def all_files (self):
        branch = self.branch
        str = self.git_pipe ('ls-tree --name-only -r %(branch)s' % locals ())
        return str.split ('\n')

    def update_workdir (self, destdir):
        repo_dir = self.dir
        branch = self.local_branch
        revision = self.revision
        
        if os.path.isdir (os.path.join (destdir, self.vc_system)):
            self.git ('reset --hard HEAD' % locals (), dir=destdir)
            self.git ('pull %(repo_dir)s %(branch)s:' % locals (), dir=destdir)
        else:
            self.system ('git-clone -l -s %(repo_dir)s %(destdir)s' % locals ())
            try:
                ## We always want to use 'master' in the checkout,
                ## Since the branch name of the clone is
                ## unpredictable, we force it here.
                os.unlink ('%(destdir)s/.git/refs/heads/master' % locals ())
            except OSError:
                pass

            if not revision:
                revision = 'origin/%(branch)s' % locals ()
            
            self.git ('branch master %(revision)s' % locals (),
                      dir=destdir)
            self.git ('checkout master', dir=destdir)

    def get_diff_from_tag (self, tag):
        return self.git_pipe ('diff %(tag)s HEAD' % locals ())

    def last_patch_date (self):
        # Whurg.  Because we use the complex non-standard and silly --git-dir
        # option, we cannot use git log without supplying a branch, which
        # is not documented in git log, btw.
        # fatal: bad default revision 'HEAD'
        # I'm not even sure if we need branch or local_branch... and why
        # our branch names are so difficult master-git.sv.gnu.org-lilypond.git
        branch = self.branch
        s = self.git_pipe ('log -1 %(branch)s' % locals ())
        m = re.search  ('Date: *(.*)', s)
        date = m.group (1)
        return tztime.parse (date, self.patch_dateformat)

    def tag (self, name):
        stamp = self.last_patch_date ()
        tag = name + '-' + tztime.format (stamp, self.tag_dateformat)
        # See last_patch_date
        # fatal: Failed to resolve 'HEAD' as a valid ref.
        branch = self.branch
        self.git ('tag %(tag)s %(branch)s' % locals ())
        return tag

    def tag_list (self, tag):
        return self.git_pipe ('tag -l %(tag)s*' % locals ()).split ('\n')

#RepositoryProxy.register (Git)

class CVS (Repository):
    vc_system = 'CVS'
    cvs_entries_line = re.compile ('^/([^/]*)/([^/]*)/([^/]*)/([^/]*)/')

    def create (rety, dir, source, branch='', revision=''):
        if not branch:
            branch='HEAD'
        source = source.replace ('cvs::pserver', ':pserver')
        p = source.rfind ('/')
        return CVS (dir, source=source, module=source[p+1:], tag=branch)
    create = staticmethod (create)

    def __init__ (self, dir, source='', module='', tag='HEAD'):
        Repository.__init__ (self, dir, source)
        self.module = module
        self.checksums = {}
        self.source = source
        self.tag = tag
        self.branch = tag # for vc_version_suffix

        branch_dir = os.path.join (self.dir, tag)
        if not os.path.isdir (branch_dir):
            self.system ('mkdir -p %s' % branch_dir)
            
    def _checkout_dir (self):
        return '%s/%s' % (self.dir, self.tag)

    def is_distributed (self):
        return False

    def is_tracking (self):
        return True ##FIXME

    def get_revision_description (self):
        try:
            contents = read_file ('ChangeLog')
            entry_regex = re.compile ('\n([0-9])')
            entries = entry_regex.split (contents)
            descr = entries[0]
            
            changelog_rev = ''
            
            for (name, version, date, dontknow) in self.cvs_entries (self.dir + '/CVS'):
                if name == 'ChangeLog':
                    changelog_rev  = version
                    break

            return ('ChangeLog rev %(changelog_rev)s\n%(description)s' %
                    locals ())
        
        except IOError:
            return ''

    def checksum (self):
        if self.checksums.has_key (self.tag):
            return self.checksums[self.tag]
        
        file = '%s/%s/.vc-checksum' % (self.dir, self.tag)

        if os.path.exists (file):
            cs = open (file).read ()
            self.checksums[self.tag] = cs
            return cs
        else:
            return '0'
        
    def read_file (self, file_name):
        return open (self._checkout_dir () + '/' + file_name).read ()
        
    def read_cvs_entries (self, dir):
        checksum = md5.md5()

        latest_stamp = 0
        for d in self.cvs_dirs (dir):
            for e in self.cvs_entries (d):
                (name, version, date, dontknow) = e
                checksum.update (name + ':' + version)

                if date == 'Result of merge':
                    raise Exception ("repository has been altered")
                
                stamp = time.mktime (time.strptime (date))
                latest_stamp = max (stamp, latest_stamp)

        version_checksum = checksum.hexdigest ()
        time_stamp = latest_stamp

        return (version_checksum, time_stamp)
    
    def update_workdir (self, destdir):
        dir = self._checkout_dir ()
        ## TODO: can we get deletes from vc?
        verbose = ''
        if self.oslog and self.oslog.verbose >= oslog.level['command']:
            verbose = 'v'
        self.system ('rsync -a%(verbose)s --delete --exclude CVS %(dir)s/ %(destdir)s' % locals ())
        
    def is_downloaded (self):
        dir = self._checkout_dir ()
        return os.path.isdir (dir + '/CVS')

    def download (self):
        suffix = self.tag
        rev_opt = '-r ' + self.tag
        source = self.source
        dir = self._checkout_dir ()
        lock_dir = locker.Locker (dir + '.lock')
        module = self.module
        cmd = ''
        if self.is_downloaded ():
            cmd += 'cd %(dir)s && cvs -q up -dCAP %(rev_opt)s' % locals()
        else:
            repo_dir = self.dir
            cmd += 'cd %(repo_dir)s/ && cvs -d %(source)s -q co -d %(suffix)s %(rev_opt)s %(module)s''' % locals ()

        self.system (cmd)

        (cs, stamp) = self.read_cvs_entries (dir)

        open (dir + '/.vc-checksum', 'w').write (cs)
        open (dir + '/.vc-timestamp', 'w').write ('%d' % stamp)
        
    def cvs_dirs (self, branch_dir):
        retval =  []
        for (base, dirs, files) in os.walk (branch_dir):
            retval += [os.path.join (base, d) for d in dirs
                       if d == 'CVS']
            
        return retval

    def cvs_entries (self, dir):
        entries_str =  open (os.path.join (dir, 'Entries')).read ()

        entries = []
        for e in entries_str.split ('\n'):
            m = self.cvs_entries_line.match (e)
            if m:
                entries.append (tuple (m.groups ()))
        return entries
        
    def all_cvs_entries (self, dir):
        ds = self.cvs_dirs (dir)
        es = []
        for d in ds:
            ## strip CVS/
            basedir = os.path.split (d)[0]
            for e in self.cvs_entries (d):
                file_name = os.path.join (basedir, e[0])
                file_name = file_name.replace (self.dir + '/', '')

                es.append ((file_name,) + e[1:])
        return es

    def all_files (self, branch):
        entries = self.all_cvs_entries (self.dir + '/' + branch)
        return [e[0] for e in entries]
    
RepositoryProxy.register (CVS)

# FIXME: why are cvs, darcs, git so complicated?
class SimpleRepo (Repository):
    def __init__ (self, dir, source, branch, revision='HEAD'):
        Repository.__init__ (self, dir, source)
        self.source = source
        self.revision = revision
        self.branch = branch
        if not os.path.isdir (self.dir):
            self.system ('mkdir -p %(dir)s' % self.__dict__)
        if not source:
            self.source, self.branch = self._source ()

    def is_tracking (self):
        ## FIXME, probably wrong.
        return (not self.revision or self.revision == 'HEAD')

    def update_workdir (self, destdir):
        dir = self._checkout_dir ()
        self._copy_working_dir (dir, destdir)

    def is_downloaded (self):
        dir = self._checkout_dir ()
        return os.path.isdir (os.path.join (dir, self.vc_system))

    def download (self):
        if not self.is_downloaded ():
            self._checkout ()
        elif self._current_revision () != self.revision:
            self._update (self.revision)
        self.info ('downloaded version: ' + self.version () + '\n')

    def _copy_working_dir (self, dir, copy):
        vc_system = self.vc_system
        verbose = ''

        if self.oslog and self.oslog.verbose >= oslog.level['command']:
            verbose = 'v'
        self.system ('rsync -a%(verbose)s --exclude %(vc_system)s %(dir)s/ %(copy)s'
                     % locals ())

    def _checkout_dir (self):
        # Support user-check-outs
        if os.path.isdir (os.path.join (self.dir, self.vc_system)):
            return self.dir
        dir = self.dir
        branch = self.branch
        module = self.module
        revision = self.revision
        return '%(dir)s/%(branch)s/%(module)s/%(revision)s' % locals ()

    def read_file (self, file_name):
        return self._read_file (self._checkout_dir () + '/' + file_name)

    def checksum (self):
        return self._current_revision ()

    def version (self):
        return ('-'.join ([self.branch, self.revision])
                .replace ('/', '-')
                .replace ('.-', '')
                .replace ('--', '-'))

class Subversion (SimpleRepo):
    vc_system = '.svn'
    patch_dateformat = '%Y-%m-%d %H:%M:%S %z'
    diff_xmldateformat = '%Y-%m-%d %H:%M:%S.999999'
    patch_xmldateformat = '%Y-%m-%dT%H:%M:%S'

    def create (rety, dir, source, branch, revision='HEAD'):
        source = source.replace ('svn:http://', 'http://')
        if not branch:
            branch = '.'
        if not revision:
            revision = 'HEAD'
        return Subversion (dir, source=source, branch=branch,
                           module='.', revision=revision)
    create = staticmethod (create)

    def __init__ (self, dir, source=None, branch='.', module='.', revision='HEAD'):
        if not revision:
            revision = 'HEAD'
        self.module = module
        SimpleRepo.__init__ (self, dir, source, branch, revision)

    def is_distributed (self):
        return False

    def _current_revision (self):
        return self.revision
        dir = self._checkout_dir ()
        ## UGH: should not parse user oriented output
        revno = self.read_pipe ('cd %(dir)s && LANG= svn log --limit=1'
                                % locals ())
        m = re.search  ('-+\nr([0-9]+) |', revno)
        assert m
        return m.group (1)
        
    def _checkout (self):
        dir = self.dir
        source = self.source
        branch = self.branch
        module = self.module
        revision = self.revision
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(dir)s && svn co %(rev_opt)s %(source)s/%(branch)s/%(module)s %(branch)s/%(module)s/%(revision)s''' % locals ()
        self.system (cmd)
        
    def _update (self, revision):
        dir = self._checkout_dir ()
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(dir)s && svn up %(rev_opt)s' % locals ()
        self.system (cmd)

    def get_revision_description (self):
        dir = self._checkout_dir ()
        return self.read_pipe ('cd %(dir)s && LANG= svn log --verbose --limit=1'
                               % locals ())

    def get_diff_from_tag (self, tag):
        dir = self._checkout_dir ()
        source = self.source
        branch = self.branch
        module = self.module
        root = self._root ()
        return self.read_pipe ('cd %(dir)s && LANG= svn diff %(root)s/tags/%(tag)s %(source)s/%(branch)s/%(module)s' % locals ())

    # FIXME: use from_revision?  how to do play nicely with TagDb
    def get_diff_from_date (self, stamp):
#        date = tztime.format (stamp, self.patch_dateformat)
        date = tztime.format (stamp, self.diff_xmldateformat)
        dir = self._checkout_dir ()
        source = self.source
        branch = self.branch
        module = self.module
        root = self._root ()
        return self.read_pipe ('cd %(dir)s && TZ= LANG= svn diff -r "{%(date)s}"' % locals ())

    def _root (self):
        dir = self._checkout_dir ()
        ## UGH: should not parse user oriented output
        root = self.read_pipe ('cd %(dir)s && LANG= svn info' % locals ())
        m = re.search  ('.*Root: (.*)', root)
        assert m
        return m.group (1)

    def _source (self):
        dir = self._checkout_dir ()
        ## UGH: should not parse user oriented output
        s = self.read_pipe ('cd %(dir)s && LANG= svn info' % locals ())
        m = re.search  ('.*URL: (.*)', s)
        source = m.group (1)
        m = re.search  ('.*Repository Root: (.*)', s)
        root = m.group (1)
        assert source.startswith (root)
        branch = source[len (root)+1:]
        return root, branch

    def last_patch_date (self):
        dir = self._checkout_dir ()
        s = self.read_pipe ('cd %(dir)s && LANG= svn log --limit=1 --xml' % locals ())
#        m = re.search  ('Last Changed Date: (.*) \(', s)
        m = re.search  ('<date>(.*)\.[0-9]{6}Z</date>', s)
        date = m.group (1)
        return tztime.parse (date, self.patch_xmldateformat)
        
    def tag (self, name):
        source = self.source
        branch = self.branch
        module = self.module
        revision = self.revision
        rev_opt = '-r %(revision)s ' % locals ()
        stamp = self.last_patch_date ()
        tag = name + '-' + tztime.format (stamp, self.tag_dateformat)
        root = self._root ()
        self.system ('svn cp -m "" %(rev_opt)s %(source)s/%(branch)s/%(module)s %(root)s/tags/%(tag)s''' % locals ())
        return tag

    def tag_list (self, tag):
        root = self._root ()
        lst = self.read_pipe ('LANG= svn ls %(root)s/tags' % locals ()).split (\
'\n')
        return filter (lambda x: x.startswith (tag), lst)

RepositoryProxy.register (Subversion)

class Bazaar (SimpleRepo):
    vc_system = '.bzr'

    def create (rety, dir, source, branch='', revision=''):
        return Bazaar (dir, source=source, revision=revision)
    create = staticmethod (create)

    def __init__ (self, dir, source, revision='HEAD'):
        # FIXME: multi-branch repos not supported for now
        if not revision:
            revision = '0'
        self.module = '.'
        SimpleRepo.__init__ (self, dir, source, '.', revision)

    def _current_revision (self):
        try:
            revno = self.bzr_pipe ('revno' % locals ())
        except:
            # FIXME: there's something nasty wrt version numbers, gub
            # wants to know about version before it downloads a repo.
            self.download ()
            revno = self.bzr_pipe ('revno' % locals ())
        assert revno
        return revno[:-1]

    def _checkout (self):
        dir = self.dir
        source = self.source
        revision = self.revision
        rev_opt = '-r %(revision)s ' % locals ()
        self.system ('''cd %(dir)s && bzr branch %(rev_opt)s %(source)s %(revision)s'''
                         % locals ())
        
    def _update (self, revision):
        rev_opt = '-r %(revision)s ' % locals ()
        source = self.source
        if not source:
            source = ''
        self.bzr_system ('pull %(rev_opt)s %(source)s' % locals ())

    def bzr_pipe (self, cmd):
        dir = self._checkout_dir ()
        return self.read_pipe ('cd %(dir)s && bzr %(cmd)s' % locals ())

    def bzr_system (self, cmd):
        dir = self._checkout_dir ()
        return self.system ('cd %(dir)s && bzr %(cmd)s' % locals ())

    def get_revision_description (self):
        return self.bzr_pipe ('log --verbose -r-1')

RepositoryProxy.register (Bazaar)

# class Git does not survive serialization and it is just too weird
# and complex
class SimpleGit (SimpleRepo):
    vc_system = '.git'
    patch_dateformat = '%a %b %d %H:%M:%S %Y %z'

    def __init__ (self, dir, source='', branch='master', revision='HEAD'):
        # FIXME: multi-branch repos not supported for now
        if not revision:
            revision = 'HEAD'
        if not branch:
            branch = 'master'
        self.module = '.'

        # FIXME: keep (silly?) local-branch-name-juggling for compat reasons
        # FIXME: handle outside Git
        if ':' in branch:
            (branch,
             self.local_branch) = tuple (branch.split (':'))
            self.local_branch = self.local_branch.replace ('/', '--')

        SimpleRepo.__init__ (self, dir, source, branch, revision)

    def git_pipe (self, cmd):
        dir = self._checkout_dir ()
        return self.read_pipe ('cd %(dir)s && git %(cmd)s' % locals ())

    def git_system (self, cmd):
        dir = self._checkout_dir ()
        return self.system ('cd %(dir)s && git %(cmd)s' % locals ())

    def _source (self):
        return 'TODO:read url from git info', self.branch

    def _current_revision (self):
        return self.revision

    def _checkout (self):
        dir = self.dir
        source = self.source
        base = self._checkout_dir ()
        self.system ('cd %(dir)s && git clone %(source)s %(base)s' % locals ())
        # FIXME: keep (silly?) local-branch-name-juggling for compat reasons
        branch = self.branch
        if self.revision:
            branch = self.revision
        elif self.local_branch:
            self.git_system ('checkout %(branch)s' % locals ())
            branch = self.local_branch
            self.git_system ('branch %(branch)s' % locals ())
        # end FIXME
        self.git_system ('checkout %(branch)s' % locals ())

    def _update (self, revision):
        self.git_system ('pull')

    def update_workdir (self, destdir):
        # FIXME: keep (silly?) local-branch-name-juggling for compat reasons
        branch = self.branch
        if self.revision:
            branch = self.revision
        elif self.local_branch:
            self.git_system ('checkout %(branch)s' % locals ())
            branch = self.local_branch
            self.git_system ('branch %(branch)s' % locals ())
        # end FIXME
        self.git_system ('checkout %(branch)s' % locals ())
        SimpleRepo.update_workdir (self, destdir)

    def get_revision_description (self):
        return self.git_pipe ('log --verbose -1')

    def get_diff_from_tag (self, tag):
        return self.git_pipe ('diff %(tag)s' % locals ())

    def last_patch_date (self):
        s = self.git_pipe ('log -1' % locals ())
        m = re.search  ('Date: *(.*)', s)
        date = m.group (1)
        return tztime.parse (date, self.patch_dateformat)

    def tag (self, name):
        stamp = self.last_patch_date ()
        tag = name + '-' + tztime.format (stamp, self.tag_dateformat)
        self.git_system ('tag %(tag)s' % locals ())
        return tag

    def tag_list (self, tag):
        return self.git_pipe ('tag -l %(tag)s*' % locals ()).split ('\n')

    def all_files (self):
        branch = self.branch
        str = self.git_pipe ('ls-tree --name-only -r %(branch)s' % locals ())
        return str.split ('\n')

Git = SimpleGit
RepositoryProxy.register (Git)

get_repository_proxy = RepositoryProxy.get_repository

def test ():
    import unittest

    for i in RepositoryProxy.repositories:
        print i, i.vc_system

    # This is not a unittest, it only serves as a smoke test mainly as
    # an aid to get rid safely of the global non-oo repository_proxy
    # stuff
    global get_repository_proxy

    class Test_get_repository_proxy (unittest.TestCase):
        def setUp (self):
            os.system ('rm -rf downloads/test')
        def testCVS (self):
            repo = get_repository_proxy ('downloads/test/', 'cvs::pserver:anonymous@cvs.savannah.gnu.org:/sources/emacs', '', '')
            self.assertEqual (repo.__class__, CVS)
        def testTarBall (self):
            repo = get_repository_proxy ('downloads/test/', 'http://ftp.gnu.org/pub/gnu/hello/hello-2.3.tar.gz', '', '')
            self.assertEqual (repo.__class__, TarBall)
        def testGit (self):
            repo = get_repository_proxy ('downloads/test/', 'git://git.kernel.org/pub/scm/git/git', '', '')
            self.assertEqual (repo.__class__, Git)
        def testLocalGit (self):
            os.system ('mkdir -p downloads/test/git')
            os.system ('cd downloads/test/git && git init')
            repo = get_repository_proxy ('downloads/test/', 'file://' + os.getcwd () + '/downloads/test/git', '', '')
            self.assertEqual (repo.__class__, Git)
        def testBazaar (self):
            repo = get_repository_proxy ('downloads/test/', 'bzr:http://bazaar.launchpad.net/~yaffut/yaffut/yaffut.bzr', '', '')
            self.assertEqual (repo.__class__, Bazaar)
        def testBazaarGub (self):
            os.system ('mkdir -p downloads/test/bzr')
            cwd = os.getcwd ()
            os.chdir ('downloads/test/bzr')
            repo = get_repository_proxy ('.', 'bzr:http://bazaar.launchpad.net/~yaffut/yaffut/yaffut.bzr', '', '')
            self.assert_ (os.path.isdir ('.gub.bzr'))
            os.chdir (cwd)
        def testGitSuffix (self):
            # FIXME: this is currently used to determine flavour of
            # downloads/lilypond.git.  But is is ugly and fragile;
            # what if I do brz branch foo foo.git?

            # This is now broken, with SimpleGit; good riddance
            pass
# #            repo = get_repository_proxy ('/foo/bar/barf/i-do-not-exist-or-possibly-am-of-bzr-flavour.git', '', '', '')
# #            self.assertEqual (repo.__class__, Git)
        def testPlusSsh (self):
            repo = get_repository_proxy ('downloads/test/', 'bzr+ssh://bazaar.launchpad.net/~yaffut/yaffut/yaffut.bzr', '', '')
            self.assertEqual (repo.__class__, Bazaar)
            repo = get_repository_proxy ('downloads/test/', 'git+ssh://git.sv.gnu.org/srv/git/lilypond.git', '', '')
            self.assertEqual (repo.__class__, Git)
            repo = get_repository_proxy ('downloads/test/', 'svn+ssh://gforge/svnroot/public/samco/trunk', '', '')
            self.assertEqual (repo.__class__, Subversion)
        def testGitTagAndDiff (self):
            os.system ('mkdir -p downloads/test/git')
            os.system ('cd downloads/test/git && git init')
# # FIXME Git/SimpleGit mixup: git-dir vs checkout-dir
# #           repo = Git (os.getcwd () + '/downloads/test/git/.git')
            repo = Git (os.getcwd () + '/downloads/test/git/')
            os.system ('cd downloads/test/git && echo one >> README')
            os.system ('cd downloads/test/git && git add .')
            os.system ('cd downloads/test/git && git commit -m "1"')
            time.sleep (1)
            repo.tag ('success-test')
            os.system ('cd downloads/test/git && echo two >> README')
            os.system ('cd downloads/test/git && git add .')
            os.system ('cd downloads/test/git && git commit -m "2"')
            repo.tag ('success-test')
            os.system ('cd downloads/test/git && echo three >> README')
            os.system ('cd downloads/test/git && git add .')
            os.system ('cd downloads/test/git && git commit -m "3"')
            patch = '''
@@ -1,2 +1,3 @@
 one
 two
+three
'''
            diff = repo.get_diff_from_tag_base ('success-test')
            self.assert_ (diff.find (patch) >=0)
        def testSnvTagAndDiff (self):
            os.system ('mkdir -p downloads/test/svn')
            os.system ('cd downloads/test/svn && svnadmin create .repo')
            os.system ('cd downloads/test/svn && svn co file://localhost$(pwd)/.repo root')
            repo = Subversion (os.getcwd () + '/downloads/test/svn/root')
            tag_db = TagDb ('downloads/test')
            os.system ('cd downloads/test/svn/root && mkdir trunk tags')
            os.system ('cd downloads/test/svn/root && svn add trunk tags')
            os.system ('cd downloads/test/svn/root && svn commit -m "init"')
            os.system ('cd downloads/test/svn && svn co file://localhost$(pwd)/.repo/trunk trunk')
            repo = Subversion (os.getcwd () + '/downloads/test/svn/trunk')
            os.system ('cd downloads/test/svn/trunk && echo one >> README')
            os.system ('cd downloads/test/svn/trunk && svn add README')
            os.system ('cd downloads/test/svn/trunk && svn commit -m "1"')
            os.system ('cd downloads/test/svn/trunk && svn up')
            repo.tag ('success-test')
            tag_db.tag ('success-test', repo)
            os.system ('cd downloads/test/svn/trunk && echo two >> README')
            os.system ('cd downloads/test/svn/trunk && svn commit -m "2"')
            os.system ('cd downloads/test/svn/trunk && svn up')
            os.system ('cd downloads/test/svn/trunk && svn info > info')
            repo.tag ('success-test')
            tag_db.tag ('success-test', repo)
            os.system ('cd downloads/test/svn/trunk && echo three >> README')
            os.system ('cd downloads/test/svn/trunk && svn commit -m "3"')
            patch = '''
@@ -1,2 +1,3 @@
 one
 two
+three
'''
            diff = repo.get_diff_from_tag_base ('success-test')
            self.assert_ (diff.find (patch) >=0)
            diff = tag_db.get_diff_from_tag_base ('success-test', repo)
            self.assert_ (diff.find (patch) >=0)

    suite = unittest.makeSuite (Test_get_repository_proxy)
    unittest.TextTestRunner (verbosity=2).run (suite)

if __name__ == '__main__':
    test ()
