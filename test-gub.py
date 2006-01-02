import smtplib
import os
import time
import email.MIMEText
import email.Header
import email.Message
import email.MIMEMultipart
import optparse

def tag_name ():
	(year, month, day, hours,
	 minutes, seconds, weekday,
	 day_of_year, dst) = time.localtime()
	
	return "success-%(year)d-%(month)d-%(day)d" % locals()

def system (cmd):
	print cmd
	return os.system (cmd)

COMMASPACE = ', '
def fail_message (options, log, diff) :
	msg = email.MIMEMultipart.MIMEMultipart()
	msg['Subject'] = email.Header.Header( 'GUB Autobuild: FAIL')

	msg.preamble = ("\nOops, our GUB build failed\n\n\n")
	msg.attach (email.MIMEText.MIMEText (log))

	if diff: 
		msg.attach (email.MIMEText.MIMEText (diff))
	msg.epilogue = ''
	
	msg['From'] = options.sender
	msg['To'] = COMMASPACE.join (options.address)
	
	return msg.as_string ()

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


stat = system ("make distclean")
stat = os.system ("nice make all >& test-gub.log")
if stat:
	f = open ('test-gub.log')
	f.seek (0, 2)
	length = f.tell()
	f.seek (- min (length, 10240), 1)
	body = f.read ()

	diff = os.popen ('darcs diff -u --from-tag success-').read ()

	msg = fail_message (options, body, diff)
	
	connection = smtplib.SMTP (options.smtp)
	connection.sendmail (options.sender, options.address, msg)

	## TODO: include diff from last known working
else:
	name = tag_name()
	system ('darcs tag %s' % name)
	system ('darcs push -t %s ' % name)
	
	
