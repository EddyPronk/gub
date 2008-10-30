from gub import tools

class Distcc (tools.AutoBuild):
    def patch (self):
        self.apply_patch ('distcc-substitute.patch')
