import os
import re

import download
import framework
import gub
import mingw

class Binutils (mingw.Binutils):
	def configure_command (self):
		# Add --program-prefix, otherwise we get
		# i686-freebsd-FOO iso i686-freebsd4-FOO.
		return (mingw.Binutils.configure_command (self)
			+ gub.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Gcc (mingw.Gcc):
	def configure_command (self):
		# Add --program-prefix, otherwise we get
		# i686-freebsd-FOO iso i686-freebsd4-FOO.
		return (mingw.Gcc.configure_command (self)
			+ gub.join_lines ('''
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
	pass
