import smtplib.py
import os
import time

server = "smtp.xs4all.nl"
sender = "hanwen@xs4all.nl"
dest = ['janneke@gnu.org',
	'hanwen@xs4all.nl']

def tag_name ():
	(year, month, day, hours,
	 minutes, seconds, weekday,
	 day_of_year, dst) = localtime()
	
	return "success-%(year)d-%(month)d-%(day)d" % locals()

def system (cmd):
	print cmd
	return os.system (cmd)

def mail_to (addresses,
	     body,
	     subject =''):
	

stat = os.system ("make distclean")
stat = os.system ("make all 2>&1 | tee test-gub.log")
if stat:
	f = open ('test-gub.log')
	f.seek (2, -10240)
	body = f.read ()

	connection = smtplib.SMTP (server)
	body = 'Subject: %s\n\n' % subject +  body
	connection.sendmail (sender, addresses, body)


	## TODO: include diff from last known working
else:
	system ('darcs tag %s' % tag_name ()) 

	## TODO: push the tag 
	
