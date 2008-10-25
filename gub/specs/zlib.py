from gub import targetbuild
from gub import build
from gub import mirrors
from gub import toolsbuild

class Zlib (targetbuild.TargetBuild):
    source = mirrors.with_template (name='zlib', version='1.2.3',
                   mirror='http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.3.tar.gz')
    def get_build_dependencies (self):
        return ['tools::autoconf']
    def patch (self):
        targetbuild.TargetBuild.patch (self)
        self.apply_patch ('zlib-1.2.3.patch')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def compile_command (self):
        return targetbuild.TargetBuild.compile_command (self) + ' ARFLAGS=r '
    def configure_command (self):
        import re
        stripped_platform = self.settings.expand ('%(platform)s')
        stripped_platform = re.sub ('-.*', '', stripped_platform)
        stripped_platform = stripped_platform.replace ('darwin', 'Darwin')
        
        zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.3 target=' + stripped_platform
        ## doesn't use autoconf configure.
        return zlib_is_broken + ' %(srcdir)s/configure --shared '
    def install_command (self):
        return targetbuild.TargetBuild.broken_install_command (self)
    def license_files (self):
        return ['%(sourcefiledir)s/zlib.license']

class Zlib__mingw (Zlib):
    def patch (self):
        Zlib.patch (self)
        self.file_sub ([("='/bin/true'", "='true'"),
                        ('mgwz','libz'),
                        ],
                       '%(srcdir)s/configure')
    def configure_command (self):
        zlib_is_broken = 'target=mingw'
        return zlib_is_broken + ' %(srcdir)s/configure --shared '

class Zlib__tools (toolsbuild.ToolsBuild, Zlib):
    source = Zlib.source
    def get_build_dependencies (self):
        return ['autoconf']
    def patch (self):
        toolsbuild.ToolsBuild.patch (self)
        self.apply_patch ('zlib-1.2.3.patch')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def install_command (self):
        return toolsbuild.ToolsBuild.broken_install_command (self)
    def install (self):
        toolsbuild.ToolsBuild.install (self)
        self.system ('cd %(install_root)s && mkdir -p ./%(tools_prefix)s && cp -av usr/* ./%(tools_prefix)s && rm -rf usr')
    def configure_command (self):
        return Zlib.configure_command (self)
    def license_files (self):
        return ['%(sourcefiledir)s/zlib.license']
