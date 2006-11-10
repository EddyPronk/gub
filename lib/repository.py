import misc
import os
import re
import md5
import locker
import time
import urllib
import download

## Rename to Source/source.py?

class Repository: 
    def __init__ (self):
        self.system = misc.system
        self.read_pipe = misc.read_pipe
        
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
    
    def update_workdir (self, destdir):
        "Populate (preferably update) DESTDIR with sources of specified version/branch"

        pass

    ## Version should be human-readable version.
    def version  (self):
        """A human-readable revision number. It need not be unique over revisions."""
        return '0'

class Version:
    def __init__ (self, version):
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

class DarcsRepository (Repository):
    def __init__ (self, dir, source=''):
        Repository.__init__ (self)
        self.dir = dir + '.darcs'
        self.source = source

    def darcs_pipe (self, cmd):

        dir = self.dir
        return self.read_pipe ('cd %(dir)s && darcs %(cmd)s' % locals ())

    def darcs (self, cmd):
        dir = self.dir
        return self.system ('cd %(dir)s && darcs %(cmd)s' % locals ())

    def get_revision_description (self):
        return self.darcs_pipe ('changes --last=1')
    
    def download (self):
        dir = self.dir
        source = self.source

        if os.path.exists (dir + '/_darcs'):
            self.darcs ('pull -a %(source)s' % locals ())
        else:
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
        
        self.system ('rsync --exclude _darcs -av %(dir)s/* %(destdir)s/' % locals())

    def get_file_content (self, file):
        dir = self.dir
        return open ('%(dir)s/%(file)s' % locals ()).read ()

    
class TarBall (Repository):
    def __init__ (self, dir, url, version, strip_components=1):
        Repository.__init__ (self)
        if not os.path.isdir (dir):
            self.system ('mkdir -p %s' % dir)

        self.dir = dir
        self.url = url
        self._version = version
        self.branch = None
        self.strip_components = strip_components
        
    def is_tracking (self):
        return False

    def _file_name (self):
        return re.search ('.*/([^/]+)$', self.url).group (1)
    
    def _is_downloaded (self):
        name = os.path.join (self.dir, self._file_name  ())
        return os.path.exists (name)
    
    def download (self):
        if self._is_downloaded ():
            return
        misc.download_url (self.url, self.dir)

    def get_checksum (self):
        import misc
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
        flags = download.untar_flags (tarball)

        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)

        self.system ('mkdir %s' % destdir)       
        strip_components = self.strip_components
        self.system ('tar -C %(destdir)s --strip-component=%(strip_components)d  %(flags)s %(tarball)s' % locals ())

    def update_workdir (self, destdir):
        if '.deb' in self._file_name () :
            self.update_workdir_deb (destdir)
        else:
            self.update_workdir_tarball (destdir)

    def version (self):
        import misc
        return self._version

class RepositoryException (Exception):
    pass

class GitRepository (Repository):
    def __init__ (self, git_dir, source='', branch='', revision=''):
        Repository.__init__ (self)
        
        self.repo_dir = os.path.normpath (git_dir) + '.git'
        self.checksums = {}
        self.remote_branch = branch
        self.source = source
        self.revision = revision

        self.repo_url_suffix = re.sub ('.*://', '', source)

        if self.repo_url_suffix:
            self.repo_url_suffix = '-' + re.sub ('[/:+]+', '-', self.repo_url_suffix)
        
        if ':' in branch:
            (self.remote_branch,
             self.local_branch) = tuple (branch.split (':'))

            self.branch = self.local_branch.replace ('/', '-')
        elif source:
            self.branch = branch

            if branch:
                self.local_branch = branch + self.repo_url_suffix
                self.branch = self.local_branch
            else:
                self.local_branch = 'master' + self.repo_url_suffix
        else:
            self.branch = branch
            self.local_branch = branch
            
    def version (self):
        return self.revision

    def is_tracking (self):
        return self.branch != ''
    
    def __repr__ (self):
        return '#<GitRepository %s>' % self.repo_dir

    def get_revision_description (self):
        return self.git_pipe ('log --max-count=1') 

    def get_file_content (self, file_name):
        committish = self.git_pipe ('log %(local_branch)s --max-count=1 --pretty=oneline'
                                    % self.__dict__).split (' ')[0]
        m = re.search ('^tree ([0-9a-f]+)',
                       self.git_pipe ('cat-file commit %(committish)s'  % locals ()))

        treeish = m.group (1)
        for f in self.git_pipe ('ls-tree -r %(treeish)s' %
                                locals ()).split ('\n'):
            (info, name) = f.split ('\t')
            (mode, type, fileish) = info.split (' ')

            if name == file_name:
                return self.git_pipe ('cat-file blob %(fileish)s ' % locals ())

        raise RepositoryException ('file not found')
        
    def get_branches (self):
        branch_lines = self.read_pipe (self.git_command () + ' branch -l ').split ('\n')

        branches =  [b[2:] for b in branch_lines]
        return [b for b in branches if b]

    def git_command (self, dir, repo_dir):
        if repo_dir:
            repo_dir = '--git-dir %s' % repo_dir

        c = 'git %(repo_dir)s' % locals ()
        if dir:
            c = 'cd %s && %s' % (dir, c)

        return c
        
    def git (self, cmd, dir='', ignore_errors=False,
             repo_dir=''):

        if repo_dir == '' and dir == '':
            repo_dir = self.repo_dir
        
        gc = self.git_command (dir, repo_dir)
        cmd = '%(gc)s %(cmd)s' % locals ()
            
        self.system (cmd, ignore_errors=ignore_errors)

    def git_pipe (self, cmd, ignore_errors=False,
                  dir='', repo_dir=''):

        if repo_dir == '' and dir == '':
            repo_dir = self.repo_dir
            
        gc = self.git_command (dir, repo_dir)
        return self.read_pipe ('%(gc)s %(cmd)s' % locals ())
        
    def download (self):
        repo = self.repo_dir
        source = self.source
        revision = self.revision
        
        if not os.path.isdir (self.repo_dir):
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
            contents = self.git_pipe ('--git-dir %(repo)s ls-tree %(revision)s' % locals (),
                                      ignore_errors=True)

            if contents:
                return
            
            self.git ('--git-dir %(repo)s http-fetch -v -c %(revision)s' % locals ())

        refs = '%s:%s' % (self.remote_branch, self.branch)
        
        self.git ('--git-dir %(repo)s fetch --update-head-ok %(source)s %(refs)s ' % locals ())
        self.checksums = {}

    def get_checksum (self):
        if self.revision:
            return self.revision
        
        branch = self.local_branch
        if self.checksums.has_key (branch):
            return self.checksums[branch]

        repo_dir = self.repo_dir
        if os.path.isdir (repo_dir):
            cs = self.git_pipe ('--git-dir %(repo_dir)s describe --abbrev=24 %(branch)s' % locals ())
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

        repo_dir = self.repo_dir
        branch = self.local_branch
        revision = self.revision
        
        if os.path.isdir (destdir + '/.git'):
            self.git ('pull --no-tags %(repo_dir)s %(branch)s' % locals (), dir=destdir)
        else:
            self.system ('git-clone -s %(repo_dir)s %(destdir)s' % locals ())

        if not revision:
            revision = open ('%(repo_dir)s/refs/heads/%(branch)s' % locals ()).read ()

        if not branch:
            branch = 'gub_build'
            
        open ('%(destdir)s/.git/refs/heads/%(branch)s' % locals (), 'w').write (revision)
        self.git ('checkout %(branch)s' % locals (), dir=destdir) 



class CVSRepository(Repository):
    cvs_entries_line = re.compile ("^/([^/]*)/([^/]*)/([^/]*)/([^/]*)/")
    #tag_dateformat = '%Y/%m/%d %H:%M:%S'

    def __init__ (self, dir,
                  source='', module='', tag='HEAD'):
        Repository.__init__ (self)
        self.repo_dir = os.path.normpath (dir) + '.cvs'
        self.module = module
        self.checksums = {}
        self.source = source
        self.tag = tag
        self.branch = tag # for vc_version_suffix
        if not os.path.isdir (self.repo_dir):
            self.system ('mkdir -p %s' % self.repo_dir)
            
    def _checkout_dir (self):
        return '%s/%s' % (self.repo_dir, self.tag)

    def is_tracking (self):
        return True ##FIXME

    def get_revision_description (self):
        try:
            contents = get_file_content ('ChangeLog')
            entry_regex = re.compile ('\n([0-9])')
            entries = entry_regex.split (contents)
            descr = entries[0]
            
            changelog_rev = ''
            
            for (name, version, date, dontknow) in self.cvs_entries (self.repo_dir + '/CVS'):
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
        
        file = '%s/%s/.vc-checksum' % (self.repo_dir, self.tag)

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
        self.system ('rsync -av --delete --exclude CVS %(dir)s/ %(destdir)s' % locals ())
        
    def download (self):
        suffix = self.tag
        rev_opt = '-r ' + self.tag
        source = self.source
        dir = self._checkout_dir ()
        lock_dir = locker.Locker (dir + '.lock')
        module = self.module
        cmd = ''
        if os.path.isdir (dir + '/CVS'):
            cmd += 'cd %(dir)s && cvs -q up -dCAP %(rev_opt)s' % locals()
        else:
            repo_dir = self.repo_dir
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
                file_name = file_name.replace (self.repo_dir + '/', '')

                es.append ((file_name,) + e[1:])
            

        return es

    def all_files (self, branch):
        entries = self.all_cvs_entries (self.repo_dir + '/' + branch)
        return [e[0] for e in entries]
    

class Subversion (Repository):
    def __init__ (self, dir, source, branch, module, revision):
        Repository.__init__ (self)
        self.dir = os.path.normpath (dir) + '.svn'
        self.source = source
        self.branch = branch
        self.module = module
        self.revision = revision
        if not os.path.isdir (self.dir):
            self.system ('mkdir -p %(dir)s' % self.__dict__)

    def is_tracking (self):
        ## fixme, probably wrong.
        return self.revision == 'HEAD'

    def update_workdir (self, destdir):
        working = self._checkout_dir ()
        self._copy_working_dir (working, destdir)

    def download (self):
        working = self._checkout_dir ()
        if not os.path.isdir (working + '/.svn'):
            self._checkout (self.source, self.branch, self.module,
                            self.revision)
        if self._current_revision () != self.revision:
            self._update (working, self.revision)

    def _current_revision (self):
        working = self._checkout_dir ()
        revno = self.read_pipe ('cd %(working)s && svn info' % locals ())
        m = re.search  ('.*Revision: ([0-9]*).*', revno)
        assert m
        return m.group (1)
        
    def get_checksum (self):
        return self._current_revision ()

    def _checkout (self, source, branch, module, revision):
        '''SVN checkout'''
        dir = self.dir
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(dir)s && svn co %(rev_opt)s %(source)s/%(branch)s/%(module)s %(branch)s-%(revision)s''' % locals ()
        self.system (cmd)
        
    def _copy_working_dir (self, working, copy):
        self.system ('rsync -av --exclude .svn %(working)s/ %(copy)s'
                     % locals ())
        
    def _checkout_dir (self):
        revision = self.revision
        dir = self.dir
        branch = self.branch
        return '%(dir)s/%(branch)s-%(revision)s' % locals ()

    def get_file_content (self, file_name):
        return open (self._checkout_dir () + '/' + file_name).read ()

    def _update (self, working, revision):
        '''SVN update'''
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(working)s && svn up %(rev_opt)s' % locals ()
        self.system (cmd)

    def version (self):
        return self.revision

def get_repository_proxy (dir, branch):
    m = re.search (r"(.*)\.(git|cvs|svn|darcs)", dir)
    
    dir = m.group (1)
    type = m.group (2)

    if type == 'cvs':
        return CVSRepository (dir, branch=branch )
    elif type == 'darcs':
        return DarcsRepository (dir)
    elif type == 'git':
        return GitRepository (dir, branch=branch)
    elif type == 'svn':
        return SvnRepository (dir, branch=branch)
    else:
        raise UnknownVcSystem('repo format unknown: ' + dir)

    return Repository('', '')
