import gub
import misc
import glob

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
	def zip_libgcc (self):
		dylib_exts = ['dylib', 'so', 'dll']
		file_lists = [glob.glob (self.expand ("%(install_root)s/usr/%(target_architecture)s/lib/*"
						      + d))
			      for d in dylib_exts]
		
		files = ' '.join (misc.list_append (file_lists))
		
		self.system ('''mkdir -p %(builddir)s/usr/lib && cp -a %(files)s %(builddir)s/usr/lib/ ''', locals())
		self.system ('''tar -zcf %(gub_uploads)s/libgcc-%(version)s-1.%(platform)s.gub  -C %(builddir)s usr/''')
		self.system ('''rm -f %s ''' % files)


	def package (self):
		self.zip_libgcc ()
		Cross_package.package (self)
		
	def configure_command (self):
		cmd = Cross_package.configure_command (self)
		# FIXME: using --prefix=%(tooldir)s makes this
		# uninstallable as a normal system package in
		# /usr/i686-mingw/
		# Probably --prefix=/usr is fine too
		languages = ['c',
			     'c++'
			     ]
		language_opt = (' --enable-languages=%s ' % ','.join (languages))
		cxx_opt = '--enable-libstdcxx-debug '

		cmd += '''
--prefix=%(tooldir)s
--program-prefix=%(target_architecture)s-
--with-as=%(tooldir)s/bin/%(target_architecture)s-as
--with-ld=%(tooldir)s/bin/%(target_architecture)s-ld
--enable-static
--enable-shared '''

		cmd += language_opt
		if 'c++' in languages:
			cmd +=  ' ' + cxx_opt

		return misc.join_lines (cmd)

	def install (self):
		Cross_package.install (self)
		self.system ('''
cd %(tooldir)s/lib && ln -fs libgcc_s.1.so libgcc_s.so
''')



