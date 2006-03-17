import glob
import re

import download
import targetpackage

class Python (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='2.4.2',
			   mirror=download.python,
			   format='bz2',
			   depends=['expat', 'zlib'])

	def patch (self):
		targetpackage.Target_package.patch (self)
		self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-1.patch')
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-configure.in-posix.patch')
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-configure.in-sysname.patch')
		self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-configure.in-sysrelease.patch')

		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-2.4.2-setup.py-no-native.patch')
		
	def python_version (self):
		return '.'.join (self.ball_version.split ('.')[0:2])

	def get_substitution_dict (self, env={}):
		dict = targetpackage.Target_package.get_substitution_dict (self, env)
		dict['python_version'] = self.python_version ()
		return dict

	def configure (self):
		self.system ('''cd %(srcdir)s && autoconf''')
		self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
		targetpackage.Target_package.configure (self)

	def compile_command (self):
		##
		## UGH.: darwin Python vs python (case insensitive FS)
		c = targetpackage.Target_package.compile_command (self)
		c += ' BUILDPYTHON=python-bin '
		return c

	def install_command (self):
		##
		## UGH.: darwin Python vs python (case insensitive FS)
		c = targetpackage.Target_package.install_command (self)
		c += ' BUILDPYTHON=python-bin '
		return c
	
class Python__mingw (Python):
	def __init__ (self, settings):
		Python.__init__ (self, settings)
		self.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_root)s/usr/include' % self.settings.__dict__

	# FIXME: first is cross compile + mingw patch, backported to
	# 2.4.2 and combined in one patch; move to cross-Python?
	def patch (self):
		Python.patch (self)
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-winsock2.patch
''')
		self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-2.4.2-setup.py-selectmodule.patch')

		## to make subprocess.py work.
		self.file_sub ([
				("import fcntl", ""),

				], "%(srcdir)s/Lib/subprocess.py")
		
	def config_cache_overrides (self, str):
		# Ok, I give up.  The python build system wins.  Once
		# someone manages to get -lwsock32 on the
		# sharedmodules link command line, *after*
		# timesmodule.o, this can go away.
		return re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
			       str)

	def install (self):
		Python.install (self)
		for i in glob.glob ('%(install_root)s/usr/lib/python%(python_version)s/lib-dynload/*.so*' \
				    % self.get_substitution_dict ()):
			dll = re.sub ('\.so*', '.dll', i)
			self.system ('mv %(i)s %(dll)s', locals ())

		## UGH. 
		self.system ('''
cp %(install_root)s/usr/lib/python%(python_version)s/lib-dynload/* %(install_root)s/usr/bin
''')
		self.system ('''
chmod 755 %(install_root)s/usr/bin/*
''')
