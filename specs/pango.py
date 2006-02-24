import shutil

import download
import targetpackage

class Pango (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='1.11.2', mirror=download.gnome_213, format='bz2',
			   depends=['freetype', 'fontconfig', 'glib', 'libtool'])

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
		self.system ('cd %(srcdir)s && patch --force -p1 < %(patchdir)s/pango-env-sub')

		## ugh, already fixed in Pango CVS.
		f = open (self.expand ('%(srcdir)s/pango/pango.def'), 'a')
		f.write ('	pango_matrix_get_font_scale_factor\n')

	def fix_modules (self):
		etc = self.expand ('%(install_root)s/usr/etc/pango')
		for a in glob.glob (etc + '/*'):
			self.file_sub ([('/usr/', '$PANGO_PREFIX/')],
				       a)

		open (etc + '/pangorc', 'w').write (
		'''[Pango]
ModuleFiles = "$PANGO_PREFIX/etc/pango/pango.modules"
ModulesPath = "$PANGO_PREFIX/lib/pango/1.4.0/modules"
''')
		shutil.copy2 (self.expand ('%(patchdir)s/pango.modules'),
			      etc)

class Pango__mingw (Pango):
	def __init__ (self, settings):
		Pango.__init__ (self, settings)
		self.with (version='1.11.2', mirror=download.gnome_213, format='bz2',
			   depends=['freetype', 'fontconfig', 'glib', 'libiconv', 'libtool'])

	def install (self):
		targetpackage.Target_package.install (self)
		self.system ('mkdir -p %(install_root)s/usr/etc/pango')
		self.dump ('''[Pango]
ModulesPath = "@INSTDIR@\\usr\\lib\\pango\\1.4.0\\modules"
ModuleFiles = "@INSTDIR@\\usr\\etc\\pango\\pango.modules"
#[PangoX]
#AliasFiles = "@INSTDIR@\\usr\\etc\\pango\\pango.modules\\pangox.aliases"
''',
			   '%(install_root)s/usr/etc/pango/pangorc.in')

		# pango.modules can be generated if we have the linux
		# installer built

# cd target/linux/installer/usr/lib/lilypond/noel/root
# PANGO_RC_FILE=$(pwd)/etc/pango/pangorc bin/pango-querymodules > etc/pango/pango.modules
		self.system ('cp %(nsisdir)s/pango.modules.in %(install_root)s/usr/etc/pango/pango.modules.in')

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

	def install (self):
		Pango.install (self)
		self.fix_modules ()

class Pango__darwin (Pango):
	def configure (self):
		Pango.configure (self)
		self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
			       '%(builddir)s/libtool')

	def install (self):
		targetpackage.Target_package.install (self)		
		self.fix_modules ()

class Pango__freebsd (Pango):
	def __init__ (self, settings):
		Pango.__init__ (self, settings)
		self.with (version='1.11.2', mirror=download.gnome_213, format='bz2',
			   depends=['freetype', 'fontconfig', 'glib', 'libiconv', 'libtool'])
