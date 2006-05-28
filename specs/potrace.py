from toolpackage import ToolBuildSpec

class Potrace (ToolBuildSpec):
    def __init__ (self, settings):
        ToolBuildSpec.__init__ (self, settings)
        self.with (mirror="http://potrace.sourceforge.net/download/potrace-%(version)s.tar.gz",
             version="1.7"),
