import glob
import re
import os

import context
import cross
import download
import gub

class Odcctools (cross.Cross_package):
	def configure (self):
		cross.Cross_package.configure (self)

		## remove LD64 support.
		self.file_sub ([('ld64','')],
			       self.builddir () + '/Makefile')

class Darwin_sdk (gub.Sdk_package):
	def __init__ (self, s):
		gub.Sdk_package.__init__ (self, s)

		os_version = 7
		if s.platform == 'darwin-x86':
			os_version = 8
			
		name = 'darwin%d-sdk' % os_version
		ball_version = '0.4'
		format = 'gz'
		self.with (version='0.4',
			   mirror=download.hw % locals(), format='gz')

	def patch (self):
		self.system ('''
rm %(srcdir)s/usr/lib/libgcc*
rm %(srcdir)s/usr/lib/libstdc\+\+*
rm %(srcdir)s/usr/lib/libltdl*
rm %(srcdir)s/usr/include/ltdl.h
rm -rf %(srcdir)s/usr/lib/gcc
rm -f $(find %(srcdir)s -name FlexLexer.h)
''')

		## ugh, need to have gcc/3.3/machine/limits.h
		### self.system ('rm -rf %(srcdir)s/usr/include/gcc')
		##self.system ('rm -rf %(srcdir)s/usr/include/machine/limits.h')

		## limits.h symlinks into GCC.
		
		pat = self.expand ('%(srcdir)s/usr/lib/*.la')
		for a in glob.glob (pat):
			self.file_sub ([(r' (/usr/lib/.*\.la)', r'%(system_root)s\1')], a)


class Gcc (cross.Gcc):
	def patch (self):
		self.file_sub ([('/usr/bin/libtool', '%(crossprefix)s/bin/%(target_architecture)s-libtool')],
			       '%(srcdir)s/gcc/config/darwin.h')

	def configure_command (self):
		c = cross.Gcc.configure_command (self)
#		c = re.sub ('enable-shared', 'disable-shared', c)
		return c
	

	def configure (self):
		cross.Gcc.configure (self)
		self.file_sub ([("nm", "%(tool_prefix)snm ")],
			       "%(srcdir)s/libstdc++-v3/scripts/make_exports.pl")
		

	def rewire_gcc_libs (self):
		for l in  self.read_pipe ("find %(install_root)s/usr/lib/ -name '*.dylib'").split():
			id = self.read_pipe ('%(tool_prefix)sotool -L %(l)s', locals ()).split()[1]
			id = os.path.split (id)[1]
			self.system ('%(tool_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(l)s', locals ())
		
	def install (self):
		cross.Gcc.install (self)
		# self.rewire_gcc_libs ()
		
class Rewirer (context.Os_context_wrapper):
	def __init__ (self, settings):
		context.Os_context_wrapper.__init__ (self,settings)
		self.ignore_libs = None

	def get_libaries (self, name):
		lib_str = self.read_pipe ('''
%(crossprefix)s/bin/%(target_architecture)s-otool -L %(name)s
''',
					  locals (), ignore_error=True)

		libs = []
		for l in lib_str.split ('\n'):
			m = re.search (r"\s+(.*) \(.*\)", l)
			if not m:
				continue
			if self.ignore_libs.has_key (m.group (1)):
				continue

			libs.append (m.group (1))

		return libs

	def rewire_mach_o_object (self, name, substitutions):
		if not substitutions:
			return
		changes = ' '.join (['-change %s %s' % (o, d)
				     for (o, d) in substitutions])
		self.system ('''
%(crossprefix)s/bin/%(target_architecture)s-install_name_tool %(changes)s %(name)s ''',
			     locals ())

	def rewire_mach_o_object_executable_path (self, name):
		orig_libs = ['/usr/lib']

		libs = self.get_libaries (name)
		subs = []
		for l in libs:

			## ignore self.
			print os.path.split (l)[1], os.path.split (name)[1]
			
			if os.path.split (l)[1] == os.path.split (name)[1]:
				continue
			
			for o in orig_libs:
				if re.search (o, l):
					newpath = re.sub (o, '@executable_path/../lib/', l); 
					subs.append ((l, newpath))
				elif l.find (self.expand ('%(targetdir)s')) >= 0:
					print 'found targetdir in linkage', l
					raise 'abort'

		self.rewire_mach_o_object (name, subs)

	def rewire_binary_dir (self, dir):
		if not os.path.isdir (dir):
			return
		(root, dirs, files) = os.walk (dir).next ()
		files = [os.path.join (root, f) for f in files]

		for f in files:
			if os.path.isfile (f):
				self.rewire_mach_o_object_executable_path(f)

	def get_ignore_libs (self):
		str = self.read_pipe ('''
tar tfz %(gub_uploads)s/darwin-sdk-%(darwin_sdk_version)s.darwin.gub
''')
		d = {}
		for l in str.split ('\n'):
			l = l.strip ()
			if re.match (r'^\./usr/lib/', l):
				d[l[1:]] = True
		return d

	def rewire_root (self, root):
		if self.ignore_libs == None:
			self.ignore_libs = self.get_ignore_libs ()

		self.rewire_binary_dir (root + '/usr/lib')
		# Ugh.
		self.rewire_binary_dir (root + '/usr/lib/pango/1.4.0/modules/')
		self.rewire_binary_dir (root + '/usr/bin')

class Package_rewirer:
	def __init__ (self, rewirer, package):
		self.rewirer = rewirer
		self.package = package

	def rewire (self):
		self.rewirer.rewire_root (self.package.install_root ())


def add_rewire_path (settings, packages):
	rewirer = Rewirer (settings)
	for p in packages:
		if p.name () == 'darwin-sdk':
			continue

		wr = Package_rewirer (rewirer, p)
		p.postinstall = wr.rewire


def get_packages (settings, names):

	## Ugh, can we write settings?  
	packages = []
	
	

	packages.append (Darwin_sdk (settings))
		
	packages += [Odcctools (settings).with (version='20051122', mirror=download.opendarwin, format='bz2'),
		     Gcc (settings).with (version='4.1.0',
					  mirror=download.gcc_41,
					  format='bz2',
					  depends=['odcctools']),
		     ]

	return packages

def change_target_packages (packages):
	cross.change_target_packages (packages)
	for p in packages.values ():
		gub.change_target_dict (p, {

			## We get a lot of /usr/lib/ -> @executable_path/../lib/
			## we need enough space in the header to do these relocs.
			'LDFLAGS': '-Wl,-headerpad_max_install_names '
			})
		
		remove = ('libiconv', 'zlib')
		if p.name () in remove:
			del packages[p.name ()]
		if p.name_dependencies:
			p.name_dependencies = filter (lambda x: x not in remove,
						      p.name_dependencies)

def system (c):
	s = os.system (c)
	if s:
		raise 'barf'

def get_darwin_sdk ():
	def system (s):
		print s
		if os.system (s):
			raise 'barf'
		
	host  = 'maagd'
	version = '0.4'
	darwin_version  = 7

	dest =	'darwin%(darwin_version)d-sdk-%(version)s' % locals()
	
	system ('rm -rf %s' % dest)
	os.mkdir (dest)
	
	src = '/Developer/SDKs/'

	if darwin_version == 7:
		src += 'MacOSX10.3.9.sdk'
	else:
		src += 'MacOSX10.4u.sdk'
	
	cmd =  ('rsync -a -v %s:%s/ %s/ ' % (host, src, dest))
	system (cmd)
 	system ('chmod -R +w %s '  % dest)
	system ('tar cfz %s.tar.gz %s '  % (dest, dest))


if __name__== '__main__':
	get_darwin_sdk ()

