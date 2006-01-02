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


release_hash = md5.new ()
release_hash.update (open ('_darcs/inventory').read())
release_hash = release_hash.hexdigest() 

## TODO: should incorporate checksum of lilypond checkout too.
def try_checked_before (hash):
	if not os.path.isdir ('test'):
		os.makedirs ('test')
		
	db = dbhash.open ('test/gub-done.db', 'c')
	was_checked = db.has_key (hash)
	db[hash] = '1'
	db.close ()
	return was_checked

def tag_name ():
	(year, month, day, hours,
	 minutes, seconds, weekday,
	 day_of_year, dst) = time.localtime()
	
	return "success-%(year)d-%(month)d-%(day)d-%(hours)dh%(minutes)dm" % locals()

def system (cmd):
	print cmd
	stat = os.system (cmd)
	if stat:
		raise 'Command failed', stat

def result_message (options, subject, parts) :
	if not parts:
		parts.append ('(empty)')
	
	parts = [email.MIMEText.MIMEText (p) for p in parts if p]

	msg = parts[0]
	if len (parts) > 1:
		msg = email.MIMEMultipart.MIMEMultipart()
		for p in parts:
			msg.attach (p)
	
	msg['Subject'] = 'GUB Autobuild: %s' % subject

	msg.epilogue = ''

	return msg

def opt_parser ():
	p = optparse.OptionParser()
	p.add_option ('-t', '--to',
		      action ='append',
		      dest = 'address',
		      default = [],
		      help = 'where to send error report')
	p.add_option ('-f', '--from',
		      action ='store',
		      dest = 'sender',
		      default = os.environ['EMAIL'],
		      help = 'whom to list as sender')
	p.add_option ('-s', '--smtp',
		      action ='store',
		      dest = 'smtp',
		      default = 'localhost',
		      help = 'SMTP server to use.')

	return p

(options, args) = opt_parser().parse_args ()

if try_checked_before (release_hash):
	print 'release has already been checked: ', release_hash 
	sys.exit (0)

stat = system ("make distclean")
stat = os.system ("nice make all >& test-gub.log")
msg = None
if stat:
	f = open ('test-gub.log')
	f.seek (0, 2)
	length = f.tell()
	f.seek (- min (length, 10240), 1)
	body = f.read ()

	diff = os.popen ('darcs diff -u --from-tag success-').read ()

	msg = result_message (options, 'FAIL', ['md5 of inventory: %s\n\n' %  release_hash, body, diff])
else:
	name = tag_name()
	system ('darcs tag %s' % name)
	system ('darcs push -t %s ' % name)

	msg = result_message (options, 'SUCCESS',
			      ['md5 of inventory: %s\n\n' %  release_hash,
			       "Tagging with %s\n\n" % name])


COMMASPACE = ', '
msg['From'] = options.sender
msg['To'] = COMMASPACE.join (options.address)
connection = smtplib.SMTP (options.smtp)
connection.sendmail (options.sender, options.address, msg.as_string ())
	
	
