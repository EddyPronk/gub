import re
import sys
#
from gub import context
from gub import build
from gub import target

# WIP of python2.5 with 2.5 X-compile patches.
class Python (target.AutoBuild):
    source = 'http://python.org/ftp/python/2.5/Python-2.5.tar.bz2'

    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        
        ## don't from gub import settings from build system.
	self.BASECFLAGS=''

    def configure_command (self):
        return 'ac_cv_printf_zd_format=yes ' + target.AutoBuild.configure_command (self)

    def patch (self):
        self.apply_patch ('python-2.5.patch')

        self.file_sub ([(r"'/usr/include'",
                         r"'%(system_prefix)s/include'")],
                       "%(srcdir)s/setup.py", must_succeed=True)
                        
    def get_subpackage_names (self):
        return ['doc', 'devel', 'runtime', '']

    def get_build_dependencies (self):
        return ['expat-devel', 'zlib-devel', 'tools::python2.5']

    def get_dependency_dict (self):
        return { '': ['expat', 'python-runtime', 'zlib'],
                 'devel' : ['libtool', 'python-devel'],
                 'runtime': [], }

    def force_autoupdate (self):
        return True

    def compile_command (self):
        ##
        ## UGH.: darwin Python vs python (case insensitive FS)
        c = target.AutoBuild.compile_command (self)
        c += ' BUILDPYTHON=python-bin '
        return c

    def install_command (self):
        ##
        ## UGH.: darwin Python vs python (case insensitive FS)
        c = target.AutoBuild.install_command (self)
        c += ' BUILDPYTHON=python-bin '
        return c

    # FIXME: c&p linux.py:install ()
    def install (self):
        target.AutoBuild.install (self)
        cfg = open (self.expand ('%(sourcefiledir)s/python-config.py.in')).read ()
        cfg = re.sub ('@PYTHON_VERSION@', self.expand ('%(version)s'), cfg)
        cfg = re.sub ('@PREFIX@', self.expand ('%(system_prefix)s/'), cfg)
        cfg = re.sub ('@PYTHON_FOR_BUILD@', sys.executable, cfg)
        self.dump (cfg, '%(install_prefix)s/cross/bin/python-config',
                   expand_string=False)
        self.system ('chmod +x %(install_prefix)s/cross/bin/python-config')


    ### Ugh.
    @context.subst_method
    def python_version (self):
        return '.'.join (self.ball_version.split ('.')[0:2])

class Python__mingw (Python):
    def __init__ (self, settings, source):
        Python.__init__ (self, settings, source)
        self.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_prefix)s/include' % self.settings.__dict__

    # FIXME: first is cross compile + mingw patch, backported to
    # 2.4.2 and combined in one patch; move to cross-Python?
    def patch (self):
        Python.patch (self)
        if 0:
            self.apply_patch ('python-2.4.2-winsock2.patch')
        self.apply_patch ('python-2.4.2-setup.py-selectmodule.patch')
    def compile (self):
        Python.compile (self)

    def configure (self):
        Python.configure (self)
        self.file_sub ([('pwd pwdmodule.c', '')],
                       '%(builddir)s/Modules/Setup')
        self.file_sub ([(' Modules/pwdmodule.o ', ' ')],
                       '%(builddir)s/Makefile')
        self.system ("cp %(srcdir)s/PC/errmap.h %(builddir)s/")
        
    def config_cache_overrides (self, str):
        # Ok, I give up.  The python build system wins.  Once
        # someone manages to get -lwsock32 on the
        # sharedmodules link command line, *after*
        # timesmodule.o, this can go away.
        return re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
                       str)

    def install (self):
        Python.install (self)

        # see python.py
        raise 'FIXME'

        ## UGH.
        self.system ('''
cp %(install_prefix)s/lib/python%(python_version)s/lib-dynload/* %(install_prefix)s/bin
''')
        self.system ('''
chmod 755 %(install_prefix)s/bin/*
''')

from gub import tools
class Python__tools (tools.AutoBuild, Python):
    source = Python.source
    def get_build_dependencies (self):
        return ['autoconf', 'libtool']
    def force_autoupdate (self):
        return True
    def install (self):
        tools.AutoBuild.install (self)
    def wrap_executables (self):
        pass
