from gub import target
from gub import tools

class Libgd (target.AutoBuild):
    source = 'http://www.libgd.org/releases/gd-2.0.36RC1.tar.gz'
    def _get_build_dependencies (self):
        return [
            'tools::libtool',
            'libjpeg-devel'
            ]
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --disable-xpm'
                + ' --without-xpm'
                )

class Libgd__tools (tools.AutoBuild, Libgd):
    def _get_build_dependencies (self):
        return [
            'libtool',
            'libjpeg-devel',
            ]
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' --disable-xpm'
                + ' --without-xpm'
                )
