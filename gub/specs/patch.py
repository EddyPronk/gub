from gub import tools

class Patch__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/patch/patch-2.5.4.tar.gz'
    def configure_variables (self):
        return ''
    def install_command (self):
        return self.broken_install_command ()
    def wrap_executables (self):
        return
