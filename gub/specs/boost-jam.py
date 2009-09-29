from gub import misc
from gub import tools

class Boost_jam (tools.ShBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost-jam-3.1.11.tgz'
    make_flags = ' gcc --symbols'
    install_command = misc.join_lines ('''
install -d %(install_prefix)s/bin
&& install -m755 bin.*/bjam  %(install_prefix)s/bin
''')
