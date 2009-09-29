from gub import tools

class Scons__tools (tools.PythonBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/scons/scons-0.98.4.tar.gz'
    license_files = ['%(srcdir)s/LICENSE.txt']
