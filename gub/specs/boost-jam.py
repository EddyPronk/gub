from gub import misc
from gub import tools

class Boost_jam (tools.ShBuild):
#    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost-jam-3.1.17.tgz'
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost-jam-3.1.11.tgz'
#    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost-jam-3.1.16.tgz'
    def compile_command (self):
        return tools.ShBuild.compile_command (self) + ' gcc --symbols'
    def install_command (self):
        return misc.join_lines ('''
install -d %(install_root)s/%(system_prefix)s/bin
&& install -m755 bin.*/bjam  %(install_root)s/%(system_prefix)s/bin
''')
