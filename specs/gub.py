# own
import cvs
import download
import glob
import buildnumber
import misc


# sys
import pickle
import os
import re
import string
import subprocess
import sys
import time

from context import *

class Package (Os_context_wrapper):
	def __init__ (self, settings):
		Os_context_wrapper.__init__(self, settings)

		self.verbose = settings.verbose()
		self.settings = settings
		self.url = ''
		self._downloader = self.wget
		self._build = 0

		# set to true for CVS releases 
		self.track_development = False


	# fixme: rename download.py to mirrors.py
	def do_download (self):
		self._downloader()
		

	def skip (self):
		pass

	def wget (self):
		dir = self.settings.downloaddir
		url = self.expand (self.url)
		name = self.expand (dir + '/' + self.file_name ())
		if not os.path.exists (name):
			self.system ('''
cd %(dir)s && wget %(url)s
''', locals ())

	def cvs (self):
		dir = self.settings.allsrcdir
		url = self.expand (self.url)
		if not os.path.exists (os.path.join (dir, self.name ())):
			self.system ('''
cd %(dir)s && cvs -d %(url)s -q co -r %(version)s %(name)s
''', locals ())
		else:
# Hmm, let's save local changes?			
#cd %(dir)s/%(name)s && cvs update -dCAP -r %(version)s
			self.system ('''
cd %(dir)s/%(name)s && cvs -q update -dAP -r %(version)s
''', locals ())
		self.untar = self.skip

	@subst_method
	def build (self):
		return '%d' % self._build

	@subst_method
	def name (self):
		file = self.__class__.__name__.lower ()
		file = re.sub ('__.*', '', file)
		file = re.sub ('_', '-', file)
		return file


	@subst_method
	def file_name(self):
		file = re.sub ('.*/([^/]+)', '\\1', self.url)
		file = file.lower ()
		return file

	@subst_method
	def basename (self):
                f = self.file_name ()
                f = re.sub ('.tgz', '', f)
                f = re.sub ('-src\.tar.*', '', f)
                f = re.sub ('\.tar.*', '', f)
                return f
	
	@subst_method
	def full_version (self):
		return string.join ([self.version (), self.build ()], '-')

	@subst_method
	def version (self):
		return misc.split_version (self.ball_version)[0]

	@subst_method
	def name_version (self):
		return '%s-%s' % (self.name (), self.version ())

	@subst_method
	def srcdir (self):
		return self.settings.allsrcdir + '/' + self.basename ()

	@subst_method
	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	@subst_method
	def install_root (self):
		return self.settings.installdir + "/" + self.name () + '-root'

	@subst_method
	def install_prefix (self):
		return self.install_root () + '/usr'

	@subst_method
        def install_command (self):
                return 'make install'

	@subst_method
	def configure_command (self):
		return '%(srcdir)s/configure --prefix=%(install_prefix)s'

	@subst_method
	def compile_command (self):
		return 'make'

	@subst_method
        def gub_name (self):
		return '%(name)s-%(version)s-%(build)s.%(platform)s.gub'

	def get_builds  (self):
		return builds
	
	def set_current_build (self):
		bs = self.get_builds ()
		bs.sort()
		if bs:
			self._build = bs[-1] + 1
		else:
			self._build = 1

	def stamp_file (self):
		return self.expand ('%(statusdir)s/%(name)s-%(version)s-%(build)s')

	def is_done (self, stage, stage_number):
		f = self.stamp_file ()
		if os.path.exists (f):
			return pickle.load (open (f)) >= stage_number
		return False

	def set_done (self, stage, stage_number):
		pickle.dump (stage_number, open (self.stamp_file (),'w'))

	def autoupdate (self, autodir=0):
		if not autodir:
			autodir = self.srcdir ()
		if os.path.isdir (os.path.join (self.srcdir (), 'ltdl')):
			self.system ('''
rm -rf %(autodir)s/libltdl
cd %(autodir)s && libtoolize --force --copy --automake --ltdl
''', locals ())
		else:
			self.system ('''
cd %(autodir)s && libtoolize --force --copy --automake
''', locals ())
		if os.path.exists (os.path.join (autodir, 'bootstrap')):
			self.system ('''
cd %(autodir)s && ./bootstrap
''', locals ())
		elif os.path.exists (os.path.join (autodir, 'autogen.sh')):
			self.system ('''
cd %(autodir)s && bash autogen.sh --noconfigure
''', locals ())
		else:
			self.system ('''
cd %(autodir)s && aclocal
cd %(autodir)s && autoheader
cd %(autodir)s && autoconf
''', locals ())
			if os.path.exists (os.path.join (self.srcdir (), 'Makefile.am')):
				self.system ('''
cd %(srcdir)s && automake --add-missing
''', locals ())


	def configure (self):
		self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

	def update_libtool (self):
		self.system ('''find %(builddir)s -name libtool -exec cp -pv %(system_root)s/usr/bin/libtool \{\} \;''')

	def install (self):
		self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
''')
		self.libtool_la_fixups ()

	def libtool_la_fixups (self):
		dll_name = 'lib'
		for i in glob.glob ('%(install_prefix)s/lib/*.la' \
				    % self.get_substitution_dict ()):
			base = os.path.basename (i)[3:-3]
			self.file_sub ([
				(''' *-L *[^"' ][^"' ]*''', ''),
				('''( |=|')(/[^ ]*usr/lib/lib)([^ ']*)\.(a|la|so)[^ ']*''', '\\1-l\\3'),
				('^old_library=.*',
				"""old_library='lib%(base)s.a'"""),
				],
				i, env=locals ())
                        if self.settings.platform.startswith ('mingw'):
			         self.file_sub ([('library_names=.*',
						"library_names='lib%(base)s.dll.a'")],
						i, env=locals ())
			#  ' " ''' '

			# FIXME: avoid using libs from /usr/lib when
			# building linux, freebsd, mingw package.

			# Move this to xpm.py, and only do this after
			# installing?  But how does xpm know whether
			# we do a native install, as system install
			# or an installer install.

			#FIXME: not darwin, or all?
                        if (self.settings.platform.startswith ('linux')
			    or self.settings.platform.startswith ('freebsd')
			    or self.settings.platform.startswith ('mingw')):
				self.file_sub ([
				('^libdir=.*',
				"""libdir='%(system_root)s/usr/lib'"""),
				],
					       i, env=locals ())

	def compile (self):
		self.system ('cd %(builddir)s && %(compile_command)s')

	# FIXME: should not misuse patch for auto stuff
	def patch (self):
		if not os.path.exists ('%(srcdir)s/configure' \
				       % self.get_substitution_dict ()):
			self.autoupdate ()

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(install_root)s -zcf %(gub_uploads)s/%(gub_name)s .
''')

	def clean (self):
		stamp = self.stamp_file ()
		self.system ('rm -rf  %(stamp)s %(install_root)s', locals ())
		if self.track_development:
			return

		self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

	def untar (self):
		if self.track_development:
			return
		
		tarball = self.expand("%(downloaddir)s/%(file_name)s")
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		flags = download.untar_flags (tarball)
		
		# clean up
		self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
tar %(flags)s %(tarball)s -C %(allsrcdir)s
''',
			     locals ())

	def with (self, version='HEAD', mirror=download.gnu,
		  format='gz', depends=[],
		  track_development=False
		  ):
		self.format = format
		self.ball_version = version
		ball_version = version
		# Use copy of default empty depends, to be able to change it.
		self.name_dependencies = list (depends)
		self.track_development = track_development
		self.url = mirror

		## don't do substitution. We want to postpone
		## generating the dict until we're sure it doesn't change. 

		return self
class Binary_package (Package):
	def untar (self):
		self.system ('rm -rf %(srcdir)s %(builddir)s %(install_root)s')
		self.system ('mkdir -p %(srcdir)s/root')
		tarball = self.expand ('%(downloaddir)s/%(file_name)s')
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		flags = download.untar_flags (tarball)
		
		self.system ('tar %(flags)s %(tarball)s -C %(srcdir)s/root', locals ())

	def configure (self):
		pass

	def patch (self):
		pass

	def compile (self):
		pass

	def install (self):
		self.system ('mkdir -p %(install_root)s')
		self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s -xvf-')


class Null_package (Package):
	"""Placeholder for downloads """
	
	def compile (self):
		pass
	def configure (self):
		pass
	def install (self):
		pass
	def untar (self):
		pass
	def patch (self):
		pass
	def package (self):
		self.system ("tar -czf %(gub_uploads)s/%(gub_name)s --files-from=/dev/null")
		
class Sdk_package (Null_package):
	def untar (self):
		Package.untar (self)
	def package (self):
		self.system ('tar -C %(srcdir)s/ -czf %(gub_uploads)s/%(gub_name)s .')

class Change_target_dict:
	def __init__ (self, package, override):
		self._target_dict_method = package.target_dict
		self._add_dict = override
		
	def target_dict (self, env={}):
		d = self._target_dict_method (env)
		d.update (self._add_dict)
		return d

def change_target_dict (package, addict):
	"""Override the target_dict() method of PACKAGE."""
	try:
		package.target_dict = Change_target_dict (package, addict).target_dict
	except AttributeError:
		pass
