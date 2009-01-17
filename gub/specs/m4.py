from gub import tools

class M4__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/m4/m4-1.4.12.tar.gz'
    def wrap_executables (self):
        # no dynamic executables [other than /lib:libc]
        return
