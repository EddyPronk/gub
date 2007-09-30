from gub import toolsbuild

class Distcc (toolsbuild.ToolsBuild):
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/distcc-substitute.patch
''')
    def __init__ (self,s):
        toolsbuild.ToolsBuild.__init__ (self,s)
        self.with_template (version='2.18.3',
             mirror="http://distcc.samba.org/ftp/distcc/distcc-%(version)s.tar.bz2"),
