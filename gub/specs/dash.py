from gub import tools

class Dash__tools (tools.AutoBuild):
    source = 'http://gondor.apana.org.au/~herbert/dash/files/dash-0.5.5.1.tar.gz'
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                # dash takes --enable-static to mean: --disable-shared
                .replace ('--enable-static', ''))
    def wrap_executables (self):
        pass
