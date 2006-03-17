import re

import download
import targetpackage
from toolpackage import Tool_package

class Gmp (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='4.1.4',
			   depends=['libtool'])
		
		self.target_architecture = re.sub ('i[0-9]86-', 'i386-', settings.target_architecture)

	# ugh.
	def configure_command (self):
		cmd = targetpackage.Target_package.configure_command (self)

		flags = ' -g -O2 -fomit-frame-pointer -march=i386 '
		return cmd

	def configure (self):
		targetpackage.Target_package.configure (self)
		# # FIXME: libtool too old for cross compile
		self.update_libtool ()
		# automake's Makefile.in's too old for new libtool,
		# but autoupdating breaks even more.  This nice
		# hack seems to work.
		self.file_sub ([('#! /bin/sh', '#! /bin/sh\ntagname=CXX')],
			       '%(builddir)s/libtool')
		
class Gmp__darwin (Gmp):
	def patch (self):

		## powerpc/darwin cross barfs on all C++ includes from
		## a C linkage file.
		## don't know why. Let's patch C++ completely from GMP.

		self.file_sub ([('__GMP_DECLSPEC_XX std::[oi]stream& operator[<>][^;]+;$', ''),
				('#include <iosfwd>', ''),
				('<cstddef>','<stddef.h>')
				],
			       '%(srcdir)s/gmp-h.in')
		Gmp.patch (self)

class Gmp__mingw (Gmp):
	def __init__ (self,settings):
		Gmp.__init__ (self, settings)
		
		# Configure (compile) without -mwindows for console
		self.target_gcc_flags = '-mms-bitfields'
		
	def patch (self):
		self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gmp-4.1.4-1.patch
''')

	def configure (self):
		Gmp.configure (self)

	def install (self):
		Gmp.install (self)
		self.system ('''
mv %(install_root)s/usr/lib/*dll %(install_root)s/usr/bin || true
''')

class Gmp__local (Tool_package):
	def __init__ (self, s):
		Tool_package.__init__ (self, s)
		self.with (version='4.1.4',
			   depends=['libtool'])


