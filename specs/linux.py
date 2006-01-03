import os
import re

import cross
import download
import framework
import gub

class Gcc (cross.Gcc):
	def configure_command (self):
		cmd = cross.Gcc.configure_command (self)
		cmd = re.sub ('--with-sysroot=[^ ]+',
			       '--with-sysroot=/', cmd)

		return cmd
		
def get_packages (settings):
	packages = [Gcc (settings).with (version='3.4.5', mirror = download.gcc, format='bz2',
					 depends=["binutils"]),
		    cross.Binutils (settings).with (version='2.16.1', format='bz2')]
	
	return packages



def change_target_packages (packages):
	cross.change_target_packages (packages)
	
	for p in packages:
		gub.change_target_dict (p,
				    {'CC': 'apgcc',
				     'CXX': 'apg++',
				     "LD": 'ld --as-needed',
				     'LDFLAGS': '-Wl,--as-needed',
#				     'APBUILD_CC': 'gcc-3.4',
#				     'APBUILD_CXX1': 'g++-3.4',
				     'APBUILD_CC': '%(target_architecture)s-gcc',
				     'APBUILD_CXX1': '%(target_architecture)s-g++',
				     })
