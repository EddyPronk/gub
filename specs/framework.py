# latest vanilla packages
#Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
#Expat (settings).with (version='1.95.8', mirror=download.sf),
#Gettext (settings).with (version='0.14.5'),
#Guile (settings).with (version='1.7.2', mirror=download.alpha, format='gz'),

# FIXME: these lists should be merged, somehow,
# linux and mingw use almost the same list (linux does not have libiconv),
# but some classes have __mingw or __linux overrides.


import python
import ghostscript
import guile

import gub
import cross

def package_fixups (settings, packs, extra_build_deps):
	for p in packs:
		if p.name () == 'lilypond':
			p._downloader = p.cvs
		if (not isinstance (p, gub.Sdk_package)
		    and not isinstance (p, cross.Cross_package)):
			p.name_build_dependencies += filter (lambda x: x != p.name (),
							     extra_build_deps)

def version_fixups (settings, packs):
	try:
		settings.python_version = [p for p in packs
					   if isinstance (p, python.Python)][0].python_version ()
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
			if isinstance (p, guile.Guile)][0].guile_version ()
	except IndexError:
		if settings.platform == 'debian':
			settings.guile_version = '1.8'
	try:
		settings.ghostscript_version = [p for p in packs
						if isinstance (p, ghostscript.Ghostscript)][0].ghostscript_version ()
	except IndexError:
		if settings.platform == 'cygwin':
			settings.ghostscript_version = '8.15'
		elif settings.platform == 'debian':
			settings.ghostscript_version = '8.15'

	# FIXME
	settings._substitution_dict['ghostscript_version'] = settings.ghostscript_version
	settings._substitution_dict['guile_version'] = settings.guile_version
	settings._substitution_dict['python_version'] = settings.python_version
	
