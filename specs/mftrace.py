from toolpackage import ToolBuildSpec

class Mftrace (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version='1.2.4',
                   mirror="http://www.xs4all.nl/~hanwen/mftrace/mftrace-%(version)s.tar.gz")

    def license_file (self):
        # FIXME: not a license file, build fix.
        return '%(srcdir)s/README.txt'
		   