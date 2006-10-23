import misc
import os
import re
import md5
import locker
import time

## note: repository.py still being used by test-gub, so don't
## throw this overboard yet.
##
class Repository: 
    def __init__ (self):
        self.system = misc.system
        self.read_pipe = misc.read_pipe
        
    def update (self, source, branch=None, commit=None):
        assert 0 

    def get_branch_version (self, branch):
        assert 0

    def checkout (self, destdir, branch=None, commit=None):
        assert 0
    
class GitRepository (Repository):
    def __init__ (self, git_dir):
        Repository.__init__ (self)
        self.repo_dir = git_dir
        self.checksums = {}
    def __repr__ (self):
        return '#<GitRepository %s>' % self.repo_dir
    
    def get_branches (self):
        branch_lines = self.read_pipe (self.git_command () + ' branch -l ').split ('\n')

        branches =  [b[2:] for b in branch_lines]
        return [b for b in branches if b]
        
    def git_command (self):
        cmd = 'git --git-dir %s ' % self.repo_dir
        return cmd
    
    def update (self, source, branch=None, commit=None):
        cmd = self.git_command ()
        if not os.path.isdir (self.repo_dir):
            repo = self.repo_dir
            self.system ('%(cmd)s clone --bare -n %(source)s %(repo)s' % locals ())
            return


        if commit:
            contents = self.read_pipe ('%(cmd)s ls-tree %(commit)s' % locals (), ignore_error=True)

            if contents:
                return
            
            self.system ('%(cmd)s http-fetch -v -c %(commit)s' % commit)

        branches = []
        if branch:
            branches.append (branch)
        else:
            branches = self.get_branches ()
            
            
        refs = ' '.join ('%s:%s' % (b,b) for b in branches)
        self.system ('%(cmd)s fetch %(source)s %(refs)s' % locals ())

        self.checksums = {}
        
    def get_branch_version (self, branch):
        if self.checksums.has_key (branch):
            return self.checksums[branch]

        if os.path.isdir (self.repo_dir):
            cs = self.read_pipe ('%s describe --abbrev=24 %s' % (self.git_command (),
                                                                 branch))
            cs = cs.strip ()
            self.checksums[branch] = cs
            return cs
        else:
            return 'invalid'
        
    def checkout (self, destdir, branch=None, commit=None):
        if not os.path.isdir (destdir):
            self.system ('mkdir -p ' + destdir)

        cmd = self.git_command ()

        if branch:
            self.system ('cd %(destdir)s && %(cmd)s checkout %(branch)s &&  %(cmd)s checkout-index -a' % locals())
        elif commit:
            self.system ('cd %(destdir)s && %(cmd)s read-tree %(commit)s && %(cmd)s checkout-index -a ' % locals ())
        

class CVSRepository(Repository):
    cvs_entries_line = re.compile ("^/([^/]*)/([^/]*)/([^/]*)/([^/]*)/")
    tag_dateformat = '%Y/%m/%d %H:%M:%S'

    def __init__ (self, dir, module):
        Repository.__init__ (self)
        self.repo_dir = dir
        self.module = module
        self.checksums = {}
        if not os.path.isdir (dir):
            self.system ('mkdir -p %s' % dir)
        
    def get_branch_version (self, branch):
        if self.checksums.has_key (branch):
            return self.checksums[branch]
        
        file = '%s/%s/.vc-checksum' % (self.repo_dir, branch)

        if os.path.exists (file):
            cs = open (file).read ()
            self.checksums[branch] = cs
            return cs
        else:
            return '0'

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
    
    def checkout (self, destdir, branch=None, commit=None):
        
        suffix = branch
        if commit:
            suffix = commit
        dir = self.repo_dir  +'/' + suffix        

        self.system ('rsync -av --exclude CVS %(dir)s/ %(destdir)s' % locals ())
        
    def update (self, source, branch=None, commit=None):
        suffix = branch
        rev_opt = '-r ' + branch
        if commit:
            suffix = commit
            rev_opt = '-r ' + commit
            
        dir = self.repo_dir  +'/' + suffix        

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
        
    def all_cvs_entries (self):
        ds = self.cvs_dirs ()
        es = []
        for d in ds:
            
            ## strip CVS/
            basedir = os.path.split (d)[0]
            for e in self.cvs_entries (d):
                
                
                filename = os.path.join (basedir, e[0])
                filename = filename.replace (self.repo_dir + '/', '')

                es.append ((filename,) + e[1:])
            

        return es
