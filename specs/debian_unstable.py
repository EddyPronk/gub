
import xpm
def get_packages (settings):
	p = xpm.Debian_package_manager (settings.system_root,
					settings.os_interface)
	#p.register_packages ('Packages')
	#return p._packages
	file = '/var/lib/apt/lists/ftp.de.debian.org_debian_dists_unstable_main_binary-i386_Packages'
	#p.get_packages (file)
	x = p.get_packages (file)
	print `x[:2]`
	return x
