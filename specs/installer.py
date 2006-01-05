import os
import re
#
import darwintools
import context
from context import subst_method

class Installer (context.Os_context_wrapper):
	def __init__ (self, settings):
		context.Os_context_wrapper.__init__ (self, settings)
		
		self.settings = settings
		self.strip_command = '%(crossprefix)s/bin/%(target_architecture)s-strip' 
		self.no_binary_strip = []

	@context.subst_method
        def name (self):
		return 'lilypond'

	@context.subst_method
	def version (self):
		return self.settings.bundle_version

	def strip_prefixes (self):
		return ['', 'usr/']
		
	def strip_unnecessary_files (self):
		"Remove unnecessary cruft."

		delete_me = ''
		for p in self.strip_prefixes ():
			delete_me += p + '%(i)s '

		for i in (
			'bin/autopoint',
			'bin/glib-mkenums',
			'bin/guile-*',
			'bin/*-config',
			'bin/*gettext*',
			'bin/[cd]jpeg',
			'bin/envsubst*',
			'bin/glib-genmarshal*',
			'bin/gobject-query*',
			'bin/gspawn-win32-helper*',
			'bin/gspawn-win32-helper-console*',
			'bin/msg*',
			'bin/pango-querymodules*',
			'bin/xmlwf',
			'cross',
			'doc',
			'include',
			'info',
			'lib/gettext',
			'lib/gettext/hostname*',
			'lib/gettext/urlget*',
			'lib/glib-2.0/include/glibconfig.h',
			'lib/glib-2.0',
			'lib/libc.*',
			'lib/libm.*',
			'lib/pkgconfig',
			'lib/*~',
			'lib/*.a',
			'lib/python%(python_version)s/distutils/command/wininst-6*',
			'lib/python%(python_version)s/distutils/command/wininst-7.1*',
			'man',
			'share/doc',
			'share/guile/%(guile_version)s/ice-9/debugger/',
			'share/gettext/intl',
			'share/ghostscript/%(ghostscript_version)s/Resource/',
			'share/ghostscript/%(ghostscript_version)s/doc/',
			'share/ghostscript/%(ghostscript_version)s/examples',
			'share/gs/%(ghostscript_version)s/Resource/',
			'share/gs/%(ghostscript_version)s/doc/',
			'share/gs/%(ghostscript_version)s/examples',
			'share/gtk-doc',
			'share/info',
			'share/man',
			'share/omf',

			# prune harder
			'lib/python%(python_version)s/bsddb',
			'lib/python%(python_version)s/compiler',
			'lib/python%(python_version)s/curses',
			'lib/python%(python_version)s/distutils',
			'lib/python%(python_version)s/email',
			'lib/python%(python_version)s/hotshot',
			'lib/python%(python_version)s/idlelib',
			'lib/python%(python_version)s/lib-old',
			'lib/python%(python_version)s/lib-tk',
			'lib/python%(python_version)s/logging',
			'lib/python%(python_version)s/test',
			'lib/python%(python_version)s/xml',
			'share/lilypond/*/make',
			'share/gettext',
			'usr/share/aclocal',
			'share/lilypond/*/python',
			'share/lilypond/*/tex',
			'share/lilypond/*/vim',
			'share/lilypond/*/python',
			'share/lilypond/*/fonts/source',
			'share/lilypond/*/fonts/svg',
			'share/lilypond/*/fonts/tfm',
			'share/lilypond/*/fonts/type1/feta[0-9]*pfa',
			'share/lilypond/*/fonts/type1/feta-braces-[a-z]*pfa',
			'share/lilypond/*/fonts/type1/parmesan*pfa',
			'share/locale',
			'share/omf',
			'share/gs/fonts/[a-bd-z]*',
			'share/gs/fonts/c[^0][^9][^5]*',
			'share/gs/Resource',			
			):

			self.system ('cd %(installer_root)s && rm -rf ' + delete_me, {'i': i })
		self.system ('rm -f %(installer_root)s/usr/share/lilypond/*/fonts/*/fonts.cache-1')
		self.system ('fc-cache %(installer_root)s/usr/share/lilypond/*/fonts/*/')

	def strip_binary_file (self, file):
		self.system ('%(strip_command)s %(file)s', locals (), ignore_error = True)

	def strip_binary_dir (self, dir):
		(root, dirs, files) = os.walk (dir % self.get_substitution_dict ()).next ()
		for f in files:
			if os.path.basename (f) not in self.no_binary_strip:
				self.strip_binary_file (root + '/' + f)
			
	def strip (self):
		self.strip_unnecessary_files ()
		self.strip_binary_dir ('%(installer_root)s/usr/lib')
		self.strip_binary_dir ('%(installer_root)s/usr/bin')
		
	def create (self):
		self.strip ()
		
class Darwin_bundle (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -S '
		self.darwin_bundle_dir = '%(targetdir)s/LilyPond.app'
		
	def create (self):
		Installer.create (self)
		rw = darwintools.Rewirer (self.settings)
		rw.rewire_root (self.settings.installer_root)


		bundle_zip = self.expand ('%(uploads)s/lilypond-%(bundle_version)s-%(bundle_build)s.zip')
		self.system ('''
rm -f %(bundle_zip)s 
rm -rf %(darwin_bundle_dir)s
tar -C %(targetdir)s -zxf %(downloaddir)s/osx-lilypad-0.0.tar.gz
cp -pR --link %(installer_root)s/usr/* %(darwin_bundle_dir)s/Contents/Resources/
cd %(darwin_bundle_dir)s/../ && zip -yr %(bundle_zip)s LilyPond.app
''', locals ())
		
	
	def xstrip (self):
		self.strip_unnecessary_files ()
		# no binary strip: makes debugging difficult.
		
		
class Nsis (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -g '
		self.no_binary_strip = ['gsdll32.dll', 'gsdll32.lib']
		
	def create (self):
		Installer.create (self)
		
		# FIXME: build in separate nsis dir, copy or use symlink
		installer = os.path.basename (self.settings.installer_root)
		self.file_sub ([
			('@GHOSTSCRIPT_VERSION@', '%(ghostscript_version)s'),
			('@GUILE_VERSION@', '%(guile_version)s'),
			('@LILYPOND_BUILD@', '%(bundle_build)s'),
			('@LILYPOND_VERSION@', '%(bundle_version)s'),
			('@PYTHON_VERSION@', '%(python_version)s'),
			('@ROOT@', '%(installer)s'),
			],
			       '%(nsisdir)s/lilypond.nsi.in',
#			       to_name='%(targetdir)s/lilypond.nsi',
			       to_name='%(targetdir)s/lilypond.nsi',
			       env=locals ())
		# FIXME: move nsis cruft to nsis dir
		self.system ('cp %(nsisdir)s/*.nsh %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.scm.in %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.sh.in %(targetdir)s')
		self.system ('cd %(targetdir)s && makensis lilypond.nsi')
#		self.system ('cd %(targetdir)s && makensis -NOCD %(nsisdir)/lilypond.nsi')
		self.system ('mv %(targetdir)s/setup.exe %(installer_uploads)s/lilypond-%(bundle_version)s-%(bundle_build)s.exe', locals ())

class Linux_installer (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		# lose the i486-foo-bar-baz-
		self.strip_command = 'strip -g'

	def strip_prefixes (self):
		return (Installer.strip_prefixes (self)
			+ [self.expand ('usr/%(framework_dir)s/usr/')])
			
	def strip (self):
		Installer.strip (self)
		self.strip_binary_dir ('%(installer_root)s/usr/%(framework_dir)s/usr/bin')
		self.strip_binary_dir ('%(installer_root)s/usr/%(framework_dir)s/usr/lib')

class Tgz (Linux_installer):
	def create (self):
		Linux_installer.create (self)
		self.system ('tar -C %(installer_root)s -zcf %(installer_uploads)s/%(name)s-%(bundle_version)s-%(package_arch)s-%(bundle_build)s.tgz .', locals ())

class Deb (Linux_installer):
	def create (self):
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(installer_uploads)s/%(name)s-%(bundle_version)s-%(package_arch)s-%(bundle_build)s.tgz', locals ())

class Rpm (Linux_installer):
	def create (self):
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(installer_uploads)s/%(name)s-%(bundle_version)s-%(package_arch)s-%(bundle_build)s.tgz', locals ())

class Autopackage (Linux_installer):
	def create (self):
		self.system ('rm -rf %(build_autopackage)s')
		self.system ('mkdir -p %(build_autopackage)s/autopackage')
		self.file_sub ([('@VERSION@', '%(bundle_version)s')],
			       '%(specdir)s/lilypond.apspec.in',
			       to_name='%(build_autopackage)s/autopackage/default.apspec')
		# FIXME: just use symlink?
		self.system ('tar -C %(installer_root)s/usr -cf- . | tar -C %(build_autopackage)s -xvf-')
		self.system ('cd %(build_autopackage)s && makeinstaller')
		self.system ('mv %(build_autopackage)s/*.package %(installer_uploads)s')


def get_installers (settings):
	installers = {
		'darwin' : [Darwin_bundle (settings)],
		'freebsd' : [
		Tgz (settings),
		],
		'linux' : [
		Tgz (settings),  # not alphabetically, used by others

		Autopackage (settings),
		Deb (settings),
		Rpm (settings),
		],
		'mingw' : [Nsis (settings)],
	}

	return installers[settings.platform]
