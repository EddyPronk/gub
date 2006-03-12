import os
#
import cross
import download
import gub
import misc
import mingw
import gup2

# FIXME: setting binutil's tooldir and/or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils (cross.Binutils):
	def makeflags (self):
		return misc.join_lines ('''
tooldir="%(crossprefix)s/%(target_architecture)s"
''')
	def compile_command (self):
		return (cross.Binutils.compile_command (self)
			+ self.makeflags ())

class Gcc (mingw.Gcc):
	def makeflags (self):
		return misc.join_lines ('''
tooldir="%(crossprefix)s/%(target_architecture)s"
gcc_tooldir="%(crossprefix)s/%(target_architecture)s"
''')
	def compile_command (self):
		return (mingw.Gcc.compile_command (self)
			+ self.makeflags ())

	def configure_command (self):
		return (mingw.Gcc.configure_command (self)
			+ misc.join_lines ('''
--with-newlib
--enable-threads
'''))

mirror = 'http://gnu.kookel.org/ftp/cygwin'
def get_packages (settings, names):
	p = gup2.Dependency_manager (settings.system_root, settings.os_interface)
        url = mirror + '/setup.ini'
	# FIXME: download/offline
	downloaddir = settings.downloaddir
	file = settings.downloaddir + '/setup.ini'
	if not os.path.exists (file):
		os.system ('wget -P %(downloaddir)s %(url)s' % locals ())
	# FIXME: must add deps to buildeps, otherwise packages do not
	# get built in correct dependency order?
	cross_packs = [
		Binutils (settings).with (version='20050610-1', format='bz2', mirror=download.cygwin,
					   depends=['cygwin', 'w32api'],
					   builddeps=['cygwin', 'w32api']
						),
		Gcc (settings).with (version='4.1.0', mirror=download.gcc_41, format='bz2',
					   depends=['binutils', 'cygwin', 'w32api'],
					   builddeps=['binutils', 'cygwin', 'w32api']
					   ),
		]

	return cross_packs + filter (lambda x: x.name () not in names,
				     get_cygwin_packages (settings, file))

def change_target_packages (packages):
	cross.change_target_packages (packages)

	# FIXME: this does not work
	for p in packages:
		gub.change_target_dict (p,
					{
			'DLLTOOL': '%(tool_prefix)sdlltool',
			'DLLWRAP': '%(tool_prefix)sdllwrap',
			'LDFLAGS': '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api',
			})


import gup2
from new import classobj
import gub
import re

mirror = 'http://gnu.kookel.org/ftp/cygwin'

def get_cygwin_package (settings, name, dict):
	Package = classobj (name, (gub.Binary_package,), {})
	package = Package (settings)
	if dict.has_key ('requires'):
		deps = [x.strip () for x in 
			    re.sub ('\([^\)]*\)', '',
				    dict['requires']).split ()]
		cross = [
			'base-passwd', 'bintutils', 
			'gcc', 'gcc-core', 'gcc-g++',
			'gcc-mingw', 'gcc-mingw-core', 'gcc-mingw-g++',
			]
		cycle = ['base-passwd']
		source = [
			'guile-devel',
			'libtool1.5', 'libltdl3',
			'libguile12', 'libguile16',
			 ]
		unneeded = [
			'_update-info-dir',
			'libXft', 'libXft1', 'libXft2',
			'libbz2_1',
			'X-startup-scripts',
			'xorg-x11-bin-lndir',
			]
		blacklist = cross + cycle + source + unneeded
		deps = filter (lambda x: x not in blacklist, deps)
		package.name_dependencies = deps
		package.name_build_dependencies = deps
	package.ball_version = dict['version']
	package.url = (mirror + '/'
		       + dict['install'].split ()[0])
	package.format = 'bz2'
	return package

def get_cygwin_packages (settings, package_file):
	dist = 'curr'
	
	dists = {'test': [], 'curr': [], 'prev' : []}
	chunks = open (package_file).read ().split ('\n\n@ ')
	for i in chunks[1:]:
		lines = i.split ('\n')
		name = lines[0].strip ()
		blacklist = ('binutils', 'gcc', 'guile', 'guile-devel', 'libguile12', 'libguile16', 'libtool', 'litool1.5' , 'libtool-devel', 'libltdl3')
		if name in blacklist:
			continue
		packages = dists['curr']
		records = {
			'sdesc': name,
			'version': '0-0',
			'install': 'urg 0 0',
			}
		j = 1
		while j < len (lines) and lines[j].strip ():
			if lines[j][0] == '#':
				j = j + 1
				continue
			elif lines[j][0] == '[':
				packages.append (get_cygwin_package (settings, name, records.copy ()))
				packages = dists[lines[j][1:5]]
				j = j + 1
				continue

			try:
				key, value = [x.strip () for x in lines[j].split (': ', 1)]
			except KeyError: ### UGH -> what kind of exceptino? 
				print lines[j], package_file
				raise 'URG'
			if (value.startswith ('"')
			    and value.find ('"', 1) == -1):
				while 1:
					j = j + 1
					value += '\n' + lines[j]
					if lines[j].find ('"') != -1:
						break
			records[key] = value
			j = j + 1
		packages.append (get_cygwin_package (settings, name, records))

	return dists[dist]


