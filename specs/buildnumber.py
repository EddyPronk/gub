import string
import os
import pickle 
import gdbm
import gub




class Build_number_db:
	def __init__ (self, dir, mode='r'):
		self.db = None
		# gdbm.open (dir + '/buildnumber.gdbm', mode)

	def key (self, package):
		return package.expand ('%(name)s-%(version)s-%(target_architecture)s')

	def set_build_number (self, package):
		package._build = self.get_build_number (package)
		
	def get_build_number (self, package):
		return 1
	
		k = self.key (package)
		if not self.db.has_key (k):
			return 1

		bn = self.db[k]

		gubname ='%(gub_uploads)s/%(name)s-%(version)s-%(bn)s.%(platform)s.gub'
		gubname = package.expand (gubname, locals ())
	
		if os.path.exists (gubname):
			return string.atoi (bn)
		else:
			return string.atoi (bn) + 1

	def write_build_number (self, pkg):
		b = pkg.build ()
		gub.log_command ("Writing build number: %s" % b)
		self.db[self.key (pkg)] = b
		
