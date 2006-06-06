
import dbhash
import xml.dom.minidom
import md5
import re
import os
import time

from misc import *

def read_pipe (cmd, ignore_error=False):
    print 'pipe:', cmd
    pipe = os.popen (cmd)

    val = pipe.read ()
    if pipe.close () and not ignore_error:
        raise SystemFailed ("Pipe failed: %s" % cmd)
    
    return val

class KeyCollision (Exception):
    pass

class Repository:
    def __init__ (self, dir, repo_admin_dir):
        self.repo_dir = os.path.normpath (dir)
        self.repo_admin_dir = repo_admin_dir
        self.test_dir = os.path.join (self.repo_admin_dir, 'test-results')
        self._databases = {}
        
        if not os.path.isdir (self.test_dir):
            os.makedirs (self.test_dir)

    def __repr__ (self):
        return '%s: %s' % (self.__class__.__name__, self.repo_dir)

    def get_db (self, name):
        try:
            return self._databases[name]
        except KeyError:
            db_file = os.path.join (self.test_dir, name)
            db = dbhash.open (db_file, 'c')
            self._databases[name] = db
            
        return db
        
    def try_checked_before (self, hash, name):
        db = self.get_db (name)
        return db.has_key (hash)

    def set_checked_before (self, hash, name):
        db = self.get_db (name)
        db[hash] = '1'

    def tag (self, name):
        pass
    
    def read_last_patch (self):
        """Return a dict with info about the last patch"""
        
        assert 0
        return {}

    def get_diff_from_tag (self, name):
        """Return diff wrt to last tag that starts with NAME  """

        assert 0
        return 'baseclass method called'
    
def read_changelog (file):
    contents = open (file).read ()
    regex = re.compile ('\n([0-9])')
    entries = regex.split (contents)
    return entries

    
class DarcsRepository (Repository):
    def __init__ (self, dir):
        Repository.__init__ (self, dir, dir + '/_darcs/')
        self.tag_repository = None

    def base_command (self, subcmd):
        repo_opt = ""
        if self.repo_dir <> '.':
            repo_opt = "cd %s && " % self.repo_dir
            
        return '%sdarcs %s ' % (repo_opt, subcmd)
    
    def tag (self, name):
        system (self.base_command ('tag')  + ' --patch-name %s ' % name)

    def push (self, name, dest):
        system (self.base_command ('push') + ' -a -t %s %s ' % (name, dest))
        
    def get_diff_from_tag (self, base_tag):
        return os.popen (self.base_command (' diff ') + ' -u --from-tag %s' % base_tag).read ()
    
    def read_last_patch (self):

        last_change = read_pipe (self.base_command ('changes') + ' --xml --last=1')
        dom = xml.dom.minidom.parseString(last_change)
        patch_node = dom.childNodes[0].childNodes[1]
        name_node = patch_node.childNodes[1]

        d = dict (patch_node.attributes.items())
        d['name'] = name_node.childNodes[0].data

        d['patch_contents'] = (
            '''%(local_date)s - %(author)s
        
    * %(name)s''' % d)
    

        return d

    def xml_patch_name (self, patch):
        name_elts =  patch.getElementsByTagName ('name')
        try:
            return name_elts[0].childNodes[0].data
        except IndexError:
            return ''

    def get_release_hash (self):
        xml_string = read_pipe (self.base_command ('changes') + ' --xml ')
        dom = xml.dom.minidom.parseString(xml_string)
        patches = dom.documentElement.getElementsByTagName('patch')
        patches = [p for p in patches if not re.match ('^TAG', self.xml_patch_name (p))]

        release_hash = md5.new ()
        for p in patches:
            release_hash.update (p.toxml ())

        return release_hash.hexdigest ()

class CVSRepository (Repository):
    cvs_entries_line = re.compile ("^/([^/]*)/([^/]*)/([^/]*)/([^/]*)/")
    tag_dateformat = '%Y/%m/%d %H:%M:%S'

    def __init__ (self, dir):
        Repository.__init__ (self, dir, dir + '/CVS/')
        self.tag_db = self.get_db ('tags.db')
        self.time_stamp = -1
        self.version_checksum = '0000'
        self.read_cvs_entries ()
        
    def read_cvs_entries (self):
        checksum = md5.md5()

        latest_stamp = 0
        for d in self.cvs_dirs ():
            for e in self.cvs_entries (d):
                (name, version, date, dontknow) = e
                checksum.update (name + ':' + version)

                if date == 'Result of merge':
                    raise Exception ("repository has been altered")
                
                stamp = time.mktime (time.strptime (date))
                latest_stamp = max (stamp, latest_stamp)

        self.version_checksum = checksum.hexdigest ()
        self.time_stamp = latest_stamp

    def get_release_hash (self):
        return self.version_checksum
    
    def tag (self, name):
        if self.tag_db.has_key (name):
            raise KeyCollision ("DB already has key " + name)

        tup = time.gmtime (self.time_stamp)
        val = time.strftime (self.tag_dateformat, tup)
        self.tag_db[name] = val
        
    def get_diff_from_exact_tag (self, name):
        date = self.tag_db [name]
        date = date.replace ('/', '')
        
        cmd = 'cd %s && cvs diff -uD "%s" ' % (self.repo_dir, date)
        return 'diff from %s\n%s:\n' % (name, cmd) + read_pipe (cmd, ignore_error=True)

    def get_diff_from_tag (self, name):
        keys = [k for k in self.tag_db.keys ()
                if k.startswith (name)]
        
        keys.sort ()
        if keys:
            return self.get_diff_from_exact_tag (keys[-1])
        else:
            return 'No previous success result to diff with'
        
    
    def read_last_patch (self):
        d = {}
        d['date'] = time.strftime (self.tag_dateformat, time.gmtime (self.time_stamp))
        d['release_hash'] = self.version_checksum
        
        for (name, version, date, dontknow) in self.cvs_entries (self.repo_dir + '/CVS'):
            if name == 'ChangeLog':
                d['name']  = version
                break

        d['patch_contents'] = read_changelog (self.repo_dir + '/ChangeLog')[0]
        return d
        
    def cvs_dirs (self):
        retval =  []
        for (base, dirs, files) in os.walk (self.repo_dir):
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

def get_repository_proxy (dir):
    if os.path.isdir (dir + '/CVS'):
        return CVSRepository (dir)
    elif os.path.isdir (dir + '/_darcs'):
        return DarcsRepository (dir)
    else:
        raise Exception('repo format unknown: ' + dir)

    return Repository('', '')


## test routine
if __name__ == '__main__':
    repo = get_repository_proxy (sys.argv[1])
    print repo.all_cvs_entries ()
