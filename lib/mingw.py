import os
import re

import download
import gub
import cross

class Gcc (cross.Gcc):
    def patch (self):
        for f in ['%(srcdir)s/gcc/config/i386/mingw32.h',
                  '%(srcdir)s/gcc/config/i386/t-mingw32']:
            self.file_sub ([('/mingw/include','/usr/include'),
                            ('/mingw/lib','/usr/lib'),
                            ], f)

# UGH: MI
class Mingw_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    def install (self):
        self.system ('''
mkdir -p %(install_root)s/usr/share
tar -C %(srcdir)s/ -cf - . | tar -C %(install_root)s/usr -xf -
mv %(install_root)s/usr/doc %(install_root)s/share
''', locals ())

class Cygcheck (gub.BinarySpec):
    "Only need the cygcheck.exe binary."
    def __init__ (self, settings):
        gub.BinarySpec.__init__ (self, settings)
        self.with (version='1.5.18-1', mirror=download.cygwin_bin, format='bz2')
        
    def untar (self):
        gub.BinarySpec.untar (self)

        file = self.expand ('%(srcdir)s/usr/bin/cygcheck.exe')
        cygcheck = open (file).read ()
        self.system ('rm -rf %(srcdir)s/')
        self.system ('mkdir -p %(srcdir)s/usr/bin/')
        open (file, 'w').write (cygcheck)

    def basename (self):
        f = gub.BinarySpec.basename (self)
        f = re.sub ('-1$', '', f)
        return f


# UGH: MI
class W32api (gub.BinarySpec, gub.SdkBuildSpec):
    def untar (self):
        gub.BinarySpec.untar (self)
        self.system ('''
cd  %(srcdir)s/ && mkdir usr && mv include lib usr/
''')

def get_cross_packages (settings):
    return [cross.Binutils (settings).with (version='2.16.1',
                                            mirror=download.gnu,
                                            format='bz2'),
            Gcc (settings).with (version='4.1.1',
                                 mirror=download.gcc_41),
            Mingw_runtime (settings).with (version='3.9',
                                           strip_components=0,
                                           mirror=download.mingw),
            W32api (settings).with (version='3.6',
                                    strip_components=0,
                                    mirror=download.mingw)
            ]

def change_target_package (p):
    cross.change_target_package (p)

    gub.change_target_dict (p,
                    {
            'DLLTOOL': '%(tool_prefix)sdlltool',
            'DLLWRAP': '%(tool_prefix)sdllwrap',
            })
