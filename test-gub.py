#!/usr/bin/python

import re
import smtplib
import os
import time
import email.MIMEText
import email.Message
import email.MIMEMultipart
import optparse
import md5
import dbhash
import xml.dom.minidom

## TODO: should incorporate checksum of lilypond checkout too.

################################################################
# utils.

class Barf:
    def __init__ (self, msg):
        self.msg = msg
    def __str__ (self):
        return self.msg
    
def system (cmd):
    print cmd
    stat = os.system (cmd)
    if stat:
        raise Barf('Command failed ' + `stat`)


def read_pipe (cmd):
    print 'pipe:', cmd
    pipe = os.popen (cmd)

    val = pipe.read ()
    if pipe.close ():
        raise Barf ("Pipe failed: %s", cmd)
    
    return val

def read_tail (file, amount=10240):
    f = open (file)
    f.seek (0, 2)
    length = f.tell()
    f.seek (- min (length, amount), 1)
    return f.read ()

def canonicalize_target (target):
    canonicalize = re.sub('[ \t\n]', '_', target)
    canonicalize = re.sub ('[^a-zA-Z0-9]', '_', canonicalize)
    return canonicalize

################################################################
#
db_file_template = 'test-done-%(canonicalized_target)s.db'

class Repository:
    def __init__ (self, dir, repo_admin_dir):
        self.repodir = dir
        self.repo_admin_dir = repo_admin_dir
        self.test_dir = os.path.join (self.repo_admin_dir, 'test-results')
        if not os.path.isdir (self.test_dir):
            os.makedirs (self.test_dir)
    def get_db (self, name):
        db_file = os.path.join (self.test_dir, name)
        print 'Using database ', db_file
        db = dbhash.open (db_file, 'c')
        return db
        
    def try_checked_before (self, hash, canonicalized_target):
        db = self.get_db (db_file_template % locals())
        return db.has_key (hash)

    def set_checked_before (self, hash, canonicalized_target):
        db = self.get_db (db_file_template % locals())
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
        if self.repodir <> '.':
            repo_opt = "cd %s && " % self.repodir
            
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
        print 'reading entries from', self.repodir
        checksum = md5.md5()

        latest_stamp = 0
        for d in self.cvs_dirs ():
            for e in self.cvs_entries (d):
                (name, version, date, dontknow) = e
                checksum.update (name + ':' + version)
                
                stamp = time.mktime (time.strptime (date))
                latest_stamp = max (stamp, latest_stamp)

        self.version_checksum = checksum.hexdigest ()
        self.time_stamp = latest_stamp

    def get_release_hash (self):
        return self.version_checksum
    
    def tag (self, name):
        if self.tag_db.has_key (name):
            raise Barf ("DB already has key " + name)

        print 'tagging db with %s' % name
        
        tup = time.gmtime (self.time_stamp)
        val = time.strftime (self.tag_dateformat, tup)
        self.tag_db[name] = val
        
    def get_diff_from_exact_tag (self, name):
        date = self.tag_db [name]
        date = date.replace ('/', '')
        
        cmd = 'cd %s && cvs diff -uD "%s" ' % (self.repodir, date)
        return 'diff from %s\n%s:\n' % (name, cmd) + read_pipe (cmd)

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
        
        for (name, version, date, dontknow) in self.cvs_entries (self.repodir + '/CVS'):
            if name == 'ChangeLog':
                d['name']  = version
                break

        d['patch_contents'] = read_changelog (self.repodir + '/ChangeLog')[0]
        return d
        
    def cvs_dirs (self):
        retval =  []
        for (base, dirs, files) in os.walk (self.repodir):
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
        

def get_repository_proxy (dir):
    if os.path.isdir (dir + '/CVS'):
        return CVSRepository (dir)
    elif os.path.isdir (dir + '/_darcs'):
        return DarcsRepository (dir)
    else:
        raise Barf('repo format unknown: ' + dir)

def result_message (parts, subject='') :
    """Concatenate PARTS to a Message object."""
    
    if not parts:
        parts.append ('(empty)')
    
    parts = [email.MIMEText.MIMEText (p) for p in parts if p]

    msg = parts[0]
    if len (parts) > 1:
        msg = email.MIMEMultipart.MIMEMultipart()
        for p in parts:
            msg.attach (p)
    
    msg['Subject'] = subject
    msg.epilogue = ''

    return msg

def opt_parser ():
    try:
        address = os.environ['EMAIL']
    except KeyError:
        address = '%s@localhost' % os.getlogin()


    
    p = optparse.OptionParser(usage="test-gub.py [options] command command ... ")
    p.add_option ('-t', '--to',
                  action='append',
                  dest='address',
                  default=[],
                  help='where to send error report')
    
    p.add_option ('-f', '--from',
                  action='store',
                  dest='sender',
                  default=address,
                  help='whom to list as sender')
    
    p.add_option ('', '--repository',
                  action="store",
                  dest="repository",
                  default=".",
                  help="repository directory")
    
    p.add_option ('', '--tag-repo',
                  action='store',
                  dest='tag_repo',
                  default='',
                  help='where to push success tags.')

    p.add_option ('', '--summary',
                  action='store_true',
                  dest='summary',
                  default=False,
                  help='produce a summary mail too.')

    p.add_option ('', '--quiet',
                  action='store_true',
                  dest='be_quiet',
                  default=False,
                  help='only send mail when there was an error.')


    p.add_option ('', '--posthook',
                  action='append',
                  dest='posthooks',
                  default=[],
                  help='commands to execute after successful tests.')

    p.add_option ('-s', '--smtp',
                  action='store',
                  dest='smtp',
                  default='localhost',
                  help='SMTP server to use.')

    return p

def test_target (repo, options, target, last_patch):
    canonicalize = canonicalize_target (target)
    release_hash = last_patch['release_hash']
    if repo.try_checked_before (release_hash, canonicalize):
        print 'release has already been checked: ', release_hash 
        return None

    logfile = 'test-%(canonicalize)s.log' %  locals()
    logfile = os.path.join (repo.test_dir, logfile)
    
    cmd = "nice time %(target)s >& %(logfile)s" %  locals()

    print 'starting : ', cmd
    stat = os.system (cmd)
    base_tag = 'success-%(canonicalize)s-' % locals ()

    result = 'unknown'
    attachments = []
    
    body = read_tail (logfile, 10240).split ('\n')
    if stat:
        diff = repo.get_diff_from_tag (base_tag)

        result = 'FAIL'
        attachments = ['error for %s\n\n%s' % (target,
                                               '\n'.join (body[-0:])),
                       diff]
    else:
        tag = base_tag + canonicalize_target (last_patch['date'])
        repo.tag (tag)
        result = "SUCCESS"
        if options.tag_repo:
            repo.push (tag, options.tag_repo)
            
        result += ', tagging with %s' % tag
            
        attachments = ['\n'.join (body[-10:])]

    repo.set_checked_before (release_hash, canonicalize)
    return (result, attachments)
    
def send_message (options, msg):
    print 'sending message.'
    
    COMMASPACE = ', '
    msg['From'] = options.sender
    msg['To'] = COMMASPACE.join (options.address)
    msg['X-Autogenerated'] = 'lilypond'
    connection = smtplib.SMTP (options.smtp)
    connection.sendmail (options.sender, options.address, msg.as_string ())

def main ():
    (options, args) = opt_parser().parse_args ()

    repository = get_repository_proxy (options.repository)
    
    last_patch = repository.read_last_patch ()
    
    release_hash = repository.get_release_hash ()
    last_patch['release_hash'] = release_hash
    release_id = '''

Last patch of this release:

%(patch_contents)s\n

MD5 of complete patch set: %(release_hash)s

''' % last_patch

    results = {}
    failures = 0
    for a in args:
        result_tup = test_target (repository, options, a, last_patch)
        if not result_tup:
            continue

        results[a] = result_tup
        
        (r, atts) = result_tup
        success = r.startswith ('SUCCESS')
        if not success:
            failures += 1

        if not (options.be_quiet and success):
            msg = result_message (atts, subject="Autotester: %s %s" % (r, a))
            send_message (options, msg)
        

        
    main = '\n'.join (['%s: %s' % (target, res)
             for (target, (res, atts)) in results.items ()])

    msg_body = [main, release_id]
    msg = result_message (msg_body, subject="Autotester: summary")

    if (results
        and options.summary
        and (failures > 0 or not options.be_quiet)):
        send_message (options, msg)

    if failures == 0 and results:
        for p in options.posthooks:
            system (p)

def test ():
    (options, args) = opt_parser().parse_args ()

    repository = get_repository_proxy (options.repository)
    print repository.read_last_patch ()
#    repository.tag ('testje')
#    repository.tag ('testje21')
#    repository.tag ('testje22')
    repository.get_diff_from_tag ('testje2')

if __name__ == '__main__':    
#    test()
    main()
