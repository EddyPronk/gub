import gub
import download
import misc

class Tool_package (gub.Package):
	def configure_command (self):
		return (gub.Package.configure_command (self)
			+ misc.join_lines ('''
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

class Guile (Tool_package):
	pass

class Gmp (Tool_package):
	pass

def get_packages (settings):
	packages_dict = {
		'linux': [],
		'darwin': [
		Pkg_config (settings).with (version="0.20",
					    mirror=download.freedesktop),
		Guile (settings).with (version='1.6.7',
				       mirror=download.gnu, format='gz',
 				       depends=[]
				       ),
		]}


	return packages_dict[settings.build_platform]


