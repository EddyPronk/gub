from toolpackage import ToolBuildSpecification

class Potrace (ToolBuildSpecification):
    def __init__ (self, settings):
        ToolBuildSpecification.__init__ (self, settings)
        self.with (mirror="http://potrace.sourceforge.net/download/potrace-%(version)s.tar.gz",
             version="1.7"),
