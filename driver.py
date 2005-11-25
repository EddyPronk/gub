import __main__
import os
import re
import sys
import getopt

sys.path.insert (0, 'specs/')

import gub
import framework


class Settings:
	def __init__ (self, arch):
		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = os.getcwd () + '/downloads'
		self.build_spec = 'i686-linux'
		self.srcdir = os.path.join (self.topdir, 'src')
		self.specdir = self.topdir + '/specs'
		self.gtk_version = '2.8'

		self.target_architecture = arch
		self.targetdir = self.topdir + '/target/%s' % self.target_architecture
		
		self.builddir = self.targetdir + '/build'
		self.garbagedir = self.targetdir + '/garbage'
		self.installdir = self.targetdir + '/install'
		self.statusdir = self.targetdir + '/status'
		self.systemdir = self.targetdir + '/system'
		self.tooldir = self.targetdir + '/tools'

	def create_dirs (self): 
		for a in ['topdir', 'statusdir', 'garbagedir',
                          'downloaddir', 'srcdir', 'specdir',
                          'targetdir', 'systemdir']:
			try:
				gub.system ('mkdir -p %s' % self.__dict__[a],
                                            ignore_error = True)
			except OSError:
				pass

def process_package (package):
	package.download ()

	for stage in ['unpack', 'patch', 'configure', 'compile', 'install']:
        	if not package.is_done (stage):
                	if stage == 'unpack':
                        	package.unpack()
			elif stage == 'configure':
                        	package.configure ()
			elif stage == 'patch':
                        	package.patch ()
			elif stage == 'compile':
                        	package.compile ()
			elif stage == 'install':
                        	package.install ()
			package.set_done (stage)

def process_packages (packages):
	for i in packages:
		process_package (i)
		
def main ():
	(options, files) = getopt.getopt (sys.argv[1:], 'V', ['verbose'])
	verbose = 0 
	for (o,a) in options:
		if o == '--verbose' or o == '-V':
			verbose = 1

	try:
		platform = files[0]
	except IndexError:
		platform = ''
		
	if platform not in ['mac', 'mingw', 'mingw-fedora']:
		print 'unknown platform', platform
		print 'Use mac, mingw, mingw-fedora'
		sys.exit (1)

	if platform == 'mac':
		settings = Settings ('powerpc-apple-darwin7')
	elif platform == 'mingw':
		settings = Settings ('i586-mingw32msvc')
	elif platform == 'mingw-fedora':
		settings = Settings ('i386-mingw32')
		platform = 'mingw'

	settings.verbose = verbose
	
	if not os.path.exists (settings.targetdir):
		settings.create_dirs ()

	os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin',
                                           os.environ["PATH"])

	if platform == 'mac':
		import darwintools
		process_packages (darwintools.get_packages (settings))

	process_packages (framework.get_packages (settings, platform))



if __name__ == '__main__':
    	main ()
