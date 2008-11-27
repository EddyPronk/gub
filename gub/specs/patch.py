from gub import tools

class Patch__tools (tools.AutoBuild):
#    source = 'ftp://ftp.gnu.org/pub/gnu/patch/patch-2.5.4.tar.gz'
#    source = 'ftp://alpha.gnu.org/pub/gnu/diffutils/patch-2.5.9.tar.gz'
# ugh, openoffice the ooo-build flavour needs the latest patch with
# additional [SUSE] patches to not barf on all CRLF problems.
# Taken from the Ibex: apt-get --download source patch
    source = 'http://lilypond.org/download/gub-sources/patch-2.5.9-5.tar.gz'
    def configure_variables (self):
        return ''
    def configure (self):
        tools.AutoBuild.configure (self)
        if 'freebsd' in self.settings.build_architecture:
            self.file_sub ([('^#define HAVE_SETMODE 1', '/* #undef HAVE_SETMODE */')],
                           '%(builddir)s/config.h')
    def install_command (self):
        return self.broken_install_command ()
    def wrap_executables (self):
        # no dynamic executables [other than /lib:libc]
        return
