from toolpackage import ToolBuildSpec

class Mftrace (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (version='1.2.14',
                   mirror="http://lilypond.org/download/sources/mftrace/mftrace-%(version)s.tar.gz")

