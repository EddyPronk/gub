import os
#
import cross
import download
import gub
import misc
import mingw
import xpm

class Gcc (mingw.Gcc):
	def configure_command (self):
		return (mingw.Gcc.configure_command (self)
			+ misc.join_lines ('''
--with-newlib
--enable-threads
'''))
	

# FIXME: setting binutil's tooldir or gcc's gcc_tooldir may fix
# -luser32 (ie -L .../w32api/) problem without having to set LDFLAGS.
class Binutils (cross.Binutils):
	def makeflags (self):
		return misc.join_lines ('''
tooldir="%(cross_prefix)s"
''')
	def compile_command (self):
		return (cross.Binutils.compile_command (self)
			+ self.makeflags ())

def get_packages (settings, names):
	p = xpm.Cygwin_package_manager (settings)
        url = p.mirror + '/setup.ini'
	# FIXME: download/offline
	downloaddir = settings.downloaddir
	file = settings.downloaddir + '/setup.ini'
	if not os.path.exists (file):
		os.system ('wget -P %(downloaddir)s %(url)s' % locals ())
	# FIXME: must add deps to buildeps, otherwise packages do not
	# get built in correct dependency order (topological sort?)
#binutils-20050610-1-src.tar.bz2
	cross_packs = [
#		cross.Binutils (settings).with (version='2.16.1', format='bz2',
# fixes auto-import		
#		cross.Binutils (settings).with (version='20050610-1', format='bz2', mirror=download.cygwin,
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
				     p.get_packages (file))

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
