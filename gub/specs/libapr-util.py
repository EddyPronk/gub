from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Libapr_util__tools (tools.AutoBuild):
    source = 'http://apache.cs.uu.nl/dist/apr/apr-util-1.3.9.tar.gz'
    dependencies = [
            'libapr-devel',
            ]
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' --with-apr=%(system_prefix)s'
                )

