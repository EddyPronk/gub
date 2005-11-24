
import re
import gub

class  Libtool (gub.Target_package):
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)
		self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/libtool/libtool-1.5.20.tar.gz'
		#self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/libtool/libtool-1.5.10.tar.gz'

 	def installdir (self):
 		return self.settings.systemdir
	
class  Gettext (gub.Target_package):
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)
		self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/gettext/gettext-0.10.40.tar.gz'
		self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/gettext/gettext-0.14.5.tar.gz'

	def configure_cache_overrides (self, str):
		str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		return str
	
	def configure_command (self):
		cmd = gub.Target_package.configure_command (self)
		cmd += ' --disable-csharp '
		return cmd
	
def get_packages (settings):
	return [
		Libtool (settings),
		Gettext (settings),
		]
