from toolpackage import Tool_package

class Mftrace (Tool_package):
    def __init__ (self, settings):
        Tool_package.__init__ (self, settings)
        self.with (version='1.2.3',
                   mirror="http://www.xs4all.nl/~hanwen/mftrace/mftrace-1.2.3.tar.gz")
