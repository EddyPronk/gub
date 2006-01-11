# misc utils
import re

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

def split_version (s):
	m = re.match ('^(([0-9].*)-([0-9]+))$', s)
	if m:
		return m.group (2), m.group (3)
	return s, '0'

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


