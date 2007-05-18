import re
import sys
#
from gub import mirrors
import glob
from gub import gubb
from gub import targetpackage

from gub import context


class Python (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        
        ## don't from gub import settings from build system.
	self.BASECFLAGS=''
        self.with_template (version='2.5',
                   mirror=mirrors.python,
                   format='bz2')

    def configure_command (self):
        return 'ac_cv_printf_zd_format=yes ' + targetpackage.TargetBuildSpec.configure_command (self)

    def patch (self):
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.5.patch')

        self.file_sub ([(r"'/usr/include'",
                         r"'%(system_root)s/usr/include'")],
                       "%(srcdir)s/setup.py", must_succeed=True)
                        
    def license_file (self):
        return '%(srcdir)s/LICENSE'

    def get_subpackage_names (self):
        return ['doc', 'devel', 'runtime', '']

    def get_build_dependencies (self):
        return ['expat-devel', 'zlib-devel']

    def get_dependency_dict (self):
        return { '': ['expat', 'python-runtime', 'zlib'],
                 'devel' : ['libtool', 'python-devel'],
                 'runtime': [], }

    def configure (self):
        self.system ('''cd %(srcdir)s && autoconf''')
        self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
        targetpackage.TargetBuildSpec.configure (self)

    def compile_command (self):
        ##
        ## UGH.: darwin Python vs python (case insensitive FS)
        c = targetpackage.TargetBuildSpec.compile_command (self)
        c += ' BUILDPYTHON=python-bin '
        return c

    def install_command (self):
        ##
        ## UGH.: darwin Python vs python (case insensitive FS)
        c = targetpackage.TargetBuildSpec.install_command (self)
        c += ' BUILDPYTHON=python-bin '
        return c

    # FIXME: c&p linux.py:install ()
    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        cfg = open (self.expand ('%(sourcefiledir)s/python-config.py.in')).read ()
        cfg = re.sub ('@PYTHON_VERSION@', self.expand ('%(version)s'), cfg)
        cfg = re.sub ('@PREFIX@', self.expand ('%(system_root)s/usr/'), cfg)
        cfg = re.sub ('@PYTHON_FOR_BUILD@', sys.executable, cfg)
        self.dump (cfg, '%(install_root)s/usr/cross/bin/python-config',
                   expand_string=False)
        self.system ('chmod +x %(install_root)s/usr/cross/bin/python-config')


    ### Ugh.
    @context.subst_method
    def python_version (self):
        return '.'.join (self.ball_version.split ('.')[0:2])

class Python__mingw (Python):
    def __init__ (self, settings):
        Python.__init__ (self, settings)
        self.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_root)s/usr/include' % self.settings.__dict__

    # FIXME: first is cross compile + mingw patch, backported to
    # 2.4.2 and combined in one patch; move to cross-Python?
    def patch (self):
        Python.patch (self)
        if 0:
            self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-winsock2.patch
''')
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-2.4.2-setup.py-selectmodule.patch')
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
        for i in glob.glob ('%(install_root)s/usr/lib/python%(python_version)s/lib-dynload/*.so*' \
                  % self.get_substitution_dict ()):
            dll = re.sub ('\.so*', '.dll', i)
            self.system ('mv %(i)s %(dll)s', locals ())

        ## UGH.
        self.system ('''
cp %(install_root)s/usr/lib/python%(python_version)s/lib-dynload/* %(install_root)s/usr/bin
''')
        self.system ('''
chmod 755 %(install_root)s/usr/bin/*
''')

from gub import toolpackage
class Python__local (toolpackage.ToolBuildSpec, Python):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (version='2.5',
                   mirror=mirrors.python,
                   format='bz2')

    def configure (self):
        self.system ('''cd %(srcdir)s && autoconf''')
        self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
        targetpackage.TargetBuildSpec.configure (self)
    def install (self):
        toolpackage.ToolBuildSpec.install (self)


    def license_file (self):
        return '%(srcdir)s/LICENSE'

    def wrap_executables (self):
        pass
