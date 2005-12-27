import os
import re
import gub

from context import *

class Settings (Context):
	def __init__ (self, arch):
		Context.__init__(self)
		
		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = self.topdir + '/downloads'
		self.patchdir = self.topdir + '/patches'
		self.build_architecture = gub.read_pipe ('gcc -dumpmachine',
							 silent=True)[:-1]
		self.specdir = self.topdir + '/specs'
		self.nsisdir = self.topdir + '/nsis'
		self.gtk_version = '2.8'

		self.target_architecture = arch
		self.tool_prefix = arch + '-'
		self.targetdir = self.topdir + '/target/%s' % self.target_architecture

		## Patches are architecture dependent, 
		## so to ensure reproducibility, we unpack for each
		## architecture separately.
		self.allsrcdir = os.path.join (self.targetdir, 'src')
		
		self.builddir = self.targetdir + '/build'
		self.statusdir = self.targetdir + '/status'

		## Safe uploads, so that we can rm -rf target/*
		## and still cheaply construct a (partly) system root
		## from .gub packages.
		## self.gub_uploads = self.targetdir + '/uploads/gub'
		self.uploads = self.topdir + '/uploads'
		self.gub_uploads = self.uploads + '/gub'

		# FIXME: rename to target_root?
		self.system_root = self.targetdir + '/system'
		self.installdir = self.targetdir + '/install'
		self.tooldir = self.targetdir + '/tools'

		# INSTALLERS
		self.installer_root = self.targetdir + '/installer'
		##self.installer_uploads = self.targetdir + '/uploads'
		self.installer_uploads = self.uploads
		self.bundle_version = None
		self.bundle_build = None
		self.package_arch = re.sub ('-.*', '', self.build_architecture)
		self.keep_build = False
		self.python_version = '2.4'

		self.use_tools = False
		self.build_autopackage = self.builddir + '/autopackage'
		
	def verbose (self):
		return self.options.verbose
	
 	def create_dirs (self): 
		for a in (
			'downloaddir',
			'gub_uploads',
			'installer_uploads',
			'specdir',
			'allsrcdir',
			'statusdir',
			'system_root',
			'targetdir',
			'tooldir',
			'topdir',
			):
			dir = self.__dict__[a]
			if os.path.isdir (dir):
				continue

			gub.system ('mkdir -p %s' % dir)

