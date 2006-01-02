import smtplib
import os
import time
import email.MIMEText
import email.Header
import email.Message
import email.MIMEMultipart

#server = "smtp.xs4all.nl"
server = "localhost"
sender = "hanwen@xs4all.nl"
addresses = [
#	'janneke@gnu.org',
# 	'hanwen@xs4all.nl',
	
	'hanwen@localhost',
	]

def tag_name ():
	(year, month, day, hours,
	 minutes, seconds, weekday,
	 day_of_year, dst) = time.localtime()
	
	return "success-%(year)d-%(month)d-%(day)d" % locals()

def system (cmd):
	print cmd
	return os.system (cmd)

COMMASPACE = ', '
def fail_message (log, diff) :
	msg = email.MIMEMultipart.MIMEMultipart()
	msg['Subject'] = email.Header.Header( 'GUB Autobuild: FAIL')

	msg.preamble = ("Oops, our GUB build failed")
	msg.attach (email.MIMEText.MIMEText (log))

	if diff: 
		msg.attach (email.MIMEText.MIMEText (diff))
	msg.epilogue = ''
	
	msg['From'] = sender
	msg['To'] = COMMASPACE.join (addresses)


	return msg.as_string ()
	
stat = system ("make distclean")
stat = os.system ("nice make all >& test-gub.log")
if stat:
	f = open ('test-gub.log')
	f.seek (0, 2)
	length = f.tell()
	f.seek (- min (length, 10240), 1)
	body = f.read ()

	diff = os.popen ('darcs diff -u --from-tag success-').read ()

	msg = fail_message (body, diff)
	
	connection = smtplib.SMTP (server)
	connection.sendmail (sender, addresses, msg)

	## TODO: include diff from last known working
else:
	name = tag_name()
	system ('darcs tag %s' % name)
	system ('darcs push -t %s ' % name)
	
	
