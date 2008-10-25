from gub import context
from gub import misc
from gub import targetbuild

class Libxml2 (targetbuild.TargetBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.18/2.18.1/sources/libxml2-2.6.27.tar.gz'
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + misc.join_lines ('''
--without-python
'''))
    @context.subst_method
    def config_script (self):
        return 'xml2-config'
