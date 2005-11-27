import cvs
import download
import gub
import os
import re

class Libtool (gub.Target_package):
	pass

class Gs (gub.Target_package):
	pass

class Python (gub.Target_package):
	def xxpatch (self):
		if self.settings.platform.startswith ('mingw'):
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/python-2.4.2-1.patch
''')

class LilyPad (gub.Target_package):
	pass

class Gmp (gub.Target_package):
	def xxconfigure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force --copy''')
		self.system ('''cd %(srcdir)s && ./missing --run aclocal''')
		self.system ('''cd %(srcdir)s && ./missing --run autoconf''')
		self.system ('''cd %(srcdir)s && ./missing --run automake''')
		self.file_sub ('ac_cv_c_bigendian=unknown',
			       'ac_cv_c_bigendian=${ac_cv_c_bigendian-unknown}',
			       '%(srcdir)s/configure')
		self.file_sub ("-Wl,-e,'\$dll_entry'", '',
			       '%(srcdir)s/configure')

		os.chmod ('%(srcdir)s/configure' % self.package_dict (), 0755)
		gub.Target_package.configure (self)
		
	def xpatch (self):
		if self.settings.platform.startswith ('mingw'):
	                ## FIXME, seems we don't need this?
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/gmp-4.1.4-1.patch
''')

	def install (self):
		gub.Target_package.install (self)
		# minimal libtool fixups
		self.system ('''
mkdir -p %(installdir)s/bin
mv %(installdir)s/lib/lib*.dll %(installdir)s/bin/
cp %(builddir)s/.libs/libgmp.dll.a %(installdir)s/lib/
''')

class Guile (gub.Target_package):
	def xpatch (self):
		if self.settings.platform.startswith ('mingw'):
	                ## FIXME
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/guile-1.7.2-3.patch
''')

	def configure_command (self):
		cmd = ''
		if self.settings.platform.startswith ('mingw'):
			self.settings.target_gcc_flags = '-mms-bitfields'
			self.settings.target_gxx_flags = '-mms-bitfields'
			cmd = gub.join_lines ('''\
PATH_SEPARATOR=";"
AS=%(target_architecture)s-as
''')
		cmd += gub.Target_package.configure_command (self) \
		      + gub.join_lines (''' 
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
''')
		return cmd

	def config_cache_overrides (self, str):
		if self.settings.platform.startswith ('mingw'):
			str += '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(systemdir)s/usr/lib"}
'''
		return str

	def configure (self):
		gub.Target_package.configure (self)
		if self.settings.platform.startswith ('mingw'):
			self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/libtool')
			self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/guile-readline/libtool')
			self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/libtool''')
			self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/guile-readline/libtool''')

	def install (self):
		gub.Target_package.install (self)
		version = self.read_pipe ('''\
GUILE_LOAD_PATH=%(installdir)s/share/guile/* %(installdir)s/bin/guile-config --version 2>&1\
''').split ()[-1]
		self.dump ('%(installdir)s/bin/%(target_architecture)s-guile-config', '''\
#!/bin/sh
[ "$1" == "--version" ] && echo "%(target_architecture)s-guile-config - Guile version $GUILE"
[ "$1" == "compile" ] && echo "-I%(systemdir)s/usr/include"
[ "$1" == "link" ] && echo "-L%(systemdir)s/usr/lib -lguile -lgmp"
exit 0
''')
		os.chmod ('%(installdir)s/bin/%(target_architecture)s-guile-config', 0755)
	

class LilyPond (gub.Target_package):
	def configure (self):
		self.autoupdate ()
		gub.Target_package.configure (self)

class Gettext (gub.Target_package):
	def config_cache_overrides (self, str):
		if self.settings.platform == 'mingw':
			str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		if 0:
			# this for mingw-3.7 only, but mingw-3.8 does not link
			# guile.exe
			str += '''
# gettext does not include winsock2.h -- do not feel like patching right now
# but in mingw only if winsock2.h
ac_cv_func_select=${ac_cv_func_select=no}
# only in additional library -- do not feel like patching right now
gl_cv_func_mbrtowc=${gl_cv_func_mbrtowc=no}
jm_cv_func_mbrtowc=${jm_cv_func_mbrtowc=no}
'''
		return str

	def configure_command (self):
		cmd = gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'

		if self.settings.platform == 'mac':
			cmd = re.sub ('--config-cache ', '', cmd) 
		return cmd
	
	def configure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force --copy''')
		gub.Target_package.configure (self)

class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def config_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

class Pango (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + gub.join_lines ('''
--without-x
--without-cairo
''')

	def configure (self):
		gub.Target_package.configure (self)
		if self.settings.platform.startswith ('mingw'):
			self.system ('''cp $HOME/installers/windows/bin/%(target_architecture)s-libtool %(builddir)s/libtool''')

class Freetype (gub.Target_package):
	def configure (self):
#		self.autoupdate (autodir=os.path.join (self.srcdir (),
#						       'builds/unix'))
		
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		gub.Target_package.configure (self)

		self.file_sub ('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX', '%(builddir)s/Makefile')

		self.dump ('%(builddir)s/Makefile', '''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''', mode='a')

	def install (self):
		gub.Package.system (self, '''
cd %(srcdir)s && ./configure --disable-static --enable-shared
''')
		gub.Package.install (self)
		

class Fontconfig (gub.Target_package):
	def configure_command (self):
		# FIXME: system dir vs packaging install
		cmd = gub.Target_package.configure_command (self) \
		      + gub.join_lines (''' 
--with-freetype-config="/usr/bin/freetype-config
--prefix=%(systemdir)s/usr
--exec-prefix=%(systemdir)s/usr
"''')

		if self.settings.platform.startswith ('mingw'):
			 cmd += gub.join_lines ('''
--with-default-fonts=@WINDIR@\\fonts\\
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts
''')

		return cmd
	
	def configure (self):
##		self.autoupdate ()
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env = {'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(installdir)s \
--exec-prefix=%(installdir)s \ 
'''})
		gub.Target_package.configure (self)
		if self.settings.platform.startswith ('mingw'):
			self.dump ('%(builddir)s/config.h', '''
#define sleep(x) _sleep (x)
''', mode='a')
		# help fontconfig cross compiling a bit, all CC/LD
		# flags are wrong, set to the target's root
		
		cflags = '-I%(srcdir)s -I%(srcdir)s/src ' \
			 + self.read_pipe ('freetype-config --cflags')[:-1]
		libs = self.read_pipe ('freetype-config --libs')[:-1]
		for i in ('fc-case', 'fc-lang', 'fc-glyphname'):
			self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES=
''', locals ())

class Expat (gub.Target_package):
#	def configure (self):
#		self.autoupdate ()
#		gub.Target_package.configure (self)

	def compile_command (self):
		return gub.Target_package.compile_command (self) + ''' \
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H" \
EXEEXT= \
'''
	def install_command (self):
		return gub.Target_package.install_command (self) + ''' \
EXEEXT= \
exec_prefix=%(installdir)s \
libdir=%(installdir)s/lib \
includedir=%(installdir)s/include \
man1dir=%(installdir)s/share/man/man1 \
'''

class Zlib (gub.Target_package):
	def configure (self):
		self.system ('''
sed -i~ 's/mgwz/libz/' %(srcdir)s/configure
shtool mkshadow %(srcdir)s %(builddir)s
cd %(builddir)s && target=mingw AR="%(AR)s r" %(srcdir)s/configure --shared
''')

# latest vanilla packages
#Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
#Freetype (settings).with (version='2.1.9', mirror=download.freetype),
#Expat (settings).with (version='1.95.8', mirror=download.sf),
#Fontconfig (settings).with (version='2.3.92', mirror=download.fontconfig),
#Gettext (settings).with (version='0.14.5'),

def get_packages (settings, platform):
	packages = {
	'mac': (
		Gettext (settings).with (version='0.10.40'),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
		Expat (settings).with (version='1.95.8', mirror=download.sourceforge, format='gz'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
	),
	'mingw': (
		Libtool (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
		Gettext (settings).with (version='0.14.1-1', mirror=download.lp, format='bz2'),
		Libiconv (settings).with (version='1.9.2'),
		Freetype (settings).with (version='2.1.7-1', mirror=download.lp, format='bz2'),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig (settings).with (version='2.3.2-1', mirror=download.lp, format='bz2'),
		Gmp (settings).with (version='4.1.4'),
		Guile (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Pango (settings).with (version='1.10.1', mirror=download.gtk),
		Python (settings).with (version='2.4.2-1', mirror=download.lp, format='bz2'),
#		Python (settings).with (version='2.4.2', mirror=download.python),
		Gs (settings).with (version='8.15-1', mirror=download.lp, format='bz2'),
		LilyPond (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
		LilyPad (settings).with (version='0.0.7-1', mirror=download.lp, format='bz2'),
	),
	}

	return packages[platform]
