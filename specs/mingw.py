import os
import re

import download
import framework
import gub

class Binutils (framework.Binutils):
	pass

class Gcc (framework.Gcc):
	def patch (self):
		# FIXME: dependencies are broken here?  MUST
		# install runtime binaries (mingw-runtime, w32api)
		# manually before we get here.
		self.system ('''
mkdir -p %(tooldir)s/%(target_architecture)s
tar -C %(system_root)s/usr -cf- include lib | tar -C %(tooldir)s/%(target_architecture)s -xf-
''')


def get_packages (settings):
	return (
		framework.Pkg_config (settings).with (version="0.20",
						      mirror=download.freedesktop),
		Binutils (settings).with (version='2.16.1', format='bz2'),
#		Gcc (settings).with (version='4.0.2', mirror=download.gcc, format='bz2'),
		Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2',
				     depends=['binutils']
				     ),
		)

	
def change_target_packages (packages):
	for p in packages:
		gub.change_target_dict (p,
					{
			'DLLTOOL': '%(tool_prefix)sdlltool',
			'DLLWRAP': '%(tool_prefix)sdllwrap',
			})
