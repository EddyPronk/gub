import cvs
import download
import glob
import gub
import os
import re

class Mingw (gub.Target_package):
	def untar (self):
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

class Gmp (gub.Target_package):
	def xxconfigure (self):
		self.system ('''cd %(srcdir)s && libtoolize --force''')
		self.system ('''cd %(srcdir)s && ./missing --run aclocal''')
		self.system ('''cd %(srcdir)s && ./missing --run autoconf''')
		self.system ('''cd %(srcdir)s && ./missing --run automake''')
		self.file_sub ('ac_cv_c_bigendian=unknown',
			       'ac_cv_c_bigendian=${ac_cv_c_bigendian-unknown}',
			       '%(srcdir)s/configure')
		self.file_sub ("-Wl,-e,'\$dll_entry'", '',
			       '%(srcdir)s/configure')

		self.system ('''chmod +x %(srcdir)s/configure''')

		gub.Target_package.configure (self)
		
	def xpatch (self):
		if self.settings.platform == 'mingw':
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
		base = 'gmp'
		self.file_sub ('library_names=.*',
			       "library_names='lib%(base)s.dll.a'",
			       '%(installdir)s/lib/lib%(base)s.la',
			       locals ())

class Guile (gub.Target_package):
	def xpatch (self):
		if self.settings.platform == 'mingw':
	                ## FIXME
			self.system ('''
cd %(srcdir)s && patch -p1 < $HOME/installers/windows/patch/guile-1.7.2-3.patch
''')

	def configure_command (self):
		self.settings.target_gcc_flags = '-mms-bitfields'
		cmd = 'PATH_SEPARATOR=";" ' \
		      + gub.Target_package.configure_command (self) \
		      + gub.join_lines (''' 
--without-threads
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--disable-rpath
''')
		return cmd

	def configure (self):
		gub.Target_package.config_cache (self)
		self.dump ('%(builddir)s/config.cache', '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(systemdir)s/usr/lib"}
''', mode='a')
		gub.Package.configure (self)

		self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/libtool')
		self.file_sub ('^\(allow_undefined_flag=.*\)unsupported',
			       '\\1',
			       '%(builddir)s/guile-readline/libtool')


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
#		self.autoupdate (autodir=os.path.join (self.srcdir (),
#						       'builds/unix'))
		
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		gub.Package.configure (self)

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

		if self.settings.platform == 'mingw':
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
		Mingw (settings).with (version='3.8', download=gub.Package.skip),
		Libtool (settings).with (version='1.5.20'),
		Zlib (settings).with (version='1.2.2-1', mirror=download.lp, format='bz2'),
		Gettext (settings).with (version='0.14.5'),
		Libiconv (settings).with (version='1.9.2'),
		Freetype (settings).with (version='2.1.7-1', mirror=download.lp, format='bz2'),
		Expat (settings).with (version='1.95.8-1', mirror=download.lp, format='bz2'),
		Fontconfig (settings).with (version='2.3.2-1', mirror=download.lp, format='bz2'),
		Gmp (settings).with (version='4.1.4'),
		Guile (settings).with (version='1.7.2-3', mirror=download.lp, format='bz2'),
#		Guile (settings).with (version='1.7.2', mirror=download.gnu_alpha, format='bz2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
#		Pango (settings).with (version='1.10.1', mirror=download.gtk),
		LilyPond (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	}

	return packages[platform]
