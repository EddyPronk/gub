from gub import toolsbuild

class Scons__tools (toolsbuild.PythonBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/scons/scons-0.98.4.tar.gz'
    def license_files (self):
        return ['%(srcdir)s/LICENSE.txt']
