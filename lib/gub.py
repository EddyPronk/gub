# own
import cvs
import download
import glob
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

		self.verbose = settings.verbose ()
		self.settings = settings
		self.url = ''
		self._downloader = self.wget
		self._dependencies = None
		self._build_dependencies = None
		
		self.checksum = '0000' 
		self.cross_checksum = '0000'
		
		# set to true for CVS releases
		self.track_development = False
		self.split_packages = []
		self.sover = '1'

		self.name_dependencies = []
		self.name_build_dependencies = []

	# urg: naming conflicts with module.
	def do_download (self):
		self._downloader ()

	def builder (self):
		available = dict (inspect.getmembers (self, callable))
		if self.settings.options.stage:
			(available[self.settings.options.stage]) ()
			return

		stages = ['untar', 'patch',
			  'configure', 'compile', 'install', 'split',
			  'package', 'dump_header_file', 'clean']

		tainted = False
		for stage in stages:
			if (not available.has_key (stage)):
				continue

			if self.is_done (stage, stages.index (stage)):
				tainted = True
				continue

			self.os_interface.log_command (' *** Stage: %s (%s)\n'
						       % (stage, self.name ()))

			if stage == 'package' and tainted and not self.settings.options.force_package:
				msg = self.expand ('''Compile was continued from previous run.
Will not package.
Use

  rm %(stamp_file)s

to force rebuild, or

  --force-package

to skip this check.
''')
				self.os_interface.log_command (msg)
				raise 'abort'


			if (stage == 'clean'
			    and self.settings.options.keep_build):
				os.unlink (self.get_stamp_file ())
				continue

			(available[stage]) ()

			if stage != 'clean':
				self.set_done (stage, stages.index (stage))

	def skip (self):
		pass

	def is_downloaded (self):
		name = self.expand ('%(downloaddir)s/%(file_name)s')
		return os.path.exists (name)

	def wget (self):
		if not self.is_downloaded ():
 			self.system ('''
cd %(downloaddir)s && wget %(url)s
''', locals ())

	def cvs (self):
		url = self.expand (self.url)
		dir = self.expand ('%(name)s-%(version)s')
		cvs_dest = self.expand ('%(downloaddir)s/%(dir)s' , locals ())
		if not os.path.exists (cvs_dest):
			self.system ('''
cd %(downloaddir)s && cvs -d %(url)s -q co -d %(dir)s -r %(version)s %(name)s
''', locals ())
		else:
# Hmm, let's save local changes?
#cd %(srcdir)s && cvs update -dCAP -r %(version)s
			self.system ('''
cd %(downloaddir)s/%(dir)s && cvs -q update -dAP -r %(version)s
''', locals ())

	@subst_method
	def name (self):
		file = self.__class__.__name__.lower ()
		file = re.sub ('__.*', '', file)
		file = re.sub ('_', '-', file)
		return file


	@subst_method
	def file_name (self):
		file = re.sub ('.*/([^/]+)', '\\1', self.url)
		return file

	@subst_method
	def basename (self):
                f = self.file_name ()
                f = re.sub ('.tgz', '', f)
                f = re.sub ('-src\.tar.*', '', f)
                f = re.sub ('\.tar.*', '', f)
                f = re.sub ('_%\(package_arch\)s.*', '', f)
                f = re.sub ('_%\(version\)s', '-%(version)s', f)
                return f

	@subst_method
	def full_version (self):
		return self.version ()

	@subst_method
	def build_dependencies_string (self):
		return ';'.join (self.name_build_dependencies)

	@subst_method
	def dependencies_string (self):
		return ';'.join (self.name_dependencies)

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
		return self.settings.allbuilddir + '/' + self.basename ()

	@subst_method
	def install_root (self):
		return self.settings.installdir + "/" + self.name () + '-root'

	@subst_method
	def install_prefix (self):
		return self.install_root () + '/usr'

	@subst_method
	def install_command (self):
		return '''make DESTDIR=%(install_root)s install'''

	@subst_method
	def configure_command (self):
		return '%(srcdir)s/configure --prefix=%(install_prefix)s'

	@subst_method
	def compile_command (self):
		return 'make'

	@subst_method
	def native_compile_command (self):
		c = 'make'
		if (self.settings.native_distcc_hosts):
			jobs = '-j%d ' % (2*len (self.settings.native_distcc_hosts.split (' ')))

			## do this a little complicated: we don't want a trace of
			## distcc during configure.
			c = 'DISTCC_HOSTS="%s" %s %s' % (self.settings.native_distcc_hosts, c, jobs)
			c = 'PATH="%(native_distcc_bindir)s:$PATH" ' + c
			
		return c


	@subst_method
        def gub_name (self):
		return '%(name)s-%(version)s.%(platform)s.gub'

	@subst_method
        def hdr_name (self):
		return '%(name)s.%(platform)s.hdr'

	@subst_method
        def hdr_file (self):
		return '%(gub_uploads)s/%(hdr_name)s'

	@subst_method
	def stamp_file (self):
		return '%(statusdir)s/%(name)s-%(version)s'

	@subst_method
	def rsync_command (self):
		return "rsync --exclude CVS -v -a %(downloaddir)s/%(name)s-%(version)s/ %(srcdir)s"

	def get_stamp_file (self):
		stamp = self.expand ('%(stamp_file)s')
		return stamp

	def is_done (self, stage, stage_number):
		f = self.get_stamp_file ()
		if os.path.exists (f):
			return pickle.load (open (f)) >= stage_number
		return False

	def set_done (self, stage, stage_number):
		pickle.dump (stage_number, open (self.get_stamp_file (),'w'))

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

	def broken_install_command (self):
		"""For packages that do not honor DESTDIR.
		"""

		# FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
		# so, must also ./configure that way
		return misc.join_lines ('''make install
bindir=%(install_prefix)s/bin
aclocaldir=%(install_prefix)s/share/aclocal
datadir=%(install_prefix)s/share
exec_prefix=%(install_prefix)s
gcc_tooldir=%(install_prefix)s
includedir=%(install_prefix)s/include
infodir=%(install_prefix)s/share/info
libdir=%(install_prefix)s/lib
libexecdir=%(install_prefix)s/lib
mandir=%(install_prefix)s/share/man
prefix=%(install_prefix)s
sysconfdir=%(install_prefix)s/etc
tooldir=%(install_prefix)s
''')

	def kill_libtool_installation_test (self, file):
		self.file_sub ([(r'if test "\$inst_prefix_dir" = "\$destdir"; then',
				 'if false && test "$inst_prefix_dir" = "$destdir"; then')],
			       file, must_succeed=True)
		
	def update_libtool (self):
		new_lt = self.expand ('%(system_root)s/usr/bin/libtool')

		if os.path.exists (new_lt):
			for lt in self.read_pipe ('find %(builddir)s -name libtool').split ():
				lt = lt.strip ()
				if not lt:
					continue

				self.system ('cp %(new_lt)s %(lt)s', locals ())
				self.kill_libtool_installation_test (lt)
				self.system ('chmod 755  %(lt)s', locals ())
		else:
			sys.stderr.write ('Cannot update libtool without libtools in system_root/usr/bin/.')

	def install (self):
		self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
rm -f %(install_root)s/usr/share/info/dir %(install_root)s/usr/cross/info/dir
''')
		self.libtool_installed_la_fixups ()

	def libtool_installed_la_fixups (self):
		for la in self.read_pipe ("cd %(install_root)s && find -name '*.la'").split ():
			la = la.strip ()
			(dir, base) = os.path.split (la)
			base = base[3:-3]
			dir = re.sub (r"^\./", "/", dir)
			full_la = self.expand ("%(install_root)s/%(la)s", locals())

			self.file_sub ([(''' *-L *[^\"\' ][^\"\' ]*''', ''),
					('''( |=|\')(/[^ ]*usr/lib|%(targetdir)s.*)/lib([^ \'/]*)\.(a|la|so)[^ \']*''',
					 '\\1-l\\3 '),
					('^old_library=.*',
					 """old_library='lib%(base)s.a'"""),
					],
				       full_la, env=locals ())
                        if self.settings.platform.startswith ('mingw'):
			         self.file_sub ([('library_names=.*',
						"library_names='lib%(base)s.dll.a'")],
						full_la, env=locals())

			# avoid using libs from build platform, by adding %(system_root)s
			self.file_sub ([('^libdir=.*',
					 """libdir='%(system_root)s/%(dir)s'"""),
					],
				       full_la, env=locals ())

	def split_devel (self):
		split_root = '%(install_root)s-devel'
		split_prefix = '%(install_root)s-devel/usr'
# Only static .a libs in devel, load time .la files go in LIB (or mingw
# BIN) package.
		self.system ('''
rm -rf %(split_root)s
mkdir -p %(split_prefix)s/bin
mv %(install_prefix)s/bin/*-config %(split_prefix)s/bin || true
tar -C %(install_root)s -cf - usr/include | tar -C %(split_root)s -xf -
rm -rf %(install_root)s/usr/include
mkdir -p %(split_prefix)s/lib
mv %(install_root)s/usr/lib/*.a %(split_prefix)s/lib || true
mv %(install_root)s/usr/lib/pkgconfig %(split_prefix)s/lib || true
mkdir -p %(split_prefix)s/share
tar -C %(install_root)s -cf - %(split_prefix)s/share/aclocal | tar -C %(split_root)s -xf -
rm -rf %(install_root)s/usr/share/aclocal
tar -C %(install_root)s -cf - %(split_prefix)s/share/libtool | tar -C %(split_root)s -xf -
rm -rf %(install_root)s/usr/share/libtool
rmdir %(install_root)s/usr/lib || true
rmdir %(install_root)s/usr/share || true
rmdir %(split_root)s/usr/lib || true
rmdir %(split_root)s/usr/share || true
''',
			     locals ())

	def split_doc (self):
		split_root = '%(install_root)s-doc'
		split_prefix = '%(install_root)s-doc/usr'
		self.system ('''
rm -rf %(split_root)s
mkdir -p %(split_prefix)s/share
tar -C %(install_prefix)s -cf - share/info | tar -C %(split_prefix)s -xf -
rm -rf %(install_root)s/usr/share/info
tar -C %(install_prefix)s -cf - share/man | tar -C %(split_prefix)s -xf -
rm -rf %(install_root)s/usr/share/man
tar -C %(install_prefix)s -cf - doc/%(name)s | tar -C %(split_prefix)s/share -xf -
tar -C %(install_prefix)s -cf - share/doc/%(name)s | tar -C %(split_prefix)s -xf -
rm -rf %(install_root)s/usr/doc/%(name)s %(install_root)s/usr/share/doc/%(name)s
rmdir %(split_root)s/usr/share/info || true
rmdir %(split_root)s/usr/share/man || true
rmdir %(split_root)s/usr/share/doc/%(name)s || true
rmdir %(split_root)s/usr/share || true
''',
			     locals ())

	def split_lib (self):
		split_root = '%(install_root)s-lib'
		split_prefix = '%(install_root)s-lib/usr'
# better move dlls to bin, see gmp
		self.system ('''
rm -rf %(split_root)s
mkdir -p %(split_prefix)s/bin
mv %(install_root)s/usr/bin/*.dll %(split_prefix)s/bin || true
mkdir -p %(split_prefix)s/lib
mv %(install_root)s/usr/lib/*.dll %(split_prefix)s/lib || true
mkdir -p %(split_prefix)s/lib
mv %(install_root)s/usr/lib/lib*.la %(split_prefix)s/lib || true
mkdir -p %(split_prefix)s/share
mv %(install_root)s/usr/share/%(name)s %(split_prefix)s/share || true
rmdir %(install_root)s/usr/bin || true
rmdir %(install_root)s/usr/lib || true
rmdir %(install_root)s/usr/share || true
rmdir %(split_root)s/usr/bin || true
rmdir %(split_root)s/usr/lib || true
rmdir %(split_root)s/usr/share || true
''',
			     locals ())

	def split (self):
		available = dict (inspect.getmembers (self, callable))
		for i in self.split_packages:
			available['split_' + i] ()

	def compile (self):
		self.system ('cd %(builddir)s && %(compile_command)s')

	# FIXME: should not misuse patch for auto stuff
	def patch (self):
		if not os.path.exists ('%(srcdir)s/configure' \
				       % self.get_substitution_dict ()):
			self.autoupdate ()

	@subst_method
        def gub_name_devel (self):
		return '%(name)s-devel-%(version)s.%(platform)s.gub'

	@subst_method
        def gub_name_doc (self):
		return '%(name)s-doc-%(version)s.%(platform)s.gub'

	@subst_method
        def gub_name_lib (self):
		if self.name ().startswith ('lib'):
			sover = self.sover
			return '%(name)s%(sover)s-%(version)s.%(platform)s.gub'
		return 'lib%(name)s%(sover)s-%(version)s.%(platform)s.gub'

	@subst_method
	def gub_ball (self):
		return '%(gub_uploads)s/%(gub_name)s'

	@subst_method
	def is_sdk_package (self):
		return 'false'
	
	def package (self):
		# naive tarball packages for now
		self.system ('''
rm -f $(find %(install_root)s -name '*~')
tar -C %(install_root)s -zcf %(gub_ball)s .
''')
		# WIP
		available = dict (inspect.getmembers (self, callable))
		for i in self.split_packages:
			split_gub_name = available['gub_name_' + i] ()
			self.system ('''
tar -C %(install_root)s-%(i)s -zcf %(gub_uploads)s/%(split_gub_name)s .
''',
				     locals ())

	def dump_header_file (self):
		hdr = self.expand ('%(hdr_file)s')
		self.log_command ("Writing %s\n" % hdr)
		pickle.dump (self.get_substitution_dict (), open (hdr, 'w'))

	def clean (self):
		self.system ('rm -rf  %(stamp_file)s %(install_root)s', locals ())
		if self.track_development:
			return

		self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

	def _untar (self, dir):
		tarball = self.expand("%(downloaddir)s/%(file_name)s")
		if not os.path.exists (tarball):
			raise 'no such file: ' + tarball
		if self.format == 'deb':
			self.system ('''
mkdir -p %(srcdir)s
ar p %(tarball)s data.tar.gz | tar -C %(dir)s -zxf-
''',
				     locals ())
		else:
			flags = download.untar_flags (tarball)
			self.system ('''
tar -C %(dir)s %(flags)s %(tarball)s
''',
				     locals ())

	def untar (self):
		if self.track_development:
			## cp options are not standardized.
			self.system (self.rsync_command ())
		else:
			self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
''')
			self._untar ('%(allsrcdir)s')

		## FIXME what was this for? --hwn
		self.system ('cd %(srcdir)s && chmod -R +w .')

	def with (self, version='HEAD', mirror=download.gnu,
		  format='gz', depends=[], builddeps=[],
		  track_development=False
		  ):
		self.format = format
		self.ball_version = version
		ball_version = version
		# Use copy of default empty depends, to be able to change it.
		self.name_dependencies = list (depends)
		self.name_build_dependencies = list (builddeps)
		self.track_development = track_development
		self.url = mirror

		## don't do substitution. We want to postpone
		## generating the dict until we're sure it doesn't change.

		return self

class Binary_package (Package):
	def untar (self):
		self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
''')
		self.system ('mkdir -p %(srcdir)s/root')
		self._untar ('%(srcdir)s/root')

	def configure (self):
		pass

	def patch (self):
		pass

	def compile (self):
		pass

	def install (self):
		self.system ('mkdir -p %(install_root)s')
		self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s -xvf-')
		self.libtool_installed_la_fixups ()

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

	## need to create a .gub, otherwise driver.py is confused: a
	## package should be installable after building.
	def package (self):
		self.system ('tar -czf %(gub_uploads)s/%(gub_name)s --files-from=/dev/null')

class Sdk_package (Null_package):
	def untar (self):
		Package.untar (self)

	## UGH: should store superclass names of each package.
	def is_sdk_package (self):
		return 'true'

	def package (self):
		self.system ('tar -C %(srcdir)s/ -czf %(gub_uploads)s/%(gub_name)s .')

class Change_target_dict:
	def __init__ (self, package, override):
		self._target_dict_method = package.get_substitution_dict
		self._add_dict = override

	def target_dict (self, env={}):
		env = env.copy()
		env.update (self._add_dict)
		d = self._target_dict_method (env)
		return d

	def append_dict (self, env= {}):
		d = self._target_dict_method ()
		for (k,v) in self._add_dict.items ():
			d[k] += v

		d.update (env)
		d = recurse_substitutions (d)
		return d

def change_target_dict (package, add_dict):
	"""Override the get_substitution_dict() method of PACKAGE."""
	try:
		package.get_substitution_dict = Change_target_dict (package, add_dict).target_dict
	except AttributeError:
		pass

def append_target_dict (package, add_dict):
	"""Override the get_substitution_dict() method of PACKAGE."""
	try:
		package.get_substitution_dict = Change_target_dict (package, add_dict).append_dict
	except AttributeError:
		pass
