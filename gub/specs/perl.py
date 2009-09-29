import re
#
from gub import misc
from gub import tools

# And this is supposed to be one of the most compiled packages?
# So why doesn't anyone fix configuring/compiling it?  Shees.
class Perl__tools (tools.AutoBuild):
    source = 'http://www.cpan.org/src/perl-5.10.0.tar.gz'
    srcdir_build_broken = True
    def patch (self):
        tools.AutoBuild.patch (self)
        self.file_sub ([('-c (/dev/null)', r'-e \1')], '%(srcdir)s/Configure')
    configure_binary = '%(autodir)s/configure.gnu'
# -Dcc=%(CC)s
# -Dprefix=%(prefix_dir)s -- BOOTSTRAP
    configure_command = misc.join_lines ('''%(configure_binary)s
 -Dprefix=%(system_prefix)s
 -Dcc='%(toolchain_prefix)sgcc %(target_gcc_flags)s'
 -Dtargetarch=%(target_architecture)s
 -Dusrinc=%(system_prefix)s/include
 -Dincpth=/
 -Dlibpth=%(system_prefix)s/lib
 -Dsitelib=%(system_prefix)s/lib/perl5/5.10.0
 -Dsitearch=%(system_prefix)s/lib/perl5/5.10.0
 -Dusedl
 -Duseshrplib
 -Dlibperl=libperl.so
 -Dcccdlflags=-fPIC
 -Dlocallibpth=/
 -Aldflags='%(rpath)s -lm -lrt -ldl'
''')
    def configure (self):
        tools.AutoBuild.configure (self)
        for i in ['%(builddir)s/makefile', '%(builddir)s/x2p/makefile']:
            # Ugh, missing some command?
            self.file_sub ([('^0$','')], i)
#    def install_command (self):
