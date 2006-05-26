import download
import toolpackage
import targetpackage

class Glib (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='2.10.1',
		   mirror='ftp://ftp.gnome.org/Public/GNOME/sources/glib/2.10/%(name)s-%(ball_version)s.tar.%(format)s',
		   format='bz2',
		   depends=['gettext', 'libiconv', 'libtool'])
	
    def config_cache_overrides (self, str):
        return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    def configure (self):
        targetpackage.Target_package.configure (self)
        # # FIXME: libtool too old for cross compile
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


class Glib__local (toolpackage.ToolBuildSpecification):
   def __init__ (self, settings):
       toolpackage.ToolBuildSpecification.__init__ (self, settings)
       self.with (version='2.10.1',
                   mirror='ftp://ftp.gnome.org/Public/GNOME/sources/glib/2.10/%(name)s-%(ball_version)s.tar.%(format)s',
                   format='bz2',
                   depends=['gettext', 'libtool'])
   def install (self):
            toolpackage.ToolBuildSpecification.install(self)
            self.system ('rm %(install_root)s/usr/lib/charset.alias',
              ignore_error=True)



