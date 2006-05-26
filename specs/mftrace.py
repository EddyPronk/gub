from toolpackage import ToolBuildSpecification

class Mftrace (ToolBuildSpecification):
    def __init__ (self, settings):
        ToolBuildSpecification.__init__ (self, settings)
        self.with (version='1.2.3',
                   mirror="http://www.xs4all.nl/~hanwen/mftrace/mftrace-1.2.3.tar.gz")
