import os
import re

import download
import framework
import gub

class Binutils (framework.Binutils):
	pass

class Gcc (framework.Gcc):
	def patch (self):
		# FIXME: set system_root to %(tooldir)s/%(target_architecture)s,
		# or copy mingw-runtime/win32api here?
		self.system ('''
mkdir -p %(tooldir)s/%(target_architecture)s
tar -C %(system_root)s/usr -cf- include lib | tar -C %(tooldir)s/%(target_architecture)s -xf-
''')

class Mingw_runtime (gub.Binary_package):
	def untar (self):
		gub.Binary_package.untar (self)
		self.system ('mkdir -p %(srcdir)s/root/usr')
		self.system ('cd %(srcdir)s/root && mv * usr',
			     ignore_error=True)

class Cygwin (gub.Binary_package):
	"Only need the cygcheck.exe binary."
	
	def untar (self):
		gub.Binary_package.untar (self)

		file = '%s/root/usr/bin/cygcheck.exe' % self.srcdir ()
		cygcheck = open (file).read ()
		self.system ('rm -rf %(srcdir)s/root')
		self.system ('mkdir -p %(srcdir)s/root/usr/bin/')
		open (file, 'w').write (cygcheck)

	def basename (self):
		f = gub.Binary_package.basename (self)
		f = re.sub ('-1$', '', f)
		return f

class W32api (gub.Binary_package):
	def untar (self):
		gub.Binary_package.untar (self)
		self.system ('mkdir -p %(srcdir)s/root/usr')
		self.system ('cd %(srcdir)s/root && mv * usr',
			     ignore_error=True)

class Regex (gub.Target_package):
	pass

class Gs (gub.Binary_package):
	def untar (self):
		gub.Binary_package.untar (self)
		self.system ('cd %(srcdir)s && mv root/gs-%(version)s/* .')

	def install (self):
		gs_prefix = '/usr/share/gs'
		self.system ('''
mkdir -p %(install_root)s/usr
tar -C %(srcdir)s -cf- bin | tar -C %(install_root)s/usr -xvf-
mkdir -p %(install_root)s/%(gs_prefix)s
tar -C %(srcdir)s -cf- fonts lib Resource | tar -C %(install_root)s/%(gs_prefix)s -xvf-
fc-cache %(install_root)s/%(gs_prefix)s/fonts
mkdir -p %(install_root)s/usr/share/doc/gs/html
tar -C %(srcdir)s/doc -cf- --exclude='[A-Z]*[A-Z]' . | tar -C %(install_root)s/usr/share/doc/gs/html -xvf-
tar -C %(srcdir)s/doc -cf- --exclude='*.htm*' . | tar -C %(install_root)s/usr/share/doc/gs/html -xvf-
''',
			     env=locals ())

class LilyPad (gub.Target_package):
	def makeflags (self):
		# FIXME: better fix Makefile
		return gub.join_lines ('''
ALL_OBJS='$(OBJS)'
WRC=/usr/bin/wrc
CPPFLAGS=-I%(system_root)s/usr/include
RC='$(WRC) $(CPPFLAGS)'
LIBWINE=
LIBPORT=
MKINSTALLDIRS=%(srcdir)s/mkinstalldirs
INSTALL_PROGRAM=%(srcdir)s/install-sh
''')
		
	def compile_command (self):
		return gub.Target_package.compile_command (self) \
		       + self.makeflags ()

	def install_command (self):
		return gub.Target_package.broken_install_command (self) \
		       + self.makeflags ()

def get_packages (settings):
	return (
		Mingw_runtime (settings).with (version='3.9', mirror=download.mingw),
		W32api (settings).with (version='3.5', mirror=download.mingw),
		Binutils (settings).with (version='2.16.1', format='bz2'),
		Cygwin (settings).with (version='1.5.18-1', mirror=download.cygwin, format='bz2', depends=['mingw-runtime']), 
		Gs (settings).with (version='8.15-1', mirror=download.lp, format='bz2', depends=['mingw-runtime']),
#		Gcc (settings).with (version='4.0.2', mirror=download.gcc, format='bz2'),
		Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2'),
		Regex (settings).with (version='2.3.90-1', mirror=download.lp, format='bz2', depends=['mingw-runtime']),
		LilyPad (settings).with (version='0.0.7-1', mirror=download.lp, format='bz2'),
		)

