import repository
import targetpackage

class Hello (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads,
                                          url='http://lilypond.org/download/gub-sources/hello-1.0.tar.gz',
                                          version='1.0',
                                          strip_components=True))

Hello__arm = Hello
