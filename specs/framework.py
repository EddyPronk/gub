
import re
import gub

class  Gettext (gub.Package):
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)
		self.url = 'ftp://dl.xs4all.nl/pub/mirror/gnu/gettext/gettext-0.14.tar.gz'

	def install_dir (self):
		return self.settings.installdir
	
def get_packages (settings):
	return [Gettext (settings),
		]
