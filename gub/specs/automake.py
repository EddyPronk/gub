from gub import tools

class Automake__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/automake/automake-1.10.1.tar.gz'
    def _get_build_dependencies (self):
        return ['autoconf']
    def configure_variables (self):
	return (tools.AutoBuild.configure_variables (self)
                + ' AUTOM4TE=%(tools_prefix)s/bin/autom4te'
		+ ' autom4te_perllibdir=%(tools_prefix)s/share/autoconf'
		+ ' AC_MACRODIR=%(tools_prefix)s/share/autoconf'
		+ ' M4PATH=%(tools_prefix)s/share/autoconf'
		+ ' AUTOM4TE_CFG=%(tools_prefix)s/share/autoconf/autom4te.cfg')
