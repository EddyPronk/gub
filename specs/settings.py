import os
import re

import gub

from context import *

class Settings (Context):
	def __init__ (self, platform):
		Context.__init__ (self)
		self.platform = platform
		self.target_architecture = {
			'darwin': 'powerpc-apple-darwin7',
			'mingw': 'i686-mingw32',
			'freebsd': 'i686-freebsd4',
			'linux': 'i686-linux',
			'local': 'local',
			}[self.platform]

		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = self.topdir + '/downloads'
		self.patchdir = self.topdir + '/patches'
		self.os_interface = Os_commands ('build-%s.log'
						 % self.target_architecture)
		self.build_architecture = self.os_interface.read_pipe ('gcc -dumpmachine',
							 silent=True)[:-1]
		self.specdir = self.topdir + '/specs'
		self.nsisdir = self.topdir + '/nsis'
		self.gtk_version = '2.8'

		self.tool_prefix = self.target_architecture + '-'
		self.targetdir = (self.topdir + '/target/%s'
				  % self.target_architecture)

		## Patches are architecture dependent, 
		## so to ensure reproducibility, we unpack for each
		## architecture separately.
		self.allsrcdir = os.path.join (self.targetdir, 'src')
		
		self.allbuilddir = self.targetdir + '/build'
		self.statusdir = self.targetdir + '/status'

		## Safe uploads, so that we can rm -rf target/*
		## and still cheaply construct a (partly) system root
		## from .gub packages.
		self.uploads = self.topdir + '/uploads'
		#self.gub_uploads = self.uploads + '/gub'
		self.gub_uploads = self.uploads + '/' + self.platform

		# FIXME: rename to target_root?
		self.system_root = self.targetdir + '/system'
		self.crossprefix = self.system_root + '/usr/cross'
		self.installdir = self.targetdir + '/install'
		self.tooldir = self.topdir + '/target/local/system/usr/'

		# INSTALLERS
		self.installer_root = self.targetdir + '/installer'
		##self.installer_uploads = self.targetdir + '/uploads'
		self.installer_uploads = self.uploads
		self.bundle_version = None
		self.bundle_build = None
		self.package_arch = re.sub ('-.*', '', self.build_architecture)
		self.keep_build = False
		self.use_tools = False
		self.build_autopackage = self.allbuilddir + '/autopackage'
		
	def verbose (self):
		try:
			return self.options.verbose
		except AttributeError:
			return False
	
 	def create_dirs (self): 
		for a in (
			'downloaddir',
			'gub_uploads',
			'installer_uploads',
			'specdir',
			'allsrcdir',
			'statusdir',
			'system_root',
			'crossprefix',
			'targetdir',
			'tooldir',
			'topdir',
			):
			dir = self.__dict__[a]
			if os.path.isdir (dir):
				continue

			self.os_interface.system ('mkdir -p %s' % dir)

