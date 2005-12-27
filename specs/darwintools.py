import glob
import re
import os
import context
import download
import framework
import gub

class Odcctools (gub.Cross_package):
	def install_prefix (self):
		return self.settings.tooldir
	
	def configure (self):
		gub.Cross_package.configure (self)

		## remove LD64 support.
		self.file_sub ([('ld64','')],
			       self.builddir () + '/Makefile')

	def package (self):
		# naive tarball packages for now
		self.system ('''
tar -C %(install_root)s/usr/ -zcf %(gub_uploads)s/%(gub_name)s .
''')



#class Gcc (cross.Gcc):
class Gcc (framework.Gcc):
	def patch (self):
		self.file_sub ([('/usr/bin/libtool', '%(tooldir)s/bin/%(target_architecture)s-libtool')],
			       '%(srcdir)s/gcc/config/darwin.h')

	def install (self):
		gub.Cross_package.install (self)
		self.system ('''
(cd %(tooldir)s/lib && rm -f libgcc_s.dylib && ln -s libgcc_s.1.dylib libgcc_s.dylib)
''')


class Rewirer (context.Os_context_wrapper):
	def __init__ (self, settings):
		context.Os_context_wrapper.__init__ (self,settings)
		self.ignore_libs = None
		
	def rewire_mach_o_object (self, name):
		lib_str = self.read_pipe ("%(tooldir)s/bin/%(target_architecture)s-otool -L %(name)s", locals(), ignore_error=True)


		##
		## this is gory: for some reason, we get the
		## libgcc paths along.
		## we need to relocate those, to make enough room
		## for the new paths.
		## 
		tooldir_lib = self.expand ('%(tooldir)s/')
		
		changes = ''
		for l in lib_str.split ('\n'):
			m = re.search ("\s+(/usr/lib/.*|%s.*) \(.*\)" % tooldir_lib, l)
			if not m:
				continue
			libpath = m.group (1)
			if self.ignore_libs.has_key (libpath):
				continue
			
			newpath = re.sub ('/usr/lib/', '@executable_path/../lib/', libpath); 
			newpath = re.sub (tooldir_lib, '@executable_path/../', newpath); 
			changes += (' -change %s %s ' % (libpath, newpath))
			
		if changes:
			
			self.system ("%(tooldir)s/bin/%(target_architecture)s-install_name_tool %(changes)s %(name)s ",
				     locals())

	def rewire_binary_dir (self, dir):
		if not os.path.isdir (dir):
			return
		(root, dirs, files) = os.walk (dir).next ()
		files = [os.path.join (root, f) for f in files]
		
		for f in files:
			if os.path.isfile (f):
				self.rewire_mach_o_object(f)
		
	def get_ignore_libs (self):
		str = self.read_pipe ('tar tfz %(gub_uploads)s/darwin-sdk-0.0-1.darwin.gub')
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

		
def get_packages (settings):
	packages = [
		Odcctools (settings).with (version='20051122', mirror=download.opendarwin, format='bz2'),		
#		Gcc (settings).with (version='4.0.2', mirror = download.gcc, format='bz2'),
		Gcc (settings).with (version='3.4.5', mirror = download.gcc, format='bz2',
				     depends=['odcctools']),
		]


	return packages
