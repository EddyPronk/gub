#!/usr/bin/python

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
def try_checked_before (hash):
	if not os.path.isdir ('test'):
		os.makedirs ('test')
		
	db = dbhash.open ('test/gub-done.db', 'c')
	was_checked = db.has_key (hash)
	db[hash] = '1'
	db.close ()
	return was_checked

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

def result_message (options, subject, parts) :
	"""Concatenate PARTS to a Message object."""
	
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

################################################################
# main


msg = None
last_patch = read_last_patch()

release_hash = md5.new ()
release_hash.update (open ('_darcs/inventory').read())
release_hash = release_hash.hexdigest() 


(options, args) = opt_parser().parse_args ()

if try_checked_before (release_hash):
	print 'release has already been checked: ', release_hash 
	sys.exit (0)

last_patch['release_hash'] = release_hash
release_id = '''
Last patch of this release:

%(local_date)s - %(author)s

	* %(name)s\n\n

MD5 of inventory: %(release_hash)s

''' % last_patch




stat = system ("make distclean")
stat = os.system ("nice make all >& test-gub.log")


if stat: 
	f = open ('test-gub.log')
	f.seek (0, 2)
	length = f.tell()
	f.seek (- min (length, 10240), 1)
	body = f.read ()

	diff = os.popen ('darcs diff -u --from-tag success-').read ()

	msg = result_message (options, 'FAIL', [release_id,
						body, diff])
else:
	tag = 'success-%(date)s' % last_patch
	system ('darcs tag %s' % tag)
	system ('darcs push -a -t %s ' % tag)

	msg = result_message (options, 'SUCCESS',
			      [release_id,
			       "Tagging with %s\n\n" % tag])


COMMASPACE = ', '
msg['From'] = options.sender
msg['To'] = COMMASPACE.join (options.address)
connection = smtplib.SMTP (options.smtp)
connection.sendmail (options.sender, options.address, msg.as_string ())
	
	
