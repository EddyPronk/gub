import gub
import misc
import glob
import os
import imp
import md5

from context import subst_method 
class Cross_package (gub.Package):
	"""Package for cross compilers/linkers etc.
	"""

	def configure_command (self):
		return (gub.Package.configure_command (self)
			+ misc.join_lines ('''
--program-prefix=%(target_architecture)s-
--prefix=%(crossprefix)s/
--with-slibdir=/usr/lib/
--target=%(target_architecture)s
--with-sysroot=%(system_root)s/
'''))

	def install_command (self):
		return '''make DESTDIR=%(install_root)s prefix=/usr/cross/ install'''
	
	def gub_ball (self):
		c =  '%(gub_cross_uploads)s/%(gub_name)s'
		return c

        def hdr_file (self):
		return '%(gub_cross_uploads)s/%(hdr_name)s.hdr'

class Binutils (Cross_package):
	def install (self):
		Cross_package.install (self)
		self.system ('rm %(install_root)s/usr/cross/lib/libiberty.a')

class Gcc (Cross_package):
	def configure_command (self):
		cmd = Cross_package.configure_command (self)
		# FIXME: using --prefix=%(tooldir)s makes this
		# uninstallable as a normal system package in
		# /usr/i686-mingw/
		# Probably --prefix=/usr is fine too
		
		
		languages = ['c', 'c++']

		if self.settings.__dict__.has_key ("no-c++"):
			del languages[1]

		language_opt = (' --enable-languages=%s ' % ','.join (languages))
		cxx_opt = '--enable-libstdcxx-debug '

		cmd += '''
--with-as=%(crossprefix)s/bin/%(target_architecture)s-as
--with-ld=%(crossprefix)s/bin/%(target_architecture)s-ld
--enable-static
--enable-shared '''

		cmd += language_opt
		if 'c++' in languages:
			cmd +=  ' ' + cxx_opt

		return misc.join_lines (cmd)
	def configure(self):
		Cross_package.configure (self)


	def move_target_libs (self, libdir):
		if not os.path.isdir (libdir):
			return

		library_suffixes =['.la', '.so', '.dylib']
		find_pred = ' -or '.join([(" -name 'lib*%s*' " % s) for s in library_suffixes])
		
		for f in self.read_pipe ("cd %(libdir)s/ && find %(find_pred)s", locals ()).split():
			(dir, file) = os.path.split (f)
			target = self.expand ('%(install_prefix)s/%(dir)s', locals())
			if not os.path.isdir (target):
				os.makedirs (target)
			self.system ('mv %(libdir)s/%(dir)s/%(file)s %(install_prefix)s/lib', locals())

	def install (self):
		Cross_package.install (self)
		old_libs = self.expand ('%(install_root)s/usr/cross/%(target_architecture)s')

		self.move_target_libs (old_libs)
		self.move_target_libs (self.expand ('%(install_root)s/usr/cross/lib'))
		## FIXME: .so senseless for darwin.
		self.system ('''
cd %(install_root)s/usr/lib && ln -fs libgcc_s.so.1 libgcc_s.so
''')



def change_target_packages (package_object_dict):
	pass


def set_cross_dependencies (package_object_dict):
	packs = package_object_dict.values ()
	cross_packs = [p for p in packs if isinstance (p, Cross_package)]
	sdk_packs = [p for p in packs if isinstance (p, gub.Sdk_package)]
	other_packs = [p for p in packs if (not isinstance (p, Cross_package)
					    and not isinstance (p, gub.Sdk_package)
					    and not isinstance (p, gub.Binary_package))]
	
	for p in other_packs:
		p.name_build_dependencies += map (lambda x: x.name (),
						  cross_packs)

	for p in other_packs + cross_packs:
		p.name_build_dependencies += map (lambda x: x.name (),
						  sdk_packs)

	return packs

def set_framework_ldpath (packs):
	for c in packs:
		change = gub.Change_target_dict (c, {'LDFLAGS': r" -Wl,--rpath,'$${ORIGIN}/../lib/' "})
		c.get_substitution_dict = change.append_dict



cross_module_checksums = {}
def get_cross_module (platform):
	base = platform
	try:
		base = 	{'debian':'debian_unstable',
			 'darwin-ppc':'darwintools',
			 'darwin-x86':'darwintools',
			 'local':'tools'}[platform]
	except KeyError:
		pass
	
	desc = ('.py', 'U', 1)
	file_name = 'lib/%s.py' % base
	file = open (file_name)
	module = imp.load_module (base, file, file_name, desc)

	cross_module_checksums[platform] = md5.md5 (open (file_name).read ()).hexdigest ()
	
	return module

def get_cross_packages (settings):
	mod = get_cross_module (settings.platform)
	return mod.get_packages (settings, [])

def get_cross_checksum (platform):
	try:
		return cross_module_checksums[platform]
	except KeyError:
		print 'No cross module found'
		return '0000'

