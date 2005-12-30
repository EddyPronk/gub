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


class Redefine_package_for_linux:
	"""Override target_dict method of a Package."""
	
	def __init__ (self, package):
		self._package = package
		self._target_dict = package.target_dict
		
	def target_dict (self, env={}):
		dict = self._target_dict ()

		dict['CC'] = 'apgcc'
		dict['CXX'] = 'apg++'
		dict['LD'] = 'ld --as-needed'
		dict['LDFLAGS']  = '-Wl,--as-needed'

		# FIXME: some libraries, gettext eg, do not build with
		# gcc-4.0.
		# FIXME: CXX1 for < 3.4 abi, CXX2 for >= 3.4 abi
		# but APBUILD_CXX2 apg++ --version yields 4.0.3 :-(
	
#		dict['APBUILD_CC'] = 'gcc-3.4'
#		dict['APBUILD_CXX1'] = 'g++-3.4'
		dict['APBUILD_CC'] = '%(target_architecture)s-gcc'
		dict['APBUILD_CXX1'] = '%(target_architecture)s-g++'

		dict.update (env)
		return dict


def change_target_packages (packages):
	for p in packages:
		redefiner = Redefine_package_for_linux (p)
		p.target_dict = redefiner.target_dict
	
