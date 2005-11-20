import os
import sys
import re

def system (cmd, ignore_error = False):
	sys.stderr.write ('invoking %s\n' % cmd)
	stat = os.system (cmd)
	if stat and not ignore_error:
		sys.stderr.write ('fail\n')
		sys.exit (1)

	return 0 



class Package:
	def __init__ (self, settings):
		self.settings = settings
	
	def download (self):
		dir = self.settings.downloaddir
		if not os.path.exists (dir + '/' + self.file_name ()): 
			system ('cd %s ; wget %s ' % (dir, self.url))

	def unpack_destination (self):
		return self.settings.srcdir
	
	def basename (self):
		f = self.file_name ()
		f = re.sub ("\.tar.*", '', f)
		return f

	def name (self):
		s = self.basename()
		s = re.sub ('-?[0-9][^-]+$', '', s)
		return s
	
	def srcdir (self):
		return self.unpack_destination () + '/' + self.basename ()

	def builddir (self):
		return self.settings.builddir + '/' + self.basename ()

	def installdir (self):
		return self.settings.installdir + '/' + self.name ()

	def file_name (self):
		file = re.sub (".*/([^/]+)", '\\1', self.url)
		return file


	def done (self, stage):
		return os.path.exists ('%s/%s-%s' % (self.settings.statusdir, self.name (), stage))

	def set_done (self, stage):
		open ('%s/%s-%s' % (self.settings.statusdir, self.name(), stage), 'w').write ('')

	def configure_command (self):
		return ("%s/configure --prefix=%s "
			% (self.srcdir (), self.installdir ()))

	def configure (self):
		system ("mkdir -p %s;  cd %s && %s" % (self.builddir(),
						       self.builddir(),
						       self.configure_command ()))

	def install_command (self):
		return 'make install'
	
	def install (self):
		system ("cd %s && %s" % (self.builddir (), self.install_command ())) 

	def compile_command (self):
		return 'make'

	def compile (self):
		system ("cd %s && %s" % (self.builddir(), self.compile_command ()))

	def patch (self):
		pass
	
	def unpack (self):
		file = self.settings.downloaddir + '/' + self.file_name ()

		cmd = ""
		if re.search (".tar$", file):
			cmd = "-xf "
		elif re.search (".tar.bz2", file):
			cmd = "-jxf "
		elif re.search ('.tar.gz', file):
			cmd = '-xzf '

		cmd = "tar %s %s -C %s " % (cmd, file, self.unpack_destination ())
		system (cmd) 

	
