from gub import toolsbuild

class Distcc (toolsbuild.AutoBuild):
    def patch (self):
        self.apply_patch ('distcc-substitute.patch')
