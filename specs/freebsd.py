import os
import re

import download
import framework
import gub
import mingw

class Binutils (mingw.Binutils):
	def configure_command (self):
		# Add --program-prefix, otherwise we get
		# i686-freebsd-FOO iso i686-freebsd4-FOO.
		return (mingw.Binutils.configure_command (self)
			+ gub.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Gcc (mingw.Gcc):
#Configuring in i686-freebsd4/libstdc++-v3
#configure: creating cache ./config.cache
#checking build system type... i486-pc-linux-gnu
#checking host system type... i686-pc-freebsd4
#checking target system type... i686-pc-freebsd4
	def config_cache_settings (self):
		return self.config_cache_overrides ('''
#ac_cv_lib_m_main=${ac_cv_lib_m_main=no}
#ac_cv_func_copysignf=${ac_cv_func_copysignf=yes}
#ac_cv_func___signbit=${ac_cv_func___signbit=yes}
ac_cv_host_alias=${ac_cv_host_alias=i486-pc-linux-gnu}}
ac_cv_env_host_alias_value=${ac_cv_env_host_alias_value=i486-pc-linux-gnu}
ac_cv_host=${ac_cv_host=i486-pc-linux-gnu}
''')

	def configure_command (self):
		# Add --program-prefix, otherwise we get
		# i686-freebsd-FOO iso i686-freebsd4-FOO.

		# Add --build, --host to avoid GCC_NO_EXECUTABLES in
		# libstdc++-v3
		return (mingw.Gcc.configure_command (self)
			+ gub.join_lines ('''
--build=%(build_architecture)s
--disable-multilib
--host=%(build_architecture)s
--program-prefix=%(tool_prefix)s
'''))

	def configure (self):
		##self.config_cache ()
		str = self.config_cache_settings ()

#target/i686-freebsd4/build/gcc-3.4.5/intl/config.cache
#target/i686-freebsd4/build/gcc-3.4.5/config.cache
#target/i686-freebsd4/build/gcc-3.4.5/gcc/config.cache
#target/i686-freebsd4/build/gcc-3.4.5/libiberty/config.cache
#target/i686-freebsd4/build/gcc-3.4.5/i686-freebsd4/libstdc++-v3/config.cache
                # code dup
		if str:
			self.system ('mkdir -p %(builddir)s')
			#cache_file = '%(builddir)s/config.cache'
                        cache_file = 'target/i686-freebsd4/build/gcc-3.4.5/i686-freebsd4/libstdc++-v3/config.cache'
			self.dump (self.config_cache_settings (), cache_file)
			os.chmod (self.expand (cache_file), 0755)

		mingw.Gcc.configure (self)


def get_packages (settings):
	return (
		Binutils (settings).with (version='2.16.1', format='bz2'),
#		Gcc (settings).with (version='4.0.2', mirror=download.gcc, format='bz2'),
		Gcc (settings).with (version='3.4.5', mirror=download.gcc, format='bz2',
				     depends=['binutils']
				     ),
		)

def change_target_packages (packages):
	pass
