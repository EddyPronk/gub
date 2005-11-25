import cvs
import download
import gub
import re

class Libtool (gub.Target_package):
	pass

class LilyPond (gub.Target_package):
	pass

class Gettext (gub.Target_package):
	def configure_cache_overrides (self, str):
		str = re.sub ('ac_cv_func_select=yes','ac_cv_func_select=no', str)
		return str
	
	def configure_command (self):
		return gub.Target_package.configure_command (self) \
		       + ' --disable-csharp'
	
class Libiconv (gub.Target_package):
	pass

class Glib (gub.Target_package):
	def configure_cache_overrides (self, str):
		return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''

class Freetype (gub.Target_package):
	def configure (self):
		self.system ('''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
		gub.Package.configure (self)

	def install (self):
		self.system ('''
cd %(srcdir)s && ./configure --disable-static --enable-shared
''', { 'CC': 'cc'},
			     )
		gub.Package.install (self)
		

def read_pipe (cmd):
	pipe = os.popen (cmd, mode)
	output = pipe.read ()
	status = pipe.close ()
	# successful pipe close returns 'None'
	if status:
		raise 'barf'
	return output

class Fontconfig (gub.Target_package):
	def configure_command (self):
		return gub.Target_package.configure_command (self) + ''' \
--with-default-fonts=@WINDIR@\\fonts \
--with-add-fonts=@INSTDIR@\\usr\\share\\gs\\fonts \
'''

	def configure (self):
		self.system ('''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env = {'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(systemdir)s \
--exec-prefix=%(systemdir)s \ 
'''})
		gub.Package.configure (self)

		# help fontconfig cross compiling a bit, all CC/LD
		# flags are wrong, set to the target's root
		
		cflags = '-I%(srcdir)s -I%(srcdir)s/src' \
			 + read_pipe ('freetype-config --cflags')
		libs = read_pipe ('freetype-config --libs')
		for i in ('fc-case' 'fc-lang' 'fc-glyphname'):
			self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES=
''')

def get_packages (settings, platform):
	packages = {
	'mac': (
		Gettext (settings).with (version='0.10.40'),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
	),
	'mingw': (
		Libtool (settings).with (version='1.5.20'),
		Gettext (settings).with (version='0.14.5'),
		Libiconv (settings).with (version='1.9.2'),
		Glib (settings).with (version='2.8.4', mirror=download.gtk),
		Freetype (settings).with (version='2.1.9', mirror=download.freetype),
#		Fontconfig (settings).with (version='2.3.92', mirror=download.fontconfig),
		Fontconfig (settings).with (version='2.3.2', mirror=download.fontconfig),
		LilyPond (settings).with (mirror=cvs.gnu, download=gub.Package.cvs),
	),
	}

	return packages[platform]
