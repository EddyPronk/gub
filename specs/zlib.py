import download
import targetpackage
import gub

class Zlib (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
	self.with (version='1.2.2',
                   mirror='http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.2.tar.gz')
        
    def patch (self):
        targetpackage.TargetBuildSpec.patch (self)

        open (self.expand ('%(license_file)s'), 'w').write (r'''

   Copyright (C) 1995-2004 Jean-loup Gailly and Mark Adler

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will the authors be held liable for any damages
  arising from the use of this software.

  Permission is granted to anyone to use this software for any purpose,
  including commercial applications, and to alter it and redistribute it
  freely, subject to the following restrictions:

  1. The origin of this software must not be misrepresented; you must not
     claim that you wrote the original software. If you use this software
     in a product, an acknowledgment in the product documentation would be
     appreciated but is not required.
  2. Altered source versions must be plainly marked as such, and must not be
     misrepresented as being the original software.
  3. This notice may not be removed or altered from any source distribution.

  Jean-loup Gailly        Mark Adler
  jloup@gzip.org          madler@alumni.caltech.edu
  
''')
        
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/zlib-1.2.2-windows.patch')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def compile_command (self):
        return targetpackage.TargetBuildSpec.compile_command (self) + ' ARFLAGS=r '
    
    def configure_command (self):
        zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.2'

        ### UGH.
        if self.settings.platform.startswith ('mingw'):
            zlib_is_broken = 'target=mingw'

        ## doesn't use autoconf configure.
        return zlib_is_broken + ' %(srcdir)s/configure --shared '

    def install_command (self):
        return targetpackage.TargetBuildSpec.broken_install_command (self)



class Zlib__mingw (Zlib):
    def patch (self):
        Zlib.patch (self)
        self.file_sub ([("='/bin/true'", "='true'"),
                        ('mgwz','libz'),
                        ],
                       '%(srcdir)s/configure')

class Zlib__darwin (gub.NullBuildSpec):
    def __init__ (self, settings):
        gub.NullBuildSpec.__init__ (self, settings)
        self.version = (lambda: '1.2.3')
        self.has_source = False

    def srcdir (self):
        return '%(allsrcdir)s/zlib-darwin'

    def package (self):
        gub.BuildSpec.package (self)
