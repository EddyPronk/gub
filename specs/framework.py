import cvs
import download
import gub
import os
import re

class Mingw (gub.Target_package):
	def unpack (self):
		self.system ('mkdir -p %(srcdir)s/')
		self.dump ('%(srcdir)s/configure', '''
cat > Makefile <<EOF
default:
	@echo done
all: default
install:
	mkdir -p %(installdir)s
	tar -C %(MINGW_RUNTIME_DIR)s/%(target_architecture)s -cf- . | tar -C %(installdir)s -xvf-
	mkdir -p %(installdir)s/bin
	-cp /cygwin/usr/bin/cygcheck.exe %(installdir)s/bin
EOF
''')
		self.system ('chmod +x %(srcdir)s/configure')

class Libtool (gub.Target_package):
	pass

class LilyPond (gub.Target_package):
	def configure (self):
		self.autoupdate ()
		gub.Target_package.configure (self)

class Gettext (gub.Target_package):
	def configure_cache_overrides (self, str):
		str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		return str
	
	def configure_command (self):
		cmd = gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'

		if self.settings.platform == 'mac':
			cmd = re.sub ('--config-cache ', '', cmd) 
		return cmd
	
class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def configure_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

class Freetype (gub.Target_package):
	def configure (self):
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		gub.Package.configure (self)
		## FIXME: use handy file re.sub
		self.system ('''
sed -i~	-e "s@^LIBTOOL=.*@LIBTOOL=%(builddir)s/libtool --tag=CXX@" %(builddir)s/Makefile
''')
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

		if self.settings.platform == 'mingw':
			 cmd += gub.join_lines ('''
--with-default-fonts=@WINDIR@\\fonts\\
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts
''')

		return cmd
	
	def configure (self):
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env = {'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(installdir)s \
--exec-prefix=%(installdir)s \ 
'''})
		gub.Package.configure (self)
		if self.settings.platform == 'mingw':
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
	def xxconfigure (self):
		self.autoupdate ()
		gub.Target_package.configure (self)

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

def get_packages (settings, platform):
	packages = {
	'mac': (
		Gettext (settings).with (version='0.10.40'),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
	),
	'mingw': (
		Mingw (settings).with (version='3.8', download=gub.Package.skip),
		Libtool (settings).with (version='1.5.20'),
		Gettext (settings).with (version='0.14.5'),
		Libiconv (settings).with (version='1.9.2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
# vanilla 1.2.3 builds only static libraries
#		Zlib (settings).with (version='1.2.3', mirror=download.zlib, format='bz2'),
		Freetype (settings).with (version='2.1.7-1', mirror=download.lp, format='bz2'),
#		Freetype (settings).with (version='2.1.7', mirror=download.freetype),
# 2.1.9 builds only static libraries
#		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
# vanilla expat does not link
#		Expat (settings).with (version='1.95.8', mirror=download.sf),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
#		Fontconfig (settings).with (version='2.3.92', mirror=download.fontconfig),
#		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
		Fontconfig (settings).with (version='2.3.2-1', mirror=download.lp, format='bz2'),
		LilyPond (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	}

	return packages[platform]
