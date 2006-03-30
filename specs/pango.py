import glob
import os
import shutil

import download
import misc
import targetpackage

class Pango (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='1.12.0',
			   mirror=download.gnome_214,
			   format='bz2',
			   depends=['freetype', 'fontconfig', 'glib', 'libiconv', 'libtool'])

	def configure_command (self):
		return targetpackage.Target_package.configure_command (self) \
		       + misc.join_lines ('''
--without-x
--without-cairo
''')

	def configure (self):
		targetpackage.Target_package.configure (self)		
		self.update_libtool ()
	def patch (self):
		targetpackage.Target_package.patch (self)
		self.system ('cd %(srcdir)s && patch --force -p1 < %(patchdir)s/pango-substitute-env.patch')

	def fix_modules (self):
		etc = self.expand ('%(install_root)s/usr/etc/pango')
		self.system ('mkdir -p %(etc)s' , locals ())
		for a in glob.glob (etc + '/*'):
			self.file_sub ([('/usr/', '$PANGO_PREFIX/')],
				       a)

		open (etc + '/pangorc', 'w').write (
		'''[Pango]
ModuleFiles = $PANGO_PREFIX/etc/pango/pango.modules
ModulesPath = $PANGO_PREFIX/lib/pango/1.5.0/modules
''')
		shutil.copy2 (self.expand ('%(sourcefiledir)s/pango.modules'),
			      etc)


	def install (self):
		targetpackage.Target_package.install (self)		
		self.fix_modules ()

class Pango__linux (Pango):
	def untar (self):
		Pango.untar (self)
		# FIXME: --without-cairo switch is removed in 1.10.1,
		# pango only compiles without cairo if cairo is not
		# installed linkably on the build system.  UGH.
		self.file_sub ([('(have_cairo[_a-z0-9]*)=true', '\\1=false'),
				('(cairo[_a-z0-9]*)=yes', '\\1=no')],
			       '%(srcdir)s/configure')
		os.chmod ('%(srcdir)s/configure' % self.get_substitution_dict (), 0755)

## placeholder, don't want plain Pango for freebsd. 
class Pango__freebsd (Pango__linux):
	pass

class Pango__darwin (Pango):
	def configure (self):
		Pango.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')
