import os

import gub

# FIXME: Want to share package_dict () and system () with gub.Package,
# add yet another base class?
class Installer (gub.Package):
	def __init__ (self, settings):
		gub.Package.__init__ (self, settings)
		self.version = settings.bundle_version

        def name (self):
		return 'lilypond'

class Bundle (Installer):
	def create (self):
		pass

class Nsis (Installer):
	def create (self):
		# FIXME: build in separate nsis dir, copy or use symlink
		installer = os.path.basename (self.settings.gubinstall_root)
		build = self.settings.build
		self.file_sub ([
			('@GUILE_VERSION@', '%(guile_version)s'),
			('@LILYPOND_BUILD@', '%(build)s'),
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
		self.system ('mv %(targetdir)s/setup.exe %(installer_uploads)s/lilypond-%(version)s-%(build)s.exe', locals ())

class Tgz (Installer):
	def create (self):
		build = self.settings.build
		self.system ('tar -C %(gubinstall_root)s -zcf %(installer_uploads)s/%(name)s-%(version)s-%(package_arch)s-%(build)s.tgz .', locals ())

class Deb (Installer):
	def create (self):
		build = self.settings.build
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-deb %(installer_uploads)s/%(name)s-%(version)s-%(package_arch)s-%(build)s.tgz', locals ())

class Rpm (Installer):
	def create (self):
		build = self.settings.build
		self.system ('cd %(installer_uploads)s && fakeroot alien --keep-version --to-rpm %(installer_uploads)s/%(name)s-%(version)s-%(package_arch)s-%(build)s.tgz', locals ())


class Autopackage (Installer):
	def create (self):
		self.system ('rm -rf %(build_autopackage)s')
		self.system ('mkdir -p %(build_autopackage)s/autopackage')
		self.file_sub ([('@VERSION@', '%(version)s')],
			       '%(specdir)s/lilypond.apspec.in',
			       to_name='%(build_autopackage)s/autopackage/default.apspec')
		# FIXME: just use symlink?
		self.system ('tar -C %(gubinstall_root)s -cf- . | tar -C %(build_autopackage)s -xvf-')
		self.system ('cd %(build_autopackage)s && makeinstaller')
		self.system ('mv %(build_autopackage)s/*.package %(installer_uploads)s')
