import glob
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

class Libc6 (gub.Binary_package, gub.Sdk_package):
	pass

class Libc6_dev (gub.Binary_package, gub.Sdk_package):
	def untar (self):
		gub.Binary_package.untar (self)
		# Ugh, rewire absolute names and symlinks.
		# Better to create relative ones?
		self.file_sub ([(' /', ' %(system_root)s/')],
			       '%(srcdir)s/root/usr/lib/libc.so')
		for i in glob.glob (self.expand ('%(srcdir)s/root/usr/lib/lib*.so')):
			if os.path.islink (i):
				s = os.readlink (i)
				if s.startswith ('/'):
					os.remove (i)
					os.symlink (self.settings.system_root
						    + s, i)

class Linux_kernel_headers (gub.Binary_package, gub.Sdk_package):
	pass

def get_packages (settings):
	packages = [
		Libc6 (settings).with (version='2.2.5-11.8', mirror=download.glibc_deb, format='deb'),
		Libc6_dev (settings).with (version='2.2.5-11.8', mirror=download.glibc_deb, format='deb'),
		Linux_kernel_headers (settings).with (version='2.6.13+0rc3-2', mirror=download.lkh_deb, format='deb'),
		cross.Binutils (settings).with (version='2.16.1', format='bz2'),
		cross.Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2',
					   depends=['binutils']),
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
