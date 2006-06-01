#!/usr/bin/python

import sys
import re
import os
import smtplib
import email.MIMEText
import email.Message
import email.MIMEMultipart
import optparse
import time

sys.path.insert (0, 'lib/')

import repository


################################################################
# utils.

def read_tail (file, amount=10240):
    f = open (file)
    f.seek (0, 2)
    length = f.tell()
    f.seek (- min (length, amount), 1)
    return f.read ()

def canonicalize_target (target):
    canonicalize = re.sub ('[ \t\n]', '_', target)
    canonicalize = re.sub ('[^a-zA-Z0-9-]+', '_', canonicalize)
    return canonicalize

class LogFile:
    def __init__ (self, name):
        self.file = open (name, 'a')
        self.prefix = 'test-gub.py[%d]: ' % os.getpid ()

    def log (self, msg):
        self.file.write ('%s%s\n' % (self.prefix, msg))
        self.file.flush ()
        
    def __del__ (self):
        self.log ('finished')

log_file = None

################################################################
#

def result_message (parts, subject='') :
    """Concatenate PARTS to a Message object."""
    
    if not parts:
        parts.append ('(empty)')
    
    parts = [email.MIMEText.MIMEText (p) for p in parts if p]

    msg = parts[0]
    if len (parts) > 1:
        msg = email.MIMEMultipart.MIMEMultipart ()
        for p in parts:
            msg.attach (p)
    
    msg['Subject'] = subject
    msg.epilogue = ''

    return msg

def opt_parser ():
    if os.environ.has_key ('EMAIL'):
        address = os.environ['EMAIL']
    else:
        try:
            address = '%s@localhost' % os.getlogin ()
        except OSError:
            address = 'root@localhost'
    
    p = optparse.OptionParser (usage="test-gub.py [options] command command ... ")
    p.add_option ('-t', '--to',
                  action='append',
                  dest='address',
                  default=[],
                  help='where to send error report')
    
    p.add_option ('--bcc',
                  action='append',
                  dest='bcc_address',
                  default=[],
                  help='BCC for error report')

    p.add_option ('-f', '--from',
                  action='store',
                  dest='sender',
                  default=address,
                  help='whom to list as sender')
    
    p.add_option ('--repository',
                  action="store",
                  dest="repository",
                  default=".",
                  help="repository directory")
    
    p.add_option ('--tag-repo',
                  action='store',
                  dest='tag_repo',
                  default='',
                  help='where to push success tags.')

    p.add_option ('--quiet',
                  action='store_true',
                  dest='be_quiet',
                  default=False,
                  help='only send mail when there was an error.')
    
    p.add_option ('--dependent',
                  action="store_true",
                  dest="is_dependent",
                  default=False,
                  help="test targets depend on each other")
                  
    p.add_option ('--posthook',
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

    db_file_name = 'test-done-%s.db' % canonicalize
    if repo.try_checked_before (release_hash, db_file_name):
        log_file.log ('release has already been checked in %s ' % db_file_name)
        return None

    logfile = 'test-%(canonicalize)s.log' %  locals ()
    logfile = os.path.join (repo.test_dir, logfile)
    
    cmd = "nice time %(target)s >& %(logfile)s" %  locals ()

    log_file.log (cmd)
    
    stat = os.system (cmd)
    base_tag = 'success-%(canonicalize)s-' % locals ()

    result = 'unknown'
    attachments = []
    
    body = read_tail (logfile, 10240).split ('\n')
    if stat:
        diff = repo.get_diff_from_tag (base_tag)

        result = 'FAIL'
        attachments = ['error for\n\n\t%s\n\n\n%s' % (target,
                                               '\n'.join (body[-0:])),
                       diff]
    else:
        tag = base_tag + canonicalize_target (last_patch['date'])
        repo.tag (tag)

        log_file.log ('tagging with %s' % tag)
        
        if options.tag_repo:
            repo.push (tag, options.tag_repo)
            
        result = "SUCCESS"
        attachments = ['success for\n\n\t%s\n\n%s'
                       % (target,
                          '\n'.join (body[-10:]))]

    log_file.log ('%s: %s' % (target, result))
    
    repo.set_checked_before (release_hash, db_file_name)
    return (result, attachments)
    
def send_message (options, msg):
    if not options.address:
        log_file.log ('No recipients for result mail')
        return
    
    COMMASPACE = ', '
    msg['From'] = options.sender
    msg['To'] = COMMASPACE.join (options.address)
    if options.bcc_address:
        msg['BCC'] = COMMASPACE.join (options.bcc_address)
        
    msg['X-Autogenerated'] = 'lilypond'
    connection = smtplib.SMTP (options.smtp)
    connection.sendmail (options.sender, options.address, msg.as_string ())

def main ():
    (options, args) = opt_parser ().parse_args ()

    global log_file
    log_file = LogFile ('log/test-gub.log')
    log_file.log (' *** Starting tests:\n  %s' % '\n  '.join (args))
    log_file.log (' *** %s' % time.ctime ())



    repo = repository.get_repository_proxy (options.repository)
    log_file.log ("Repository %s" % str (repo))
    
    last_patch = repo.read_last_patch ()
    
    release_hash = repo.get_release_hash ()
    last_patch['release_hash'] = release_hash
    release_id = '''

Last patch of this release:

%(patch_contents)s\n

MD5 of complete patch set: %(release_hash)s

''' % last_patch


    summary_body = '\n\n'
    results = {}
    failures = 0
    for a in args:
        result_tup = test_target (repo, options, a, last_patch)
        if not result_tup:
            continue

        (result, atts) = result_tup

        results[a] = result_tup
        
        success = result.startswith ('SUCCESS')
        if not success:
            failures += 1

        if not (options.be_quiet and success):
            msg = result_message (atts, subject="Autotester: %s %s" % (result, a))
            send_message (options, msg)

        summary_body += '%s\n  %s\n'  % (a, result)

    msg_body = [summary_body, release_id]
    msg = result_message (msg_body, subject="Autotester: summary")

    if (results
        and len (args) > 1
        and (failures > 0 or not options.be_quiet)):
        
        send_message (options, msg)

    if failures == 0 and results:
        for p in options.posthooks:
            os.system (p)

def test ():
    (options, args) = opt_parser ().parse_args ()

    repo = repository.get_repository_proxy (options.repository)
    print repo.read_last_patch ()
#    repository.tag ('testje')
#    repository.tag ('testje21')
#    repository.tag ('testje22')
    repo.get_diff_from_tag ('testje2')

if __name__ == '__main__':    
#    test ()
    main ()
