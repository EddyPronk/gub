from toolpackage import ToolBuildSpec

class Mftrace (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version='1.2.3',
                   mirror="http://www.xs4all.nl/~hanwen/mftrace/mftrace-1.2.3.tar.gz")
