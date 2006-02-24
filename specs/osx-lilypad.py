import download
import gub
import targetpackage

class OSX_Lilypad (gub.Null_package):
	def __init__ (self, settings):
		targetpackage.Target_package.__init__ (self, settings)
		self.with.with (version="0.0", mirror=download.hw, depends=[])

