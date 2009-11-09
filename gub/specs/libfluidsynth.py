from gub import target

class Libfluidsynth (target.AutoBuild):
    source = 'http://download.savannah.gnu.org/releases/fluid/fluidsynth-1.1.0.tar.gz'
    dependencies = [
        'glib-devel',
        ]

class Libfluidsynth__mingw (Libfluidsynth):
    def patch (self):
        Libfluidsynth.patch (self)
        self.system ('''
cp %(sourcefiledir)s/mingw-headers/wine-windef.h %(srcdir)s/src
cp %(sourcefiledir)s/mingw-headers/dsound.h %(srcdir)s/src
''')
        self.dump ('''
#include "wine-windef.h"
''',
                   '%(srcdir)s/src/config.h.in',
                   mode='a')
