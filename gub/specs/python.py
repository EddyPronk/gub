import glob
import re
import sys
#
from gub import mirrors
from gub import build
from gub import targetbuild
from gub import context

class Python (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_template (version='2.4.2',
                   mirror=mirrors.python,
                   format='bz2')

        ## don't from gub import settings from build system.
	self.BASECFLAGS = ''
        self.CROSS_ROOT = '%(targetdir)s'

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

    def patch (self):
        targetbuild.TargetBuild.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-1.patch')
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-configure.in-posix.patch')
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-configure.in-sysname.patch')
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-configure.in-sysrelease.patch')
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-2.4.2-setup.py-import.patch')
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-2.4.2-setup.py-cross_root.patch')
        self.file_sub ([('@CC@', '@CC@ -I$(shell pwd)')],
                        '%(srcdir)s/Makefile.pre.in')

    def configure (self):
        self.system ('''cd %(srcdir)s && autoconf''')
        self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
        targetbuild.TargetBuild.configure (self)

    def compile_command (self):
        ##
        ## UGH.: darwin Python vs python (case insensitive FS)
        c = targetbuild.TargetBuild.compile_command (self)
        c += ' BUILDPYTHON=python-bin '
        return c

    def install_command (self):
        ##
        ## UGH.: darwin Python vs python (case insensitive FS)
        c = targetbuild.TargetBuild.install_command (self)
        c += ' BUILDPYTHON=python-bin '
        return c

    # FIXME: c&p linux.py:install ()
    def install (self):
        targetbuild.TargetBuild.install (self)
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

class Python__mingw_binary (build.BinaryBuild):
    def __init__ (self, settings):
        build.BinaryBuild.__init__ (self, settings)
        self.with_template (mirror="http://lilypond.org/~hanwen/python-2.4.2-windows.tar.gz",
                   version='2.4.2')

    def python_version (self):
        return '2.4'

    def install (self):
        build.BinaryBuild.install (self)

        self.system ("cd %(install_root)s/ && mkdir usr && mv Python24/include  usr/ ")
        self.system ("cd %(install_root)s/ && mkdir -p usr/bin/ && mv Python24/* usr/bin/ ")
        self.system ("rmdir %(install_root)s/Python24/")


class Python__mingw_cross (Python):
    def __init__ (self, settings):
        Python.__init__ (self, settings)
        self.target_gcc_flags = '-DMS_WINDOWS -DPy_WIN_WIDE_FILENAMES -I%(system_prefix)s/include' % self.settings.__dict__

    # FIXME: first is cross compile + mingw patch, backported to
    # 2.4.2 and combined in one patch; move to cross-Python?
    def patch (self):
        Python.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/python-2.4.2-winsock2.patch
''')
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/python-2.4.2-setup.py-selectmodule.patch')

        ## to make subprocess.py work.
        self.file_sub ([
                ("import fcntl", ""),
                ], "%(srcdir)s/Lib/subprocess.py",
               must_succeed=True)

    def config_cache_overrides (self, str):
        # Ok, I give up.  The python build system wins.  Once
        # someone manages to get -lwsock32 on the
        # sharedmodules link command line, *after*
        # timesmodule.o, this can go away.
        return re.sub ('ac_cv_func_select=yes', 'ac_cv_func_select=no',
               str)

    def install (self):
        Python.install (self)
        for i in glob.glob ('%(install_prefix)s/lib/python%(python_version)s/lib-dynload/*.so*' \
                  % self.get_substitution_dict ()):
            dll = re.sub ('\.so*', '.dll', i)
            self.system ('mv %(i)s %(dll)s', locals ())

        ## UGH.
        self.system ('''
cp %(install_prefix)s/lib/python%(python_version)s/lib-dynload/* %(install_prefix)s/bin
''')
        self.system ('''
chmod 755 %(install_prefix)s/bin/*
''')

class Python__mingw (Python__mingw_cross):
    pass


from gub import toolsbuild
class Python__tools (toolsbuild.ToolsBuild, Python):
    def __init__ (self, settings):
        toolsbuild.ToolsBuild.__init__ (self, settings)
        self.with_template (version='2.4.2',
                   mirror=mirrors.python,
                   format='bz2')

    def configure (self):
        self.system ('''cd %(srcdir)s && autoconf''')
        self.system ('''cd %(srcdir)s && libtoolize --copy --force''')
        targetbuild.TargetBuild.configure (self)
    def install (self):
        toolsbuild.ToolsBuild.install (self)


    def license_file (self):
        return '%(srcdir)s/LICENSE'

    def wrap_executables (self):
        pass
