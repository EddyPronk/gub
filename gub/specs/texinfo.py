from gub import tools

class Texinfo__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/texinfo/texinfo-4.11.tar.gz'
    def patch (self):
        # for 4.11
        self.system ('cd %(srcdir)s/build-aux && chmod +x install-sh config.sub config.guess missing')
    def _get_build_dependencies (self):
        return ['ncurses']
