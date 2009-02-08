from gub import target

class Xulrunner (target.AutoBuild):
    source = 'http://releases.mozilla.org/pub/mozilla.org/xulrunner/releases/1.9.0.3/source/xulrunner-1.9.0.3-source.tar.bz2'
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                .replace ('--config-cache', '--cache-file=%(builddir)s/config.cache'))

class Xulrunner__mingw (Xulrunner):
    def patch (self):
        self.file_sub ([('#! /bin/sh', '#! /bin/bash\nenable -n pwd')],
                       '%(srcdir)s/configure')
    def _get_build_dependencies (self):
        return ['mingw-pwd']
