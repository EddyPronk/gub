import os
#
import cross
import xpm

def get_packages (settings):
	p = xpm.Debian_package_manager (settings)
        url = p.mirror + '/dists/unstable/main/binary-i386/Packages.gz'
	# FIXME: download/offline
	downloaddir = settings.downloaddir
	file = settings.downloaddir + '/Packages'
	if not os.path.exists (file):
		os.system ('wget -P %(downloaddir)s %(url)s' % locals ())
		os.system ('gunzip  %(file)s.gz' % locals ())
	return p.get_packages (file)

def change_target_packages (packages):
	cross.change_target_packages (packages)
