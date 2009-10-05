#
from gub import misc
from gub import repository
from gub import target
from gub import tools

class Libtool (target.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/libtool/libtool-2.2.6a.tar.gz'
    #source = 'git://git.sv.gnu.org/libtool.git?branch=master&revision=77e114998457cb6170ad84b360cb5b9be90f2191'
    dependencies = ['tools::libtool']
    configure_variables = (target.AutoBuild.configure_variables
                           .replace ('SHELL=', 'CONFIG_SHELL='))
    if 'stat' in misc.librestrict ():
        configure_command = ('CONFIG_SHELL=%(tools_prefix)s/bin/bash '
                             'LD_PRELOAD=%(tools_prefix)s/lib/librestrict-open.so '
                             + target.AutoBuild.configure_command
                             .replace ('/sh', '/bash')
                             .replace ('SHELL=', 'CONFIG_SHELL='))
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        # repository patched in method.
        def version_from_VERSION (self):
            return '2.2.7'
        if isinstance (source, repository.Git):
            source.version = misc.bind_method (version_from_VERSION, source)
            source._version = '2.2.7'
        Libtool.set_sover (self)
        if isinstance (self.source, repository.Git):
            self.dependencies += ['tools::libtool', 'tools::automake']
    def autoupdate (self):
        # automagic works, but takes forever
        if isinstance (self.source, repository.Git):
            self.system ('cd %(srcdir)s && reconfdirs=". libltdl" ./bootstrap')
#        target.AutoBuild.autoupdate (self)
    @staticmethod
    def set_sover (self):
        # FIXME: how to automate this?
        self.so_version = '3'
        if self.source._version in ('2.2.4', '2.2.6.a', '2.2.7'):
            self.so_version = '7'
    subpackage_names = ['devel', 'doc', 'runtime', '']
    def get_subpackage_definitions (self):
        d = target.AutoBuild.get_subpackage_definitions (self)
        d['devel'].append (self.settings.prefix_dir + '/bin/libtool*')
        d['devel'].append (self.settings.prefix_dir + '/share/libltdl')
        return d
    def update_libtool (self):
        pass
    config_cache_overrides = (target.AutoBuild.config_cache_overrides + '''
ac_cv_prog_F77=${ac_cv_prog_F77=no}
ac_cv_prog_FC=${ac_cv_prog_FC=no}
ac_cv_prog_GCJ=${ac_cv_prog_GCJ=no}
''')

class Libtool__darwin (Libtool):
    def install (self):
        Libtool.install (self)
        ## necessary for programs that load dynamic modules.
        self.dump ("prependdir DYLD_LIBRARY_PATH=$INSTALLER_PREFIX/lib",
                   '%(install_prefix)s/etc/relocate/libtool.reloc')

class Libtool__tools (tools.AutoBuild, Libtool):
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        Libtool.set_sover (self)
    update_libtool = tools.AutoBuild.nop
    def install (self):
        tools.AutoBuild.install (self)
        # FIXME: urg.  Are we doing something wrong?  Why does libtool
        # ignore [have /usr prevail over] --prefix ?
        self.file_sub ([(' (/usr/lib/*[" ])', r' %(system_prefix)s/lib \1'),
                        ('((-L| )/usr/lib/../lib/* )', r'\2%(system_prefix)s/lib \1')],
                       '%(install_prefix)s/bin/libtool')
    if 'stat' in misc.librestrict ():
        configure_command = ('SHELL=/bin/bash CONFIG_SHELL=/bin/bash '
                             + tools.AutoBuild.configure_command)
