from gub import targetpackage
from gub import repository

url = 'http://www.eecs.harvard.edu/~nr/noweb/dist/noweb-2.11b.tgz'

class Noweb (targetpackage.TargetBuildSpec):
    '''A WEB-like literate-programming tool
Noweb is designed to meet the needs of literate programmers while
remaining as simple as possible.  Its primary advantages are
simplicity, extensibility, and language-independence.
'''
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url, version='2.11b'))
        self.BIN='%(install_prefix)s/bin'
        self.LIB='%(install_prefix)s/lib'
        self.MAN='%(install_prefix)s/share/man'
        self.TEXINPUTS='%(install_prefix)s/share/tex/inputs'
    def makeflags (self):
        return 'BIN=%(install_prefix)s/bin LIB=%(install_prefix)s/lib MAN=%(install_prefix)s/share/man TEXINPUTS=%(install_prefix)s/share/tex/inputs'
    def patch (self):
        self.shadow_tree ('%(srcdir)s/src', '%(builddir)s')
    def configure (self):
        pass
    def get_subpackage_names (self):
        return ['']
    def install_command (self):
        from gub import misc
        return misc.join_lines ('''
mkdir -p %(install_prefix)s/bin %(install_prefix)s/lib %(install_prefix)s/share/man/man1 %(install_prefix)s/share/tex/inputs
&& make %(makeflags)s DESTDIR=%(install_root)s install
''')
    def license_file (self):
        return '%(srcdir)s/src/COPYRIGHT'
