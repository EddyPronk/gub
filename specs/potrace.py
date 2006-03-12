from toolpackage import Tool_package

class Potrace (Tool_package):
	def __init__ (self, settings):
		Tool_package.__init__ (self, settings)
		self.with (mirror="http://potrace.sourceforge.net/download/potrace-%(version)s.tar.gz",
			   version="1.7"),
