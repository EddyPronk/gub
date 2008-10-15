from gub import toolsbuild

class Distcc (toolsbuild.ToolsBuild):
    def patch (self):
        self.apply_patch ('distcc-substitute.patch')
