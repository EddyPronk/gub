import os
import re
import time


import darwintools
import context
import gup2

from context import subst_method
from misc import *

class Installer (context.Os_context_wrapper):
	def __init__ (self, settings):
		context.Os_context_wrapper.__init__ (self, settings)

		self.settings = settings
		self.strip_command = '%(crossprefix)s/bin/%(target_architecture)s-strip' 
		self.no_binary_strip = []
		self.no_binary_strip_extensions = ['.la', '.py', '.def',
						   '.scm', '.pyc']

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
			'lib/python*/distutils/command/wininst-6*',
			'lib/python*/distutils/command/wininst-7.1*',
			'man',
			'share/doc',
			'share/guile/*/ice-9/debugger/',
			'share/gettext/intl',
			'share/ghostscript/*/{Resource,doc,examples}/',
			'share/gs/*/{Resource,doc,examples}/',
			'share/gtk-doc',
			'share/info',
			'share/man',
			'share/omf',

			# prune harder
			'lib/python*/bsddb',
			'lib/python*/compiler',
			'lib/python*/curses',
			'lib/python*/distutils',
			'lib/python*/email',
			'lib/python*/hotshot',
			'lib/python*/idlelib',
			'lib/python*/lib-old',
			'lib/python*/lib-tk',
			'lib/python*/logging',
			'lib/python*/test',
# xml2ly needs xml.dom
#			'lib/python%(python_version)s/xml',
			'share/lilypond/*/make',
			'share/gettext',
			'usr/share/aclocal',
			'share/lilypond/*/tex',
			'share/lilypond/*/fonts/source',
# Keep svg fonts.  They are needed for usable/sharable svg output.
#			'share/lilypond/*/fonts/svg',
			'share/lilypond/*/fonts/tfm',
			'share/lilypond/*/fonts/type1/feta[0-9]*pfa',
			'share/lilypond/*/fonts/type1/feta-braces-[a-z]*pfa',
			'share/lilypond/*/fonts/type1/parmesan*pfa',
			'share/locale',
			'share/omf',
			## 2.6 installer: leave c059*
			'share/gs/fonts/[a-bd-z]*',
			'share/gs/fonts/c[^0][^5][^9]*',
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
			if (os.path.basename (f) not in self.no_binary_strip
			    and os.path.splitext (f)[1] not in self.no_binary_strip_extensions):
				self.strip_binary_file (root + '/' + f)
			
	def strip (self):
		self.strip_unnecessary_files ()
		self.strip_binary_dir ('%(installer_root)s/usr/lib')
		self.strip_binary_dir ('%(installer_root)s/usr/bin')
		
	def create (self):
		pass
		
class Darwin_bundle (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -S '
		self.darwin_bundle_dir = '%(targetdir)s/LilyPond.app'
		
	def create (self):
		Installer.create (self)
		rw = darwintools.Rewirer (self.settings)
		pm = gup2.Dependency_manager (self.settings.system_root,
					      self.settings.os_interface)
		rw.set_ignore_libs (pm)
		osx_lilypad_version = pm.package_dict ('osx-lilypad')['version']
		
		rw.rewire_root (self.settings.installer_root)

		bundle_zip = self.expand ('%(uploads)s/lilypond-%(bundle_version)s-%(bundle_build)s.%(platform)s.zip')
		self.system ('''
rm -f %(bundle_zip)s 
rm -rf %(darwin_bundle_dir)s
tar -C %(targetdir)s -zxf %(downloaddir)s/osx-lilypad-%(osx_lilypad_version)s.tar.gz
cp %(darwin_bundle_dir)s/Contents/Resources/subprocess.py %(installer_root)s/usr/share/lilypond/current/python/
cp -pR --link %(installer_root)s/usr/* %(darwin_bundle_dir)s/Contents/Resources/

''', locals ())
		self.file_sub (
			[('2.7.26-1',
			  '%(bundle_version)s-%(bundle_build)s'),
			 ('Build from .*',
			  'Build from %s' % time.asctime()),
			 ],
			'%(darwin_bundle_dir)s/Contents/Info.plist',
			env=locals (),
			must_succeed=True)
		self.system ('cd %(darwin_bundle_dir)s/../ && zip -yr %(bundle_zip)s LilyPond.app',
			     locals ())
		
		self.log_command ("Created %(bundle_zip)s\n", locals()) 
		
class Nsis (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.strip_command += ' -g '
		self.no_binary_strip = ['gsdll32.dll', 'gsdll32.lib']

	def create (self):
		Installer.create (self)
		
		# FIXME: build in separate nsis dir, copy or use symlink
		installer = os.path.basename (self.settings.installer_root)

		package_manager = gup2.Dependency_manager (self.settings.system_root,
							   self.settings.os_interface)
		
		self.file_sub ([
			('@GHOSTSCRIPT_VERSION@', package_manager.package_dict ('ghostscript')['version']),
			
			('@GUILE_VERSION@', package_manager.package_dict ('ghostscript')['version']),
			('@LILYPOND_BUILD@', '%(bundle_build)s'),
			('@LILYPOND_VERSION@', '%(bundle_version)s'),
			('@PYTHON_VERSION@', package_manager.package_dict ('python')['version']),
			('@ROOT@', '%(installer)s'),
			],
			       '%(nsisdir)s/lilypond.nsi.in',
#			       to_name='%(targetdir)s/lilypond.nsi',
			       to_name='%(targetdir)s/lilypond.nsi',
			       env=locals ())
		
		self.system ('cp %(nsisdir)s/*.nsh %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.bat.in %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.scm.in %(targetdir)s')
		self.system ('cp %(nsisdir)s/*.sh.in %(targetdir)s')
		self.system ('cd %(targetdir)s && makensis lilypond.nsi')

		final = 'lilypond-%(bundle_version)s-%(bundle_build)s.%(platform)s.exe'
		self.system ('mv %(targetdir)s/setup.exe %(installer_uploads)s/%(final)s', locals ())





class Linux_installer (Installer):
	def __init__ (self, settings):
		Installer.__init__ (self, settings)
		self.bundle_tarball = '%(targetdir)s/%(name)s-%(bundle_version)s-%(bundle_build)s.%(platform)s.tar.bz2'

	def strip_prefixes (self):
		return Installer.strip_prefixes (self)

	def create_tarball (self):
		self.system ('tar -C %(installer_root)s -jcf %(bundle_tarball)s .', locals ())

def create_shar (orig_file, hello, head, target_shar):
	length = os.stat (orig_file)[6]

	tarflag = tar_compression_flag (orig_file)

	base_orig_file = os.path.split (orig_file)[1]
	script = open (head).read ()

	header_length = 0
	header_length = len (script % locals ()) + 1

	f = open (target_shar, 'w')
	f.write (script % locals())
	f.close ()

		
	cmd = 'cat %(orig_file)s >> %(target_shar)s' % locals ()
	print 'invoking ', cmd
	stat = os.system (cmd)
	if stat:
		raise 'create_shar() failed'
	os.chmod (target_shar, 0755)

class Shar (Linux_installer):
	def create (self):
		self.create_tarball ()
		
		target_shar = self.expand ('%(installer_uploads)s/%(name)s-%(bundle_version)s-%(bundle_build)s.%(platform)s.sh')

		head = self.expand ('%(patchdir)s/sharhead.sh')
		tarball = self.expand (self.bundle_tarball)

		hello = self.expand ("version %(bundle_version)s release %(bundle_build)s")
		create_shar (tarball, hello, head, target_shar)
			     
class Deb (Linux_installer):
	def create (self):
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(bundle_tarball)s', locals ())

class Rpm (Linux_installer):
	def create (self):
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(bundle_tarball)s', locals ())

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

class Cygwin_package (Installer):
	def __init__ (self, settings, target_manager, name):
		Installer.__init__ (self, settings, target_manager)
		self._name = name
		self.target_manager = target_manager
	def create (self):
		# FIND gub package object for NAME
		print 'packs: ' + `self.target_manager._packages`
		p = self.target_manager._packages[self._name]
		# CREATE balls *-build.tar.bz2, NAME-build-scr.tar.bz2
		# CREATE setup.hint files
		self.cygwin_ball (p, '')
		for i in p.split_packages:
			self.cygwin_ball (p, i)

	def cygwin_ball (self, package, split):
		cygwin_uploads = '%(gub_uploads)s/release'
		package_name = self._name
		if not split:
			gub_name = package.gub_name ()
		else:
			cygwin_uploads += '/' + self.name ()
			import inspect
			available = dict (inspect.getmembers (package, callable))
			gub_name = available['gub_name_' + split] ()

		base_name = re.sub ('-%\(version\)s.*', '', gub_name)
		ball_name = re.sub ('\.%\(platform\)s.*',
				    '-%(bundle_build)s.tar.bz2',
				    gub_name)
		hint = base_name + '.hint'
		dir = '%(installer_root)s-' + base_name
		package.system ('''
rm -rf %(dir)s
mkdir -p %(dir)s
tar -C %(dir)s -zxf %(gub_uploads)s/%(gub_name)s
rm -rf %(dir)s/usr/cross
mkdir -p %(cygwin_uploads)s/%(base_name)s
tar -C %(dir)s --owner=0 --group=0 -jcf %(cygwin_uploads)s/%(base_name)s/%(ball_name)s .
cp -pv %(installer_root)s-%(package_name)s/etc/hints/%(hint)s %(cygwin_uploads)s/%(base_name)s/setup.hint
''',
				locals ())

	def name (self):
		return self._name

def get_installers (settings, args=[]):

	## UGH : creating 6 instances of installer ?!
	installers = {
		'arm' : [Shar (settings)],
		'darwin-ppc' : [Darwin_bundle (settings)],
		'darwin-x86' : [Darwin_bundle (settings)],
		'freebsd' : [Shar (settings)],
		'linux' : [Shar (settings)],
		'mingw' : [Nsis (settings)],
	}

	if settings.platform == 'cygwin':
		return map (lambda x:

			    ## need install manager?
			    Cygwin_package (settings, x), args)
	return installers[settings.platform]
