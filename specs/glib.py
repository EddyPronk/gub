import download
import targetpackage

class Glib (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='2.9.5', mirror=download.gnome_213, format='bz2',
			   depends=['gettext'])

	def config_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()
		
	def install (self):
		targetpackage.Target_package.install (self)
		self.system ('rm %(install_root)s/usr/lib/charset.alias',
			     ignore_error=True)
		
class Glib__darwin (Glib):
	def configure (self):
		Glib.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')

class Glib__freebsd (Glib):
	def __init__ (self, settings):
		Glib.__init__ (self, settings)
		self.with (version='2.9.5', mirror=download.gnome_213, format='bz2',
			   depends=['gettext', 'libiconv', 'libtool'])

# FIXME: handling libtool+libiconv dependencies smarter (adding for
# mingw/freebsd or removing for darwin) would allow dropping quite some
# __platform overrides.
GLib__mingw = Glib__freebsd
