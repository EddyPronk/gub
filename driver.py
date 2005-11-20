import sys
sys.path.insert (0, 'specs/')

import re
import os
import gub


class Settings:
	def __init__ (self):
		pass

	
settings = Settings()
settings.target_architecture = 'powerpc-apple-darwin' 
settings.topdir = os.getcwd()
settings.downloaddir = os.getcwd() + '/downloads/'

settings.srcdir = os.path.join (settings.topdir, 'src')
settings.specdir = settings.topdir + '/specs/'
settings.targetdir = settings.topdir + '/target/%s/' % settings.target_architecture
settings.systemdir = settings.targetdir + '/system/'
settings.builddir = settings.targetdir + '/build/'
settings.installdir = settings.targetdir + '/install/'
settings.statusdir = settings.targetdir + '/status/'
settings.tooldir = settings.targetdir + '/tools/'

os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin', os.environ["PATH"])


def create_dirs (settings): 
    for a in ['topdir', 'statusdir', 
	      'downloaddir', 'srcdir', 'specdir',
	      'targetdir', 'systemdir']:
	    try:
		    gub.system ('mkdir -p %s' % settings.__dict__[a], ignore_error = True)
	    except OSError:
		    pass



def process_package (package):
	package.download ()

	for stage in ['unpack', 'patch', 'configure', 'compile', 'install']:
#		if not package.done (stage):
#			(package.__class__.__dict__[stage]) (package)
#			package.set_done (stage)

		if not package.done (stage):
			if stage == 'unpack': package.unpack()
			elif stage == 'configure':  package.configure ()
			elif stage == 'patch':  package.patch ()
			elif stage == 'compile': package.compile ()
			elif stage == 'install': package.install ()
			
			package.set_done (stage)

def process_packages (ps):
	for p in ps:
		process_package (p)
	
	
if not os.path.exists (settings.targetdir):
	create_dirs (settings)

import darwintools
import framework

process_packages (darwintools.get_packages (settings))
process_packages (framework.get_packages (settings))
		




