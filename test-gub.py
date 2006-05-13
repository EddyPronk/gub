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
import sys
import xml.dom.minidom

## TODO: should incorporate checksum of lilypond checkout too.

db_file_template = 'log/gub-done-%(canonicalized_target)s.db'

def try_checked_before (hash, canonicalized_target):
    if not os.path.isdir ('test'):
        os.makedirs ('test')

    db_file = db_file_template % locals()
    print 'Using database ', db_file
    db = dbhash.open (db_file, 'c')
    return db.has_key (hash)

def set_checked_before (hash, canonicalized_target):
    db_file = db_file_template % locals()
    print 'Writing check to', db_file
    db = dbhash.open (db_file, 'c')
    db[hash] = '1'
    
def read_last_patch ():
    """Return a dict with info about the last patch"""
    
    last_change = os.popen ('darcs changes --xml --last=1').read ()
    dom = xml.dom.minidom.parseString(last_change)
    patch_node = dom.childNodes[0].childNodes[1]
    name_node = patch_node.childNodes[1]

    d = dict (patch_node.attributes.items())
    d['name'] = patch_node.childNodes[1].childNodes[0].data
    return d

def system (cmd):
    print cmd
    stat = os.system (cmd)
    if stat:
        raise 'Command failed', stat

def result_message (options, parts, subject='') :
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
    p = optparse.OptionParser(usage="test-gub.py [options] command command ... ")
    p.add_option ('-t', '--to',
           action ='append',
           dest = 'address',
           default = [],
           help = 'where to send error report')
    
    try:
        address = os.environ['EMAIL']
    except KeyError:
        address = '%s@localhost' % os.getlogin()

    p.add_option ('', '--check-file',
                  dest='check_files',
                  action="append",
                  metavar="FILE",
                  default=[],
                  help="Include FILE in the version checksumming too")
    p.add_option ('-f', '--from',
                  action='store',
                  dest='sender',
                  default=address,
                  help='whom to list as sender')
    p.add_option ('', '--tag-repo',
                  action='store',
                  dest='tag_repo',
                  default='',
                  help='where to push success tags.')

    p.add_option ('-s', '--smtp',
                  action='store',
                  dest='smtp',
                  default='localhost',
                  help='SMTP server to use.')

    return p

def read_tail (file, amount=10240):
    f = open (file)
    f.seek (0, 2)
    length = f.tell()
    f.seek (- min (length, amount), 1)
    return f.read ()

################################################################
# main
def xml_patch_name (patch):
    name_elts =  patch.getElementsByTagName ('name')
    try:
        return name_elts[0].childNodes[0].data
    except IndexError:
        return ''
    
def get_release_hash (extra_files):
    xml_string = os.popen ('darcs changes --xml').read()
    dom = xml.dom.minidom.parseString(xml_string)
    patches = dom.documentElement.getElementsByTagName('patch')
    patches = [p for p in patches if not re.match ('^TAG', xml_patch_name (p))]

    release_hash = md5.new ()
    for p in patches:
        release_hash.update (p.toxml ())

    for f in extra_files:
        release_hash.update (open (f).read ())

    release_hash = release_hash.hexdigest()
    print 'release hash is ', release_hash
    
    return release_hash

def canonicalize_target (target):
    canonicalize = re.sub('[ \t\n]', '_', target)
    canonicalize = re.sub ('[^a-zA-Z]', '_', canonicalize)
    return canonicalize

def test_target (options, target, last_patch):
    canonicalize = canonicalize_target (target)
    release_hash = last_patch['release_hash']
    if try_checked_before (release_hash, canonicalize):
        print 'release has already been checked: ', release_hash 
        return None
        

    logfile = 'log/test-%(canonicalize)s.log' %  locals()
    cmd = "nice time %(target)s >& %(logfile)s" %  locals()
    print 'starting : ', cmd
    stat = os.system (cmd)
    base_tag = 'success-%(canonicalize)s-' % locals ()

    result = 'unknown'
    attachments = []
    
    body = read_tail (logfile, 10240).split ('\n')
    if stat: 
        diff = os.popen ('darcs diff -u --from-tag %s' % base_tag).read ()
        
        result = 'FAIL'
        attachments = ['error for %s\n\n%s' % (target,
                           '\n'.join (body[-0:])),
                       diff]
    else:
        tag = base_tag + last_patch['date']
        system ('darcs tag %s' % tag)
        result = "SUCCESS"
        if options.tag_repo:
            system ('darcs push -a -t %s %s ' % (tag, options.tag_repo))
            result += ', tagging with %s' % tag
            
        attachments = ['\n'.join (body[-10:])]

    set_checked_before (release_hash, canonicalize)
    return (result, attachments)
    
def send_message (options, msg):
    COMMASPACE = ', '
    msg['From'] = options.sender
    msg['To'] = COMMASPACE.join (options.address)
    connection = smtplib.SMTP (options.smtp)
    connection.sendmail (options.sender, options.address, msg.as_string ())

    
def main ():
    (options, args) = opt_parser().parse_args ()

    last_patch = read_last_patch ()
    release_hash = get_release_hash (options.check_files)
    last_patch['release_hash'] = release_hash
    release_id = '''

Last patch of this release:

%(local_date)s - %(author)s

    * %(name)s\n\n

MD5 of complete patch set: %(release_hash)s

''' % last_patch

    results = {}
    for a in args:
        result_tup = test_target (options, a, last_patch)
        if not result_tup:
            continue

        results[a] = result_tup
        
        (r, atts) = result_tup
        msg = result_message (options, atts,
                   subject="GUB Autobuild: %s %s" % (r, a))
        send_message (options, msg)                

        
    main = '\n'.join (['%s: %s' % (target, res)
             for (target, (res, atts)) in results.items ()])

    msg_body = [main, release_id]
    msg = result_message (options, msg_body,
               subject="GUB Autobuild: summary")
    
    if results:
        send_message (options, msg)
        
main()
