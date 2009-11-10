from gub import target

class Fluidsynth (target.AutoBuild):
    source = 'http://download.savannah.gnu.org/releases/fluid/fluidsynth-1.1.0.tar.gz'
    dependencies = [
        'glib-devel',
        'portaudio',
        ]
    configure_flags = (target.AutoBuild.configure_flags
                       + ' --with-pic'
                       + ' --disable-libsndfile-support'
                       + ' --disable-pulse-support'
                       + ' --disable-alsa-support'
                       + ' --enable-portaudio-support'
                       + ' --disable-oss-support'
                       + ' --disable-midishare'
                       + ' --disable-jack-support'
                       + ' --disable-coreaudio'
                       + ' --disable-coremidi'
                       + ' --disable-lash'
                       + ' --disable-ladcca'
                       )

class Fluidsynth__mingw (Fluidsynth):
    patches = [
#        'fluidsynth-mingw-static-libs.patch',
#        'fluidsynth-mingw-static-libs-configure.patch',
        'fluidsynth-mingw-static-libs-src-makefile.patch',
    ]
    # The link command includes libraries that we only have in
    # static form: libstdc++.a libuuid.a and libdsound.a.
    # It seems only libdsound.a is needed, but our dll does
    # not build with this static lib?
    '''
    Creating library file: .libs/libfluidsynth.dll.a
.libs/libfluidsynth_la-fluid_dsound.o:fluid_dsound.c:(.text+0x42a): undefined reference to `_DirectSoundEnumerateA@8'
.libs/libfluidsynth_la-fluid_dsound.o:fluid_dsound.c:(.text+0x6df): undefined reference to `_DirectSoundCreate@12'
.libs/libfluidsynth_la-fluid_dsound.o:fluid_dsound.c:(.text+0x732): undefined reference to `_DirectSoundEnumerateA@8'
collect2: ld returned 1 exit status
'''
    xconfigure_flags = (Fluidsynth.configure_flags
                       .replace ('--with-pic', '--without-pic')
                       .replace ('--enable-shared', '--disable-shared')
                       .replace ('--disable-static', '--enable-static')
                       )
    def patch (self):
        Fluidsynth.patch (self)
        self.system ('''
cp %(sourcefiledir)s/mingw-headers/wine-windef.h %(srcdir)s/src
cp %(sourcefiledir)s/mingw-headers/dsound.h %(srcdir)s/src
''')
    def autoupdate (self):
        Fluidsynth.autoupdate (self)
        self.dump ('''
#include "wine-windef.h"
''',
                   '%(srcdir)s/src/config.h.in',
                   mode='a')
