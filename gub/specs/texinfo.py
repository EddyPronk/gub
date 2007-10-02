from gub import toolsbuild

class Texinfo (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='texinfo', version="4.8",
                   mirror=mirrors.gnu, format="bz2")
    patches = 'texinfo-4.8.patch'
