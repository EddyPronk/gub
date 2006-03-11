import os
#
import cross
import download
import gub
import misc
import mingw
import gup2
import cygwinpm

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
				     cygwinpm.get_packages (file))

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
