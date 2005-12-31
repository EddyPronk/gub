import re
import os
import framework
import download

class Gcc (framework.Gcc):
	def configure_command (self):
		cmd = framework.Gcc.configure_command (self)
		cmd = re.sub ('--with-sysroot=[^ ]+',
			       '--with-sysroot=/', cmd)

		return cmd
		
def get_packages (settings):
	packages = [Gcc (settings).with (version='3.4.5', mirror = download.gcc, format='bz2',
					 depends=["binutils"]),
		    framework.Binutils (settings).with (version='2.16.1', format='bz2')]
	
	return packages


def change_target_packages (packages):
	for p in packages:
		change_target_dict (p,
				    {'CC': 'apgcc',
				     'CXX': 'apg++',
				     "LD": 'ld --as-needed',
				     'LDFLAGS': '-Wl,--as-needed',
#				     'APBUILD_CC': 'gcc-3.4',
#				     'APBUILD_CXX1': 'g++-3.4',
				     'APBUILD_CC': '%(target_architecture)s-gcc',
				     'APBUILD_CXX1': '%(target_architecture)s-g++',
				     'LIBRARY_PATH': '%(system_root)s/usr/lib:%(system_root)s/usr/bin'})
