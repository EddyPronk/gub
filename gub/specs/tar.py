from gub import tools

class Tar__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/tar/tar-1.20.tar.gz'
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        self.source._unpack = self.source._unpack_promise_well_behaved
    def wrap_executables (self):
        # no dynamic executables [other than /lib:libc]
        return
