import download
import toolpackage
import targetpackage

class Glib (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='2.10.1',
		   mirror='ftp://ftp.gnome.org/Public/GNOME/sources/glib/2.10/%(name)s-%(ball_version)s.tar.%(format)s',
		   format='bz2')

    def get_build_dependencies (self):
        return ['gettext-devel', 'libtool']

    def get_dependency_dict (self):
        d = targetpackage.Target_package.get_dependency_dict ()
        d[''].append ('gettext')
        return d
    
    def config_cache_overrides (self, str):
        return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    def configure (self):
        targetpackage.Target_package.configure (self)

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        
    def install (self):
        targetpackage.Target_package.install (self)
        self.system ('rm %(install_root)s/usr/lib/charset.alias',
              ignore_error=True)
        
class Glib__darwin (Glib):
    def configure (self):
        Glib.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')
        
class Glib__freebsd (Glib):
    def get_dependency_dict (self):
        d = Gettext.get_dependency_dict (self)
        d[''].append ('libiconv')
        return d
    
    def get_build_dependencies (self):
        return Glib.get_build_dependencies (self) + ['libiconv-devel']
    
class Glib__local (toolpackage.Tool_package):
   def __init__ (self, settings):
       toolpackage.Tool_package.__init__ (self, settings)
       self.with (version='2.10.1',
                  mirror='ftp://ftp.gnome.org/Public/GNOME/sources/glib/2.10/%(name)s-%(ball_version)s.tar.%(format)s',
                  format='bz2')

   def install (self):
            toolpackage.Tool_package.install(self)
            self.system ('rm %(install_root)s/usr/lib/charset.alias',
              ignore_error=True)



