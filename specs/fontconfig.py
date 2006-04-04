import download
import gub
import misc
import targetpackage
import toolpackage

class Fontconfig (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version='2.3.2', mirror=download.fontconfig,
			   depends=['expat', 'freetype', 'libtool']),

	def configure_command (self):
		# FIXME: system dir vs packaging install

		## UGH  - this breaks  on Darwin!
		return targetpackage.Target_package.configure_command (self) \
		      + misc.join_lines ('''
--with-freetype-config="%(system_root)s/usr/bin/freetype-config
--prefix=%(system_root)s/usr
"''')
#--urg-broken-if-set-exec-prefix=%(system_root)s/usr

	def configure (self):
		gub.Package.system (self, '''
		rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''',
			     env={'ft_config' : '''/usr/bin/freetype-config \
--prefix=%(system_root)s/usr \
'''})
#--urg-broken-if-set-exec-prefix=%(system_root)s/usr \
		targetpackage.Target_package.configure (self)

		# # FIXME: libtool too old for cross compile
		self.update_libtool ()

		# FIXME: how to put in __mingw class without duplicating
		# configure ()
		if self.settings.platform.startswith ('mingw'):
			self.dump ('''
#define sleep(x) _sleep (x)
''',
				   '%(builddir)s/config.h',
				   mode='a')
		# help fontconfig cross compiling a bit, all CC/LD
		# flags are wrong, set to the target's root

		cflags = '-I%(srcdir)s -I%(srcdir)s/src ' \
			 + self.read_pipe ('freetype-config --cflags')[:-1]
		libs = self.read_pipe ('freetype-config --libs')[:-1]
		for i in ('fc-case', 'fc-lang', 'fc-glyphname'):
			self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES=
''', locals ())

		self.file_sub ([('DOCSRC *=.*', 'DOCSRC=')],
			       '%(builddir)s/Makefile')

	def patch (self):
		targetpackage.Target_package.patch (self)
		self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/fontconfig-2.3.2-mingw-fccache.patch')
		

class Fontconfig__mingw (Fontconfig):
	## no need to add c:\windows\fonts. FontConfig does this
	## automatically

	def x__init__ (self, settings):
		Fontconfig.__init__ (self, settings)
		self.with (version='2.3.94', mirror=download.fontconfig,
			   depends=['expat', 'freetype', 'libtool'])

	def patch (self):
		Fontconfig.patch (self)
		self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/fontconfig-2.3.2-mingw-timestamp.patch")

class Fontconfig__darwin (Fontconfig):
	def configure_command (self):
		cmd = Fontconfig.configure_command (self)
		cmd += ' --with-add-fonts=/Library/Fonts,/System/Library/Fonts '
		return cmd

	def configure (self):
		Fontconfig.configure (self)
		self.file_sub ([('-Wl,[^ ]+ ', '')],
			       '%(builddir)s/src/Makefile')


class Fontconfig__linux (Fontconfig):
	def configure (self):
		Fontconfig.configure (self)
		self.file_sub ([
			('^sys_lib_search_path_spec="/lib/* ',
			 'sys_lib_search_path_spec="%(system_root)s/usr/lib /lib '),
			# FIXME: typo: dl_search (only dlsearch exists).
			# comment-out for now
			#('^sys_lib_dl_search_path_spec="/lib/* ',
			# 'sys_lib_dl_search_path_spec="%(system_root)s/usr/lib /lib ')
			],
			       '%(builddir)s/libtool')


class Fontconfig__freebsd (Fontconfig__linux):
	pass


class Fontconfig__local (toolpackage.Tool_package):
	def __init__ (self, settings):
		toolpackage.Tool_package.__init__ (self, settings)
		self.with (version='2.3.2', mirror=download.fontconfig,
			   depends=['expat', 'freetype'])
		
