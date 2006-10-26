import misc
import os
import re
import md5
import locker
import time
import urllib
import download

## note: repository.py still being used by test-gub, so don't
## throw this overboard yet.
##
class Repository: 
    def __init__ (self):
        self.system = misc.system
        self.read_pipe = misc.read_pipe
        
    def download (self):
        assert 0 

    def get_checksum (self):
        assert 0

    def get_file_content (self, filename):
        return ''

    def is_tracking (self):
        "download will fetch newer versions if available"
        return False
    
    def update_workdir (self, destdir):
        "Populate (preferably update) DESTDIR with sources of specified version/branch"

        assert 0

class DarcsRepository (Repository):
    def __init__ (self, dir, source):
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
    def __init__ (self, dir, url):
        Repository.__init__ (self)
        if not os.path.isdir (dir):
            self.system ('mkdir -p %s' % dir)

        self.dir = dir
        self.url = url
        self.branch = None
        self.revision = None
          
    
    def is_tracking (self):
        return False

    def _filename (self):
        return re.search ('.*/([^/]+)$', self.url).group (1)
    
    def _is_downloaded (self):
        name = self.dir + '/' + self._filename  ()
        return os.path.exists (self)
    
    def download (self):
        misc.download_url (self.url, self.dir)

    def get_checksum (self):
        return self._filename ()
    
    def update_workdir_deb (self, destdir):
        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)

        tarball = self.dir + '/' + self._filename ()
        self.system ('mkdir %s' % destdir)       
        self.system ('ar p %(tarball)s data.tar.gz | tar -C %(destdir)s --strip-component 1 -zxf -' % locals ())
        
    def update_workdir_tarball (self, destdir):
        
        tarball = self.dir + '/' + self._filename ()
        flags = download.untar_flags (tarball)

        if os.path.isdir (destdir):
            self.system ('rm -rf %s' % destdir)

        self.system ('mkdir %s' % destdir)       
        self.system ('tar -C %(destdir)s --strip-component 1  %(flags)s %(tarball)s' % locals ())

    def update_workdir (self, destdir):
        if '.deb' in self._filename () :
            self.update_workdir_deb (destdir)
        else:
            self.update_workdir_tarball (destdir)

class RepositoryException (Exception):
    pass

class GitRepository (Repository):
    def __init__ (self, git_dir, source='', branch='', revision=''):
        Repository.__init__ (self)
        
        self.repo_dir = os.path.normpath (git_dir) + '.git'
        self.checksums = {}
        self.branch = branch
        self.revision = revision
        self.source = source

    def is_tracking (self):
        return self.branch != ''
    
    def __repr__ (self):
        return '#<GitRepository %s>' % self.repo_dir

    def get_revision_description (self):
        return self.git_pipe ('git log --max-count=1') 

    def get_file_content (self, filename):
        committish = self.git_pipe ('log %(branch)s --max-count=1 --pretty=oneline'
                                    % self.__dict__).split (' ')[0]
        m = re.search ('^tree ([0-9a-f]+)',
                       self.git_pipe ('cat-file commit %(committish)s'  % locals ()))

        treeish = m.group (1)
        for f in self.git_pipe ('ls-tree -r %(treeish)s' %
                                locals ()).split ('\n'):
            (info, name) = f.split ('\t')
            (mode, type, fileish) = info.split (' ')

            if name == filename:
                return self.git_pipe ('cat-file blob %(fileish)s ' % locals ())

        raise RepositoryException ('file not found')
        
    def get_branches (self):
        branch_lines = self.read_pipe (self.git_command () + ' branch -l ').split ('\n')

        branches =  [b[2:] for b in branch_lines]
        return [b for b in branches if b]

    def git_command (self, object_dir, dir, repo_dir):
        if repo_dir:
            repo_dir = '--git-dir %s' % repo_dir
        c = 'GIT_OBJECT_DIRECTORY=%(object_dir)s git %(repo_dir)s' % locals ()
        if dir:
            c = 'cd %s && %s' % (dir, c)

        return c
        
    def git (self, cmd, dir='', ignore_error=False,
             repo_dir=''):

        if repo_dir == '' and dir == '':
            repo_dir = self.repo_dir
        
        gc = self.git_command (self.repo_dir + '/objects', dir, repo_dir)
        cmd = '%(gc)s %(cmd)s' % locals ()
            
        self.system (cmd, ignore_error=ignore_error)

    def git_pipe (self, cmd, ignore_error=False,
                  dir='', repo_dir=''):

        if repo_dir == '' and dir == '':
            repo_dir = self.repo_dir
            
        gc = self.git_command (self.repo_dir + '/objects', dir, repo_dir)
        return self.read_pipe ('%(gc)s %(cmd)s' % locals ())
        
    def download (self):
        "Fetch updates from internet"
        
        repo = self.repo_dir
        source = self.source
        revision = self.revision
        
        if not os.path.isdir (self.repo_dir):
            self.git ('--git-dir %(repo)s clone --bare -n %(source)s %(repo)s' % locals ())
            return

        if revision:
            contents = self.git_pipe ('--git-dir %(repo)s ls-tree %(revision)s' % locals (),
                                      ignore_error=True)

            if contents:
                return
            
            self.git ('--git-dir %(repo)s http-fetch -v -c %(revision)s' % locals ())

        refs = '%s:%s' % (self.branch, self.branch)
        
        self.git ('--git-dir %(repo)s fetch --update-head-ok %(source)s %(refs)s ' % locals ())
        self.checksums = {}

    def set_current_branch (self, branch):
        open (self.repo_dir + '/HEAD', 'w').write ('ref: refs/heads/%s\n' % branch)
        
    def get_checksum (self):
        
        branch = self.branch
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
        branch = self.branch
        revision = self.revision
        
        if not os.path.isdir (destdir):
            self.system ('mkdir -p ' + destdir)

        if os.path.isdir (destdir + '/.git'):
            self.git ('pull %(repo_dir)s' % locals (), dir=destdir)
        else:
            self.git ('init-db', dir=destdir)

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
        if not os.path.isdir (dir):
            self.system ('mkdir -p %s' % dir)
            
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
        
        file = '%s/%s/.vc-checksum' % (self.repo_dir, branch)

        if os.path.exists (file):
            cs = open (file).read ()
            self.checksums[branch] = cs
            return cs
        else:
            return '0'
        
    def get_file_content (self, filename):
        return open (self._checkout_dir () + '/' + filename).read ()
        
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
        
        dir = self._checkout_dir()


        ## TODO: can we get deletes from vc?
        self.system ('rsync -av --delete --exclude CVS %(dir)s/ %(destdir)s' % locals ())
        
    def download (self):
        suffix = self.tag
        rev_opt = '-r ' + self.tag
        source = self.source
        
        dir = self._checkout_dir()

        lock_dir = locker.Locker (dir + '.lock')
        module = self.module
        cmd = ''
        if os.path.isdir (dir + '/CVS'):
            cmd += 'cd %(dir)s && cvs -q up -dAP %(rev_opt)s' % locals()
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
                filename = os.path.join (basedir, e[0])
                filename = filename.replace (self.repo_dir + '/', '')

                es.append ((filename,) + e[1:])
            

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

    def get_file_content (self, filename):
        return open (self._checkout_dir () + '/' + filename).read ()

    def _update (self, working, revision):
        '''SVN update'''
        rev_opt = '-r %(revision)s ' % locals ()
        cmd = 'cd %(working)s && svn up %(rev_opt)s' % locals ()
        self.system (cmd)
