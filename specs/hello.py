import download
import repository
import targetpackage

class Hello (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.NewTarBall (self.settings.downloads,
                                             mirror=download.lilypondorg,
                                             name=self.name (),
                                             ball_version='1.0'))
