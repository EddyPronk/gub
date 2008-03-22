from gub import mirrors
from gub import toolsbuild
from gub import targetbuild

class Glib (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)


        ## 2.12.4 : see bug  http://bugzilla.gnome.org/show_bug.cgi?id=362918
    source = mirrors.with_template (name='glib', #version='2.12.4',   mirror=mirrors.gnome_216,
                                    version='2.16.1',
                                    mirror=mirrors.gnome_222,
                                    format='bz2')

    def get_build_dependencies (self):
        return ['gettext-devel', 'libtool']

    def get_dependency_dict (self):
        d = targetbuild.TargetBuild.get_dependency_dict (self)
        d[''].append ('gettext')
        return d
    
    def config_cache_overrides (self, str):
        return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    def configure (self):
        targetbuild.TargetBuild.configure (self)

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias',
                     ignore_errors=True)
        
class Glib__darwin (Glib):
    def configure (self):
        Glib.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')
        
class Glib__mingw (Glib):
    def get_dependency_dict (self):
        d = Glib.get_dependency_dict (self)
        d[''].append ('libiconv')
        return d
    
    def get_build_dependencies (self):
        return Glib.get_build_dependencies (self) + ['libiconv-devel']

class Glib__freebsd (Glib):
    def get_dependency_dict (self):
        d = Glib.get_dependency_dict (self)
        d[''].append ('libiconv')
        return d
    
    def get_build_dependencies (self):
        return Glib.get_build_dependencies (self) + ['libiconv-devel']
    
    def configure_command (self):
        return Glib.configure_command (self) + ' --disable-threads'
        
gnome_2183 ='http://ftp.gnome.org/pub/GNOME/platform/2.18/2.18.3/sources/%(name)s-%(ball_version)s.tar.%(format)s'

gnome_2195 = 'http://ftp.gnome.org/pub/GNOME/platform/2.19/2.19.5/sources/%(name)s-%(ball_version)s.tar.%(format)s'

class Glib__freebsd__64 (Glib__freebsd):
    def __init__ (self, settings, source):
        Glib__freebsd.__init__ (self, settings, source)
    source = mirrors.with_template (name='glib', version='2.12.12', mirror=gnome_2183,
                   format='bz2')
    def patch (self):
        self.apply_patch ('glib-2.12.12-disable-threads.patch')
    def configure_command (self):
        return Glib.configure_command (self) + ' --disable-threads --disable-timeloop'

class Glib__tools (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='glib', version='2.10.3',
                   mirror=mirrors.gnome_214,
                   format='bz2')

    def install (self):
        toolsbuild.ToolsBuild.install (self)
        self.system ('rm %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/lib/charset.alias',
                         ignore_errors=True)

    def get_build_dependencies (self):
        return ['gettext-devel', 'libtool']            
