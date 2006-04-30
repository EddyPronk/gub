from toolpackage import Tool_package

class Mftrace (Tool_package):
    def __init__ (self, settings):
        Tool_package.__init__ (self, settings)
        self.with (version='1.1.19',
             mirror="http://www.xs4all.nl/~hanwen/mftrace/mftrace-1.1.19.tar.gz")
