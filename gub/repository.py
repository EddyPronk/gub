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

import os
import re
import md5
import time
import urllib

from gub import misc
from gub import locker
from gub import mirrors

## Rename to Source/source.py?

class Repository: 
    def __init__ (self, dir, vcs, source):
        self.vcs = vcs
        self.dir = os.path.normpath (dir) + self.vcs

        if not dir or dir == '.':
            dir = os.getcwd ()
            if os.path.isdir (os.path.join (dir, self.vcs)):
                # Support user-checkouts: If we're already checked-out
                # HERE, use that as repository
                self.dir = dir
            else:
                # Otherwise, check fresh repository out under .VCS
                self.dir = os.path.join (os.getcwd (), self.vcs)
        self .source = source

        self.oslog = None
        # Fallbacks, this will go through oslog
        self.system = misc.system
        self.read_pipe = misc.read_pipe
        self.download_url = misc.download_url

    def set_oslog (self, oslog):
        # Fallbacks, this will go through oslog
        self.oslog = oslog
        self.system = oslog.system
        self.read_pipe = oslog.read_pipe
        self.download_url = oslog.download_url

    def download (self):
        pass

    def get_checksum (self):
        """A checksum that characterizes the entire repository.
        Typically a hash of all source files."""

        return '0'

    def get_file_content (self, file_name):
        return ''

    def is_tracking (self):
        "Whether download will fetch newer versions if available"
        return False
    
    def is_downloaded (self):
        "Whether repository is available"
        return False
    
    def update_workdir (self, destdir):
        "Populate (preferably update) DESTDIR with sources of specified version/branch"

        pass

    ## Version should be human-readable version.
    def version  (self):
        """A human-readable revision number. It need not be unique over revisions."""
        return '0'

    def read_last_patch (self):
        """Return a dict with info about the last patch"""
        assert 0
        return {}

    def get_diff_from_tag (self, name):
        """Return diff wrt to last tag that starts with NAME  """
        assert 0
        return 'baseclass method called'

class Version:
    def __init__ (self, version):
        self.dir = None
        self._version = version

    def download (self):
        pass

    def get_checksum (self):
        return self.version ()

    def is_tracking (self):
        return False

    def update_workdir (self, destdir):
        pass

    def version (self):
        return self._version

    def set_oslog (self, oslog):
        pass

class Darcs (Repository):
    def __init__ (self, dir, source=''):
        Repository.__init__ (self, dir, '_darcs', source)

    def darcs_pipe (self, cmd):
        dir = self.dir
        return self.read_pipe ('cd %(dir)s && darcs %(cmd)s' % locals ())

    def darcs (self, cmd):
        dir = self.dir
        return self.system ('cd %(dir)s && darcs %(cmd)s' % locals ())

    def get_revision_description (self):
        return self.darcs_pipe ('changes --last=1')
    
    def is_downloaded (self):
        return os.path.isdir (os.path.join (self.dir, self.vcs))

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

    def get_checksum (self):
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
        vcs = self.vcs
        self.system ('rsync --exclude %(vcs)s -a%(verbose)s %(dir)s/* %(destdir)s/' % locals())

    def get_file_content (self, file):
        dir = self.dir
        return open ('%(dir)s/%(file)s' % locals ()).read ()

    
class TarBall (Repository):
    # TODO: s/url/source
    def __init__ (self, dir, url, version=None, strip_components=1):
        Repository.__init__ (self, dir, '.tar', url)

        self.dir = dir
        if not os.path.isdir (self.dir):
            self.system ('mkdir -p %s' % self.dir)

        self._version = version
        if not version:
            print misc.split_ball (url)
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

    def get_checksum (self):
        from gub import misc
        return misc.ball_basename (self._file_name ())
    
    def update_workdir_deb (self, destdir):
        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)

        tarball = self.dir + '/' + self._file_name ()
        strip_components = self.strip_components
        self.system ('mkdir %s' % destdir)       
        self.system ('ar p %(tarball)s data.tar.gz | tar -C %(destdir)s --strip-component=%(strip_components)d -zxf -' % locals ())
        
    def update_workdir_tarball (self, destdir):
        
        tarball = self.dir + '/' + self._file_name ()
        flags = mirrors.untar_flags (tarball)

        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)

        self.system ('mkdir %s' % destdir)       
        strip_components = self.strip_components
        self.system ('tar -C %(destdir)s --strip-component=%(strip_components)d %(flags)s %(tarball)s' % locals ())

    def update_workdir (self, destdir):
        if '.deb' in self._file_name () :
            self.update_workdir_deb (destdir)
        else:
            self.update_workdir_tarball (destdir)

    def version (self):
        from gub import misc
        return self._version

class NewTarBall (TarBall):
    def __init__ (self, dir, mirror, name, ball_version, format='gz',
                  strip_components=1):
        TarBall.__init__ (self, dir, mirror % locals (), ball_version,
                          strip_components)

class RepositoryException (Exception):
    pass

class Git (Repository):
    def __init__ (self, dir, source='', branch='', revision=''):
        Repository.__init__ (self, dir, '.git', source)
        user_repo_dir = os.path.join (self.dir, self.vcs)
        if os.path.isdir (user_repo_dir):
            self.dir = user_repo_dir
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

    def get_file_content (self, file_name):
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

    def get_checksum (self):
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
        
        if os.path.isdir (os.path.join (destdir, self.vcs)):
            self.git ('pull %(repo_dir)s %(branch)s' % locals (), dir=destdir)
        else:
            self.system ('git-clone -l -s %(repo_dir)s %(destdir)s' % locals ())

        if not revision:
            revision = open ('%(repo_dir)s/refs/heads/%(branch)s' % locals ()).read ()

        if not branch:
            branch = 'gub_build'
            
        open ('%(destdir)s/.git/refs/heads/%(branch)s' % locals (), 'w').write (revision)
        self.git ('checkout %(branch)s' % locals (), dir=destdir) 

class CVS (Repository):
    cvs_entries_line = re.compile ("^/([^/]*)/([^/]*)/([^/]*)/([^/]*)/")
    #tag_dateformat = '%Y/%m/%d %H:%M:%S'

    def __init__ (self, dir, source='', module='', tag='HEAD'):
        Repository.__init__ (self, dir, '.cvs', source)
        self.module = module
        self.checksums = {}
        self.source = source
        self.tag = tag
        self.branch = tag # for vc_version_suffix
        if not os.path.isdir (self.dir):
            self.system ('mkdir -p %s' % self.dir)
            
    def _checkout_dir (self):
        return '%s/%s' % (self.dir, self.tag)

    def is_tracking (self):
        return True ##FIXME

    def get_revision_description (self):
        try:
            contents = get_file_content ('ChangeLog')
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

    def get_checksum (self):
        if self.checksums.has_key (self.tag):
            return self.checksums[self.tag]
        
        file = '%s/%s/.vc-checksum' % (self.dir, self.tag)

        if os.path.exists (file):
            cs = open (file).read ()
            self.checksums[self.tag] = cs
            return cs
        else:
            return '0'
        
    def get_file_content (self, file_name):
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
        if self.oslog and self.oslog.verbose >= self.oslog.commands:
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
        if not self.is_downloaded ():
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
    
# FIXME: why are cvs, darcs, git so complicated?
class SimpleRepo (Repository):
    def __init__ (self, dir, vcs, source, branch, revision='HEAD'):
        Repository.__init__ (self, dir, vcs, source)
        self.source = source
        self.revision = revision
        self.branch = branch
        if not os.path.isdir (self.dir):
            self.system ('mkdir -p %(dir)s' % self.__dict__)

    def is_tracking (self):
        ## FIXME, probably wrong.
        return (not self.revision or self.revision == 'HEAD')

    def update_workdir (self, destdir):
        dir = self._checkout_dir ()
        self._copy_working_dir (dir, destdir)

    def is_downloaded (self):
        dir = self._checkout_dir ()
        return os.path.isdir (os.path.join (dir, self.vcs))

    def download (self):
        if not self.is_downloaded ():
            self._checkout ()
        if self._current_revision () != self.revision:
            self._update (self.revision)

    def _copy_working_dir (self, dir, copy):
        vcs = self.vcs
        verbose = ''

        from gub import oslog
        if self.oslog and self.oslog.verbose >= oslog.level['command']:
            verbose = 'v'
        self.system ('rsync -a%(verbose)s --exclude %(vcs)s %(dir)s/ %(copy)s'
                     % locals ())

    def _checkout_dir (self):
        # Support user-check-outs
        if os.path.isdir (os.path.join (self.dir, self.vcs)):
            return self.dir
        revision = self.revision
        dir = self.dir
        branch = self.branch
        if branch and revision:
            branch += '-'
        return '%(dir)s/%(branch)s%(revision)s' % locals ()

    def get_file_content (self, file_name):
        return open (self._checkout_dir () + '/' + file_name).read ()

    def get_checksum (self):
        return self._current_revision ()

    def version (self):
        return self.revision

class Subversion (SimpleRepo):
    def __init__ (self, dir, source, branch, module, revision='HEAD'):
        if not revision:
            revision = 'HEAD'
        SimpleRepo.__init__ (self, dir, '.svn', source, branch, revision)
        self.module = module

    def _current_revision (self):
        dir = self._checkout_dir ()

        ## UGH: should not parse user oriented output
        revno = self.read_pipe ('cd %(dir)s && LANG= svn info' % locals ())
        m = re.search  ('.*Revision: ([0-9]*).*', revno)
        assert m
        return m.group (1)
        
    def _checkout (self):
        dir = self.dir
        source = self.source
        branch = self.branch
        module = self.module
        revision = self.revision
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(dir)s && svn co %(rev_opt)s %(source)s/%(branch)s/%(module)s %(branch)s-%(revision)s''' % locals ()
        self.system (cmd)
        
    def _update (self, revision):
        dir = self._checkout_dir ()
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(dir)s && svn up %(rev_opt)s' % locals ()
        self.system (cmd)

class Bazaar (SimpleRepo):
    def __init__ (self, dir, source, revision='HEAD'):
        # FIXME: multi-branch repos not supported for now
        if not revision:
            revision = '0'
        SimpleRepo.__init__ (self, dir, '.bzr', source, '', revision)

    def _current_revision (self):
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

def get_appended_vcs_name (name):
    return re.search (r"(.*)[._](bzr|git|cvs|svn|darcs|tar(.gz|.bz2))", name)

def get_prepended_vcs_name (name):
    return re.search (r"(bzr|git|cvs|svn|darcs):", name)

# FIXME: removeme, allow for user to checkout sources in any directory
# and use that as cache
def get_vcs_type_from_checkout_directory_name (dir):
    m = get_appended_vcs_name (dir)
    if m:
        dir = m.group (1)
        type = m.group (2)
        return dir, type
    return dir, None

def get_vcs_type_of_dir (dir):
    # FIXME: get these from all repositories...
    for i in ('.bzr', '.git', 'CVS', '.svn', '_darcs'):
        if os.path.isdir (os.path.join (dir, i)):
            return i.replace ('.', '').replace ('_', '')
    #Hmm
    return 'tar.gz'

def get_vcs_type_from_url (url):
    m = get_prepended_vcs_name (url)
    if m:
        type = m.group (1)
        url = m.group (2)
        return url, type
    p = url.find ('//:')
    if p > 0:
        protocol = url[:p]
        type = {'bzr+ssh': 'bzr',
                'svn+ssh': 'svn',
            }.get (protocol, None)
        if type:
            return url, type
    m = get_appended_vcs_name (url)
    if m:
        type = m.group (2)
        return url, type
    return url, None

def get_repository_proxy (dir, url, revision, branch):
    type = None
    if url:
        url, type = get_vcs_type_from_url (url)
    if not type:
        dir, type = get_vcs_type_from_checkout_directory_name (dir)
    if not type:
        # FIXME: todo: teach repositories that they might be
        type = get_vcs_type_of_dir (dir)

    if type == 'bzr':
        return Bazaar (dir, source=url, revision=revision)
    elif type == 'cvs':
        return CVS (dir, source=url, tag=branch)
    elif type == 'darcs':
        return Darcs (dir, source=url)
    elif type == 'git':
        return Git (dir, source=url, branch=branch, revision=revision)
    elif type == 'svn':
        return Subversion (dir, source=url, branch=branch)
    elif type and type.startswith ('.tar.'):
        return TarBall (dir, url=url, branch=branch)
    
    class UnknownVcSystem (Exception):
        pass
    raise UnknownVcSystem ('Cannot determine vcs type: url=%(url)s, dir=%(dir)s'
                           % locals ())
