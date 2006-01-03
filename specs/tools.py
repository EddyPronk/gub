import gub
import download
import misc

class Tool_package (gub.Package):
	def configure_command (self):
		return (gub.Package.configure_command (self)
			+ misc.join_lines ('''
--program-prefix=%(target_architecture)s-
--prefix=%(tooldir)s/
'''))

	def install_command (self):
		return '''make DESTDIR=%(install_root)s prefix=/usr install'''

	def package (self):
		self.system ('''
tar -C %(install_root)s/usr -zcf %(gub_uploads)s/%(gub_name)s .
''')

class Pkg_config (Tool_package):
	pass

def get_packages (settings):
	return (
		Pkg_config (settings).with (version="0.20",
						  mirror=download.freedesktop),
	
		)
