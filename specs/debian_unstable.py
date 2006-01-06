import cross
import xpm

def get_packages (settings):
	p = xpm.Debian_package_manager (settings)
	# ugh
	file = '/var/lib/apt/lists/ftp.de.debian.org_debian_dists_unstable_main_binary-i386_Packages'
	return p.get_packages (file)

def change_target_packages (packages):
	cross.change_target_packages (packages)
