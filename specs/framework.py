import re
import gub
import download

class Libtool (gub.Target_package):
	pass

class Gettext (gub.Target_package):
	def configure_cache_overrides (self, str):
		str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		return str
	
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'
	
class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def configure_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

def get_packages (settings, platform):
	mingw = ( platform == 'mingw')
	mac = (platform == 'mac')

	packages = []
	if mingw:
		libtool = Libtool (settings)
		download.set_gnu_download (libtool, '1.5.20', 'gz')
		packages.append (libtool)
		
	gettext = Gettext (settings)
	if platform == 'mingw':
		download.set_gnu_download (gettext, '0.14.5', 'gz')
	elif platform == 'mac':
		download.set_gnu_download (gettext, '0.10.40', 'gz')
	packages.append (gettext)

	if platform == 'mingw':
		libiconv = Libiconv (settings)
		download.set_gnu_download (libiconv, '2.8.4', 'gz')
		packages.append (libiconv)

	return packages
