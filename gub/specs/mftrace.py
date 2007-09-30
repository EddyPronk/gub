from gub import toolsbuild
class Mftrace (toolsbuild.ToolsBuild):
    def __init__ (self, settings):
        toolsbuild.ToolsBuild.__init__ (self, settings)
        self.with_template (version='1.2.14',
                   mirror="http://lilypond.org/download/sources/mftrace/mftrace-%(version)s.tar.gz")

