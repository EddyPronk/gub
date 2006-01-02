import gub
import misc

class Cross_package (gub.Package):
	"""Package for cross compilers/linkers etc.
	"""

	def configure_command (self):
		return (gub.Package.configure_command (self)
			+ misc.join_lines ('''
--target=%(target_architecture)s
--with-sysroot=%(system_root)s/
'''))

        def xgub_name (self):
		## makes build number handling more complicated.
		return '%(name)s-%(version)s-%(build)s.%(build_architecture)s-%(target_architecture)s.gub'

	def install_command (self):
		# FIXME: to install this, must revert any prefix=tooldir stuff
		return 'make prefix=/usr DESTDIR=%(install_root)s install'

	def package (self):
		# naive tarball packages for now
		# cross packages must not have ./usr because of tooldir
		self.system ('''
tar -C %(install_root)s/usr -zcf %(gub_uploads)s/%(gub_name)s .
''')

class Pkg_config (Cross_package):
	pass

class Binutils (Cross_package):
	pass

class Gcc (Cross_package):
	def patch (self):
		self.file_sub ([('/usr/bin/libtool', '%(tooldir)s/bin/%(target_architecture)s-libtool')],
			       '%(srcdir)s/gcc/config/darwin.h')

	def configure_command (self):
		cmd = Cross_package.configure_command (self)
		# FIXME: using --prefix=%(tooldir)s makes this
		# uninstallable as a normal system package in
		# /usr/i686-mingw/
		# Probably --prefix=/usr is fine too
		cmd += '''
--prefix=%(tooldir)s
--program-prefix=%(target_architecture)s-
--with-as=%(tooldir)s/bin/%(target_architecture)s-as
--with-ld=%(tooldir)s/bin/%(target_architecture)s-ld
--enable-static
--enable-shared
--enable-libstdcxx-debug
--enable-languages=c,c++ ''' % self.settings.__dict__

		return misc.join_lines (cmd)

	def install (self):
		Cross_package.install (self)
		self.system ('''
cd %(tooldir)s/lib && ln -fs libgcc_s.1.so libgcc_s.so
''')



