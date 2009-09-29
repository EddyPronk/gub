from gub import tools

class Libapr_util__tools (tools.AutoBuild):
    source = 'http://apache.cs.uu.nl/dist/apr/apr-util-1.3.9.tar.gz'
    dependencies = [
            'libapr-devel',
            ]
    configure_flags = (tools.AutoBuild.configure_flags
                + ' --with-apr=%(system_prefix)s'
                )

