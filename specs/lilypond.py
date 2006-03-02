import glob
import os
import re

import cvs
import gub
import misc
import targetpackage

class LilyPond (targetpackage.Target_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
			   depends=['fontconfig', 'gettext',
				    'guile', 'pango', 'python', 'ghostscript'],
			   track_development=True)

		# FIXME: should add to C_INCLUDE_PATH
		builddir = self.builddir ()
		self.target_gcc_flags = (settings.target_gcc_flags
					 + ' -I%(builddir)s' % locals ())
		self._downloader = self.cvs

	def rsync_command (self):
		c = targetpackage.Target_package.rsync_command (self)
		c = c.replace ('rsync', 'rsync --delete --exclude configure')
		return c

	def configure_command (self):
		## FIXME: pickup $target-guile-config
		return (targetpackage.Target_package.configure_command (self)
			+ misc.join_lines ('''
--enable-relocation
--disable-documentation
--enable-static-gxx
--with-python-include=%(system_root)s/usr/include/python%(python_version)s
'''))

	def configure (self):
		self.autoupdate ()
	

	def do_configure (self):
		if not os.path.exists (self.expand ('%(builddir)s/FlexLexer.h')):
			flex = self.read_pipe ('which flex')
			flex_include_dir = os.path.split (flex)[0] + "/../include"
			gub.Package.system (self, '''
mkdir -p %(builddir)s
cp %(flex_include_dir)s/FlexLexer.h %(builddir)s/
''', locals ())
		targetpackage.Target_package.configure (self)

		self.file_sub ([('DEFINES = ', r'DEFINES = -DGHOSTSCRIPT_VERSION=\"%(ghostscript_version)s\" ')],
			       '%(builddir)s/config.make')
		
	# FIXME: shared for all CVS packages
	def srcdir (self):
		return '%(allsrcdir)s/%(name)s-%(version)s'

#	# FIXME: shared for all CVS packages
	def builddir (self):
		return '%(targetdir)s/build/%(name)s-%(version)s'

	def compile (self):
		d = self.get_substitution_dict ()
		if (misc.file_is_newer ('%(srcdir)s/config.make.in' % d,
				   '%(builddir)s/config.make' % d)
		    or misc.file_is_newer ('%(srcdir)s/GNUmakefile.in' % d,
				      '%(builddir)s/GNUmakefile' % d)
		    or misc.file_is_newer ('%(srcdir)s/config.hh.in' % d,
				      '%(builddir)s/config.make' % d)
		    or misc.file_is_newer ('%(srcdir)s/configure' % d,
				      '%(builddir)s/config.make' % d)):
			self.do_configure ()
			
		targetpackage.Target_package.compile (self)

	def compile_command (self):
		s = targetpackage.Target_package.compile_command (self)
		if self.settings.lilypond_branch == 'lilypond_2_6':
			# ugh, lilypond-2.6 has broken srcdir build system
			# and gub is leaking all kind of vars.
			s = 'unset builddir srcdir topdir;' + s

		return s
		
        def name_version (self):
		# whugh
		if os.path.exists (self.srcdir ()):
			d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
			return 'lilypond-%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
		return targetpackage.Target_package.name_version (self)

	def install (self):
		targetpackage.Target_package.install (self)
		d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
		v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
		self.system ("cd %(install_root)s/usr/share/lilypond && rm -f current && ln -sf %(v)s current",
			     locals ())

		self.system ("cd %(install_root)s/usr/lib/lilypond && rm -f current && ln -sf %(v)s current",
			     locals ())


        def gub_name (self):
		nv = self.name_version ()
		p = self.settings.platform
		return '%(nv)s.%(p)s.gub' % locals ()

	def autoupdate (self, autodir=0):
		autodir = self.srcdir ()

		if (misc.file_is_newer (self.expand ('%(autodir)s/configure.in', locals ()),
				   self.expand ('%(builddir)s/config.make',locals ()))
		    or misc.file_is_newer (self.expand ('%(autodir)s/stepmake/aclocal.m4', locals ()),
				      self.expand ('%(autodir)s/configure', locals ()))):
			self.system ('''
			cd %(autodir)s && bash autogen.sh --noconfigure
			''', locals ())
			self.do_configure ()

class LilyPond__cygwin (LilyPond):
	def __init__ (self, settings):
		LilyPond.__init__ (self, settings)
		self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
			   depends=['fontconfig', 'freetype2', 'guile', 'pango', 'python'],
			   builddeps=['gettext-devel', 'glib-devel', 'guile', 'libfreetype2-devel', 'pango-devel', 'python'],
			   track_development=True)

        def patch (self):
		# FIXME: for our gcc-3.4.5 cross compiler in the mingw
		# environment, THIS is a magic word.
		self.file_sub ([('THIS', 'SELF')],
			       '%(srcdir)s/lily/parser.yy')

	def compile_command (self):
		python_lib = "%(system_root)s/usr/bin/libpython%(python_version)s.dll"
		LDFLAGS = '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api'

		return (LilyPond.compile_command (self)
		       + misc.join_lines ('''
LDFLAGS="%(LDFLAGS)s %(python_lib)s"
'''% locals ()))

class LilyPond__mingw (LilyPond__cygwin):
	def __init__ (self, settings):
		LilyPond__cygwin.__init__ (self, settings)
		self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
			   depends=['fontconfig', 'gettext',
				    'guile', 'pango', 'python', 'ghostscript', 'cygwin', 'lilypad'],
			   track_development=True)

	def do_configure (self):
		LilyPond__cygwin.do_configure (self)
##		# Configure (compile) without -mwindows for console
##		self.target_gcc_flags = '-mms-bitfields'
		self.config_cache ()
		cmd = (self.configure_command ()
		       + ' --enable-config=console')
		self.system ('''cd %(builddir)s && %(cmd)s''',
			     locals ())
		## conf=console: no -mwindows
		self.file_sub ([(' -mwindows', ' '),
				('DEFINES = ', r'DEFINES = -DGHOSTSCRIPT_VERSION=\"%(ghostscript_version)s\" '),
				(' -g ', ' '),
				],
			       '%(builddir)s/config-console.make')
		self.file_sub ([(' -g ', ' ')],
				'%(builddir)s/config.make')

	def compile (self):
		LilyPond.compile (self)
		gub.Package.system (self, '''
mkdir -p %(builddir)s/mf/out-console
cp -pv %(builddir)s/mf/out/* %(builddir)s/mf/out-console
''')
		cmd = LilyPond__mingw.compile_command (self)
		cmd += ' conf=console'
		self.system ('''cd %(builddir)s && %(cmd)s''',
			     locals ())

	def install (self):
		LilyPond__cygwin.install (self)
		self.system ('''

rm -f %(install_prefix)s/bin/lilypond-windows
install -m755 %(builddir)s/lily/out/lilypond %(install_prefix)s/bin/lilypond-windows.exe
rm -f %(install_prefix)s/bin/lilypond
install -m755 %(builddir)s/lily/out-console/lilypond %(install_prefix)s/bin/lilypond.exe
cp %(install_root)s/usr/lib/lilypond/*/python/* %(install_root)s/usr/bin
cp %(install_root)s/usr/share/lilypond/*/python/* %(install_root)s/usr/bin
''')
		for i in glob.glob (('%(install_root)s/usr/bin/*'
				     % self.get_substitution_dict ())):
			s = self.read_pipe ('file %(i)s' % locals ())
			if s.find ('guile') >= 0:
				self.system ('mv %(i)s %(i)s.scm', locals ())
			elif  s.find ('python') >= 0:
				self.system ('mv %(i)s %(i)s.py', locals ())

		for i in self.read_pipe ('''
find %(install_root)s -name "*.ly"
''').split ():
			s = open (i).read ()
			open (i, 'w').write (re.sub ('\r*\n', '\r\n', s))

class LilyPond__debian (LilyPond):
	def __init__ (self, settings):
		LilyPond.__init__ (self, settings)
		self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
			   builddeps=['libfontconfig1-dev', 'guile-1.6-dev', 'libpango1.0-dev', 'python-dev'],
			   track_development=True)

class LilyPond__darwin (LilyPond):
	def __init__ (self, settings):
		LilyPond.__init__ (self, settings)
		self.with (version=settings.lilypond_branch, mirror=cvs.gnu, track_development=True,
			   depends=['pango', 'guile', 'gettext', 'ghostscript', 'fondu', 'osx-lilypad']
			   ),

	def configure_command (self):
		cmd = LilyPond.configure_command (self)

		pydir = ('%(system_root)s/System/Library/Frameworks/Python.framework/Versions/%(python_version)s'
			 + '/include/python%(python_version)s')

		cmd += ' --with-python-include=' + pydir
		cmd += ' --enable-static-gxx '
		
		return cmd

	def do_configure (self):
		LilyPond.do_configure (self)

		make = self.expand ('%(builddir)s/config.make')

		if re.search ("GUILE_ELLIPSIS", open (make).read ()):
			return
		self.file_sub ([('CONFIG_CXXFLAGS = ',
				 'CONFIG_CXXFLAGS = -DGUILE_ELLIPSIS=... '),
#				(' -O2 ', '')
## ugh. this will break if other progs use -g too
				(' -g ', ' ')
				],
			       '%(builddir)s/config.make')

#Hmm
Lilypond = LilyPond
Lilypond__cygwin = LilyPond__cygwin
Lilypond__darwin = LilyPond__darwin
Lilypond__debian = LilyPond__debian
Lilypond__mingw = LilyPond__mingw
