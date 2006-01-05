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

class Libc6 (gub.Binary_package):
	pass

class Libc6_dev (gub.Binary_package):
	pass

#[   ] libc6-pic_2.2.5-11.8_i386.deb               12-Jan-2005 08:32   822k
#[   ] libc6-dev_2.2.5-11.8_i386.deb               12-Jan-2005 08:32   2.3M
#[   ] libc6_2.2.5-11.8_i386.deb                   12-Jan-2005 08:32   3.2M

def get_packages (settings):
	packages = [
		Libc6 (settings).with (version='2.2.5-11.8', mirror=download.glibc_deb, format='deb'),
		Libc6_dev (settings).with (version='2.2.5-11.8', mirror=download.glibc_deb, format='deb'),
		cross.Binutils (settings).with (version='2.16.1', format='bz2'),
		cross.Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2',				     depends=['binutils', 'libc6', 'libc6-dev']),
		]
	return packages



def change_target_packages (packages):
	cross.change_target_packages (packages)
	
	for p in packages:
		gub.change_target_dict (p,
				    {'CC': 'apgcc',
				     'CXX': 'apg++',
				     'LD': 'ld --as-needed',
				     'LDFLAGS': '-Wl,--as-needed',
#				     'APBUILD_CC': 'gcc-3.4',
#				     'APBUILD_CXX1': 'g++-3.4',
				     'APBUILD_CC': '%(target_architecture)s-gcc',
				     'APBUILD_CXX1': '%(target_architecture)s-g++',
				     })
