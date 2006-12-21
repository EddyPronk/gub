from toolpackage import ToolBuildSpec

class Mftrace (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version='1.2.5',
                   mirror="http://lilypond.org/mftrace/mftrace-%(version)s.tar.gz")

