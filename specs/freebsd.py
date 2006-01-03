import os
import re

import cross
import download
import framework
import gub
import misc

class Binutils (cross.Binutils):
	def configure_command (self):
		# Add --program-prefix, otherwise we get
		# i686-freebsd-FOO iso i686-freebsd4-FOO.
		return (cross.Binutils.configure_command (self)
			+ misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Gcc (cross.Gcc):
	def configure_command (self):
		# Add --program-prefix, otherwise we get
		# i686-freebsd-FOO iso i686-freebsd4-FOO.
		return (cross.Gcc.configure_command (self)
			+ misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

def get_packages (settings):
	return (
		Binutils (settings).with (version='2.16.1', format='bz2'),
#		Gcc (settings).with (version='4.0.2', mirror=download.gcc, format='bz2'),
		Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2', depends=['binutils']
				     ),
		)

def change_target_packages (packages):
	cross.change_target_packages (packages)
	
