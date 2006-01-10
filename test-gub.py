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
def try_checked_before (hash, canonicalized_target):
	if not os.path.isdir ('test'):
		os.makedirs ('test')

	db_file = 'log/gub-done-%s.db' % canonicalized_target
	print 'Using database ', db_file
	
	db = dbhash.open (db_file, 'c')
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
	
def get_release_hash ():
	xml_string = os.popen ('darcs changes --xml').read()
	dom = xml.dom.minidom.parseString(xml_string)
	patches = dom.documentElement.getElementsByTagName('patch')
	patches = [p for p in patches if not re.match ('^TAG', xml_patch_name (p))]

	release_hash = md5.new ()
	for p in patches:
		release_hash.update (p.toxml ())
		
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
		sys.exit (0)


	logfile = 'log/test-%(canonicalize)s.log' %  locals()
	cmd = "nice time %(target)s >& %(logfile)s" %  locals()
	print 'starting : ', cmd
	stat = os.system (cmd)
	base_tag = 'success-%(canonicalize)s-' % locals ()

	result = 'unknown'
	attachments = []
	
	if stat: 
		body = read_tail (logfile, 10240)
		diff = os.popen ('darcs diff -u --from-tag %s' % base_tag).read ()
		
		result = 'FAIL'
		attachments = ['error for %s\n\n%s' % (target, '\n'.join (body.split ('\n')[-45:])),
			       diff]
	else:
		tag = base_tag + last_patch['date']
		system ('darcs tag %s' % tag)
		system ('darcs push -a -t %s ' % tag)
		result = "SUCCESS, tagging with %s\n\n" % tag
		

	return (result, attachments)
	
def send_message (options, msg):
	COMMASPACE = ', '
	msg['From'] = options.sender
	msg['To'] = COMMASPACE.join (options.address)
	connection = smtplib.SMTP (options.smtp)
	connection.sendmail (options.sender, options.address, msg.as_string ())

	
def main ():
	(options, args) = opt_parser().parse_args ()

	last_patch = read_last_patch()
	release_hash = get_release_hash ()
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
		results[a] = result_tup
		
		(r, atts) = result_tup
		msg = result_message (options, atts, subject="GUB Autobuild: %s %s" % (r, a))
		send_message (options, msg)		

	main = '\n\n'.join (['%s: %s' % (target, res) for (target, (res, atts)) in results.items()])

	msg_body = [main, release_id]
	msg = result_message (options, msg_body, subject="GUB Autobuild: summary")
	
	send_message (options, msg)
main()
