from gub import tools

class Dash__tools (tools.AutoBuild):
    source = 'http://gondor.apana.org.au/~herbert/dash/files/dash-0.5.5.1.tar.gz'
    def patch (self):
        tools.AutoBuild.patch (self)
        self.file_sub ([('testcmd		test [[]', ''),
                        ('echocmd		echo', '')],
                       '%(srcdir)s/src/builtins.def.in',
                       must_succeed=True)
    configure_flags = (tools.AutoBuild.configure_flags
                # dash takes --enable-static to mean: --disable-shared
                .replace ('--enable-static', ''))
