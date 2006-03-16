import os
import re

import cross
import download
import gub
import linux
import misc
import targetpackage

class Arm_runtime (gub.Binary_package, gub.Sdk_package):
	pass

def get_cross_packages (settings):
	return (
		linux.Libc6 (settings).with (version='2.2.5-11.8', mirror=download.glibc_deb, format='deb'),
		linux.Libc6_dev (settings).with (version='2.2.5-11.8', mirror=download.glibc_deb, format='deb'),
		linux.Linux_kernel_headers (settings).with (version='2.6.13+0rc3-2', mirror=download.lkh_deb, format='deb'),
		#Arm_runtime (settings).with (version='4.10-2', mirror=download.jantien),
		cross.Binutils (settings).with (version='2.16.1', format='bz2'),
#		cross.Gcc (settings).with (version='4.0.2', mirror=download.gcc, format='bz2', depends=['binutils']),
		cross.Gcc (settings).with (version='4.1.0', mirror=download.gcc_41, format='bz2', depends=['binutils']),
		)


def change_target_packages (packages):
	cross.change_target_packages (packages)
	cross.set_framework_ldpath ([p for p in packages.values () if isinstance (p, targetpackage.Target_package)])
	return packages
