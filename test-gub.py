import smtplib
import os
import time

server = "smtp.xs4all.nl"
sender = "hanwen@xs4all.nl"
addresses = [
	'janneke@gnu.org',
	'hanwen@xs4all.nl']

def tag_name ():
	(year, month, day, hours,
	 minutes, seconds, weekday,
	 day_of_year, dst) = time.localtime()
	
	return "success-%(year)d-%(month)d-%(day)d" % locals()

def system (cmd):
	print cmd
	return os.system (cmd)

stat = os.system ("make distclean")
#stat = os.system ("nice make all 2>&1 | tee test-gub.log")

stat = os.system ("nice make all >& test-gub.log")
if stat:
	f = open ('test-gub.log')
	f.seek (0, 2)
	length = f.tell()
	f.seek (- min (length, 10240), 1)
	body = f.read ()

	connection = smtplib.SMTP (server)
	subject = 'GUB Autobuild: FAIL'
	body = 'Subject: %s\n\n' % subject +  body
	connection.sendmail (sender, addresses, body)

	## TODO: include diff from last known working
else:
	#	system ('darcs tag %s' % tag_name ()) 
	pass
	## TODO: push the tag
	
	
