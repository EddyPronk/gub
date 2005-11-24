
import re
import gub

class Libtool (gub.Target_package):
	def __init__ (self, settings, version):
		gub.Package.__init__ (self, settings, version)

class Gettext (gub.Target_package):
	def __init__ (self, settings, version):
		gub.Package.__init__ (self, settings, version)

	def configure_cache_overrides (self, str):
		str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		return str
	
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'
	
class Libiconv (gub.Target_package):
	def __init__ (self, settings, version):
		gub.Package.__init__ (self, settings, version, gub.gnu_org_mirror)

class Glib (gub.Target_package):
	def __init__ (self, settings, version):
		gub.Package.__init__ (self, settings, version, gub.gtk_mirror)

	def configure_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

def get_packages (settings):
	return [
		Libtool (settings, '1.5.20'),
		Gettext (settings, '0.14.5'),
		Libiconv (settings, '1.9.2'),
		Glib (settings, '2.8.4'),
		]
