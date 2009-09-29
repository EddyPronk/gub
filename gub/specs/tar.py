#
from gub import repository
from gub import tools

class Tar__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/tar/tar-1.20.tar.gz'
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        if isinstance (self.source, repository.TarBall):
            self.source._unpack = self.source._unpack_promise_well_behaved
