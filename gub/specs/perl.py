import re
#
from gub import misc
from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

# And this is supposed to be one of the most compiled packages?
# So why doesn't anyone fix configuring/compiling it?  Shees.
class Perl__tools (tools.AutoBuild):
    source = 'http://www.cpan.org/src/perl-5.10.0.tar.gz'
    def patch (self):
        tools.AutoBuild.patch (self)
        self.file_sub ([('-c (/dev/null)', r'-e \1')], '%(srcdir)s/Configure')
    def configure_binary (self):
        return '%(autodir)s/configure.gnu'
    def GNU_NOT_HAHA_configure_command (self):
        # Handy, a GNU configure frontend...  Not.
        command = (tools.AutoBuild.configure_command (self)
                   .replace ('--config-cache', '')
                   .replace ('--enable-shared', '')
                   .replace ('--disable-static', ''))
        command = re.sub ('--(build|host|target)=[^ ]* ', '', command)
        command = re.sub ('--(includedir|infodir|libdir|mandir|sysconfdir|)=[^ ]* ', '', command)
        
        return ('''CC=%(CC)s'''
                + command)
    def configure_command (self):
# -Dcc=%(CC)s
        return misc.join_lines ('''%(configure_binary)s
 -Dprefix=%(prefix_dir)s
 -Dcc='%(toolchain_prefix)sgcc %(target_gcc_flags)s'
 -Dtargetarch=%(target_architecture)s
 -Dusrinc=%(system_prefix)s/include
 -Dincpth=/
 -Dlibpth=%(system_prefix)s/lib
 -Dlocallibpth=/
 -Aldflags='%(rpath)s'
''')
    def configure (self):
        self.shadow ()
        tools.AutoBuild.configure (self)
        for i in ['%(builddir)s/makefile', '%(builddir)s/x2p/makefile']:
            # Ugh, missing some command?
            self.file_sub ([('^0$','')], i)
