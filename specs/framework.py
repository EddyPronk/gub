# latest vanilla packages
#Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
#Expat (settings).with (version='1.95.8', mirror=download.sf),
#Gettext (settings).with (version='0.14.5'),
#Guile (settings).with (version='1.7.2', mirror=download.alpha, format='gz'),

# FIXME: these lists should be merged, somehow,
# linux and mingw use almost the same list (linux does not have libiconv),
# but some classes have __mingw or __linux overrides.


from python import *
from ghostscript import *
from guile import *

def package_fixups (settings, packs):
	deps = {
		'arm': ['libc6','libc6-dev', 'linux-kernel-headers'],
		'cygwin' : [],
		'debian' : [],
		'darwin' : ['darwin-sdk'],
		'linux' : [],
		'mingw': ['mingw-runtime'],
		'freebsd': ['freebsd-runtime'],
		}

	ex =  ['binutils', 'gcc']
	for i in deps.keys ():
		ex += deps[i]

	for i in packs:
		if not i.name () in ex:
			i.name_dependencies += deps[settings.platform]

	for p in packs:
		if p.name () == 'lilypond':
			p._downloader = p.cvs

def version_fixups (settings, packs):
	try:
		settings.python_version = [p for p in packs
#					   if isinstance (p, Python)][0].python_version ()
					   if p.name () == 'python'][0].python_version ()
	except IndexError:
		if 0:
			pass
		elif settings.platform == 'arm':
			settings.python_version = '2.4'
		elif settings.platform == 'cygwin':
			settings.python_version = '2.4'
		elif settings.platform == 'darwin':
			settings.python_version = '2.3'
		elif settings.platform == 'debian':
			settings.python_version = '2.3'
	try:
		settings.guile_version = [p for p in packs
#			if isinstance (p, Guile)][0].guile_version ()
			if p.name () == 'guile'][0].guile_version ()
	except IndexError:
		if settings.platform == 'debian':
			settings.guile_version = '1.8'
	try:
		settings.ghostscript_version = [p for p in packs
#						if isinstance (p, Ghostscript)][0].ghostscript_version ()
						if p.name () == 'ghostscript'][0].ghostscript_version ()
	except IndexError:
		if settings.platform == 'cygwin':
			settings.ghostscript_version = '8.15'
		elif settings.platform == 'debian':
			settings.ghostscript_version = '8.15'

	# FIXME
	settings._substitution_dict['ghostscript_version'] = settings.ghostscript_version
	settings._substitution_dict['guile_version'] = settings.guile_version
	settings._substitution_dict['python_version'] = settings.python_version
	
