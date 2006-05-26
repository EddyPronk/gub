from toolpackage import Tool_package

class Icoutils (Tool_package):
    def __init__ (self, settings):
        Tool_package.__init__ (self, settings)
        self.with (version='0.26.0',
             mirror='http://savannah.nongnu.org/download/icoutils/icoutils-%(version)s.tar.gz',
             builddeps=['libpng']),
