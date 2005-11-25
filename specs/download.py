import string
import re


def set_download (package, version, format, url_template):
	d = package.package_dict ()
	d.update (locals())
	package.url = url_template % d
	

def set_gtk_download (package, version, format):
	set_download (package, version, format, 'ftp://ftp.gtk.org/pub/gtk/v%(gtk_version)s/%(name)s-%(version)s.tar.%(format)s')
	

def set_gnu_download (package, version, format):
	# base = 'ftp://dl.xs4all.nl/pub/mirror/gnu'
	base = 'ftp://sunsite.dk/pub/gnu'
	
	set_download (package, version, format, base + '/%(name)s/%(name)s-%(version)s.tar.%(format)s')


