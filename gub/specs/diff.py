from gub import tools

class Diff__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/diffutils/diffutils-2.8.1.tar.gz'
    def wrap_executables (self):
        # no dynamic executables [other than /lib:libc]
        pass
