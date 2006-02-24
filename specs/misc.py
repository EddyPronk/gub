# misc utils
import re
import string
import sys

def join_lines (str):
	return str.replace ('\n', ' ')

def grok_sh_variables (file):
	dict = {}
	for i in open (file).readlines ():
		m = re.search ('^(\w+)\s*=\s*(\w*)', i)
		if m:
			k = m.group (1)
			s = m.group (2)
			dict[k] = s
	return dict

def version_to_string (t):
	def itoa (x):
		if type (x) == int:
			return "%d" % x
		return x
	return '%s-%s' % (string.join (map (itoa, t[:-1]), '.'), t[-1])

def split_version (s):
	m = re.match ('^(([0-9].*)-([0-9]+))$', s)
	if m:
		return m.group (2), m.group (3)
	return s, '0'

def string_to_version (s):
	s = re.sub ('([^0-9][^0-9]*)', ' \\1 ', s)
	s = re.sub ('[ _.-][ _.-]*', ' ', s)
	s = s.strip ()
	def atoi (x):
		if re.match ('^[0-9]+$', x):
			return string.atoi (x)
		return x
	return tuple (map (atoi, (string.split (s, ' '))))

def split_ball (s):
	m = re.match ('^(.*?)-([0-9].*(-[0-9]+)?)(\.[a-z]*)?(\.tar\.(bz2|gz)|\.gub)$', s)
	if not m:
		## FIXME, not an error if not a ball...
		##sys.stderr.write ('split_ball: ' + s)
		##sys.stderr.write ('\n')
		return (s[:2], (0, 0), 'gz')
	return (m.group (1), string_to_version (string.join (split_version (m.group (2)), '-')), m.group (6))

def list_append (lists):
	return reduce (lambda x,y: x+y, lists, [])

def uniq (list):
	u = []
	done = {}
	for e in list:
		if done.has_key (e):
			continue

		done[e] = 1
		u.append (e)

	return u



def intersect (l1, l2):
	return [l for l in l1 if l in l2]

def bind_method (func, self):
	return lambda *args: func (self, *args)


def tar_compression_flag (ball):
	compression_flag = ''
	if ball.endswith ('bz2'):
		compression_flag = 'j'
	if ball.endswith ('gz'):
		compression_flag = 'z'
	return compression_flag


def file_is_newer (f1, f2):
	return (not os.path.exists (f2)
		or os.stat (f1).st_mtime > os.stat (f2).st_mtime)

