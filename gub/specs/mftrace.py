from gub import toolpackage
class Mftrace (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (version='1.2.14',
                   mirror="http://lilypond.org/download/sources/mftrace/mftrace-%(version)s.tar.gz")

