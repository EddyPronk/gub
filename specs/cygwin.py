import os
#
import cross
import download
import mingw
import xpm

def get_packages (settings):
	p = xpm.Cygwin_package_manager (settings)
        url = p.mirror + '/setup.ini'
	# FIXME: download/offline
	downloaddir = settings.downloaddir
	file = settings.downloaddir + '/setup.ini'
	if not os.path.exists (file):
		os.system ('wget -P %(downloaddir)s %(url)s' % locals ())
	cross_packs = [
		cross.Binutils (settings).with (version='2.16.1', format='bz2'),
		mingw.Gcc (settings).with (version='4.0.2', format='bz2',
	#	mingw.Gcc (settings).with (version='4.1-20060217', mirror=download.gcc_41, format='bz2',
					   depends=['binutils', 'cygwin']),
		]
	return cross_packs + p.get_packages (file)

def change_target_packages (packages):
	cross.change_target_packages (packages)
