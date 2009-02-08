config_cache = {
    'tools': '',
    'all': '''
ac_cv_c_stack_direction=${ac_cv_c_stack_direction=-1}
ac_cv_func_getpgrp_void=${ac_cv_func_getpgrp_void=yes}
ac_cv_func_select=${ac_cv_func_select=yes} # but in mingw only if winsock2.h
ac_cv_func_setvbuf_reversed=${ac_cv_func_setvbuf_reversed=no}
ac_cv_lib_dld_shl_load=${ac_cv_lib_dld_shl_load=no}
ac_cv_spinlocks=${ac_cv_spinlocks=no}
ac_cv_sprintf_count=${ac_cv_sprintf_count=yes}
ac_cv_sys_restartable_syscalls=${ac_cv_sys_restartable_syscalls=yes}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib"'"}
lt_cv_dlopen=${lt_cv_dlopen="dlopen"}
''',
    '32': '''
ac_16bit_type=${ac_16bit_type=short}
ac_32bit_type=${ac_32bit_type=int}
ac_64bit_type=${ac_64bit_type=none}
ac_cv_c_long_size_t=${ac_cv_c_long_size_t=no}
ac_cv_c_long_time_t=${ac_cv_c_long_time_t=yes}
ac_cv_sizeof___int64=${ac_cv_sizeof___int64=0}
ac_cv_sizeof_char=${ac_cv_sizeof_char=1}
ac_cv_sizeof_char_p=${ac_cv_sizeof_char_p=4}
ac_cv_sizeof_double=${ac_cv_sizeof_double=8}
ac_cv_sizeof_float=${ac_cv_sizeof_float=4}
ac_cv_sizeof_int=${ac_cv_sizeof_int=4}
ac_cv_sizeof_intmax_t=${ac_cv_sizeof_intmax_t=8}
ac_cv_sizeof_intptr_t=${ac_cv_sizeof_intptr_t=4}
ac_cv_sizeof_long=${ac_cv_sizeof_long=4}
ac_cv_sizeof_long_double=${ac_cv_sizeof_long_double=12}
ac_cv_sizeof_long_long=${ac_cv_sizeof_long_long=8}
ac_cv_sizeof_ptrdiff_t=${ac_cv_sizeof_ptrdiff_t=4}
ac_cv_sizeof_short=${ac_cv_sizeof_short=2}
ac_cv_sizeof_size_t=${ac_cv_sizeof_size_t=4}
ac_cv_sizeof_uintptr_t=${ac_cv_sizeof_uintptr_t=4}
ac_cv_sizeof_unsigned___int64=${ac_cv_sizeof_unsigned___int64=0}
ac_cv_sizeof_unsigned_char=${ac_cv_sizeof_unsigned_char=1}
ac_cv_sizeof_unsigned_int=${ac_cv_sizeof_unsigned_int=4}
ac_cv_sizeof_unsigned_long=${ac_cv_sizeof_unsigned_long=4}
ac_cv_sizeof_unsigned_long_long=${ac_cv_sizeof_unsigned_long_long=8}
ac_cv_sizeof_unsigned_short=${ac_cv_sizeof_unsigned_short=2}
ac_cv_sizeof_void_p=${ac_cv_sizeof_void_p=4}
ac_cv_sizeof_wchar_t=4
''',
    '64': '''
ac_16bit_type=${ac_16bit_type=short}
ac_32bit_type=${ac_32bit_type=int}
ac_64bit_type=${ac_64bit_type=long}
ac_cv_c_long_size_t=${ac_cv_c_long_size_t=yes}
ac_cv_c_long_time_t=${ac_cv_c_long_time_t=yes}
ac_cv_sizeof___int64=${ac_cv_sizeof___int64=0}
ac_cv_sizeof_char=${ac_cv_sizeof_char=1}
ac_cv_sizeof_char_p=${ac_cv_sizeof_char_p=8}
ac_cv_sizeof_double=${ac_cv_sizeof_double=8}
ac_cv_sizeof_float=${ac_cv_sizeof_float=4}
ac_cv_sizeof_int=${ac_cv_sizeof_int=4}
ac_cv_sizeof_intmax_t=${ac_cv_sizeof_intmax_t=8}
ac_cv_sizeof_intptr_t=${ac_cv_sizeof_intptr_t=8}
ac_cv_sizeof_long=${ac_cv_sizeof_long=8}
ac_cv_sizeof_long_double=${ac_cv_sizeof_long_double=16}
ac_cv_sizeof_long_long=${ac_cv_sizeof_long_long=8}
ac_cv_sizeof_ptrdiff_t=${ac_cv_sizeof_ptrdiff_t=8}
ac_cv_sizeof_short=${ac_cv_sizeof_short=2}
ac_cv_sizeof_size_t=${ac_cv_sizeof_size_t=8}
ac_cv_sizeof_uintptr_t=${ac_cv_sizeof_uintptr_t=8}
ac_cv_sizeof_unsigned___int64=${ac_cv_sizeof_unsigned___int64=0}
ac_cv_sizeof_unsigned_char=${ac_cv_sizeof_unsigned_char=1}
ac_cv_sizeof_unsigned_int=${ac_cv_sizeof_unsigned_int=4}
ac_cv_sizeof_unsigned_long=${ac_cv_sizeof_unsigned_long=8}
ac_cv_sizeof_unsigned_long_long=${ac_cv_sizeof_unsigned_long_long=8}
ac_cv_sizeof_unsigned_short=${ac_cv_sizeof_unsigned_short=2}
ac_cv_sizeof_void_p=${ac_cv_sizeof_void_p=8}
''',
    'arm' : '''
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="-ldl"}
glib_cv_uscore=${glib_cv_uscore=no}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib"'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
''',
    'mipsel' : '''
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="-ldl"}
glib_cv_uscore=${glib_cv_uscore=no}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib"'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
''',
    'freebsd-x86' : '''
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=no}
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=no}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=no}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}
ac_cv_search_dlopen=${ac_cv_search_dlopen="none required"}
glib_cv_uscore=${glib_cv_uscore=no}
libc_cv_c_cleanup=${libc_cv_c_cleanup=yes}
libc_cv_forced_unwind=${libc_cv_forced_unwind=yes}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib "'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-lc"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
''',
    'linux-x86' : '''
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=yes}
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="-ldl"}
glib_cv_uscore=${glib_cv_uscore=no}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib"'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
''',
    'linux-64' : '''
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=yes}
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="-ldl"}
glib_cv_uscore=${glib_cv_uscore=no}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib"'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
''',
    'darwin-ppc' : '''
ac_cv_c_bigendian=${ac_cv_c_bigendian=yes}
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=no}
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="none required"}
ac_cv_type_socklen_t=${ac_cv_type_socklen_t=yes}
glib_cv_uscore=${glib_cv_uscore=no}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
    'linux-ppc' : '''
ac_cv_c_bigendian=${ac_cv_c_bigendian=yes}
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=yes}
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="-ldl"}
glib_cv_uscore=${glib_cv_uscore=no}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_root)s/lib"'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
''',
    'darwin-x86' : '''
ac_cv_c_bigendian=${ac_cv_c_bigendian=no}
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=no}
ac_cv_func_posix_getgrgid_r=${ac_cv_func_posix_getgrgid_r=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_search_dlopen=${ac_cv_search_dlopen="none required"}
ac_cv_type_socklen_t=${ac_cv_type_socklen_t=yes}
glib_cv_uscore=${glib_cv_uscore=no}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
    'cygwin': '''
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=no}
ac_cv_func_lstat_dereferences_slashed_symlink=${ac_cv_func_lstat_dereferences_slashed_symlink=yes}
ac_cv_func_malloc_0_nonnull=${ac_cv_func_malloc_0_nonnull=yes}
ac_cv_func_memcmp_working=${ac_cv_func_memcmp_working=yes}
ac_cv_func_mkfifo=${ac_cv_func_mkfifo=yes}
ac_cv_func_stat_empty_string_bug=${ac_cv_func_stat_empty_string_bug=no}
ac_cv_have_dev_ptc=${ac_cv_have_dev_ptc=}
ac_cv_have_dev_ptmx=${ac_cv_have_dev_ptmx=}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}
ac_cv_search_dlopen=${ac_cv_search_dlopen="none required"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_prefix)s/lib/w32api %(system_root)s/lib"'"}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
    'mingw': '''
ac_cv_c_c99_format=${ac_cv_c_c99_format=no}
ac_cv_exeext=${ac_cv_exeext=.exe}
ac_cv_file__dev_ptc=${ac_cv_file__dev_ptc=no}
ac_cv_file__dev_ptmx=${ac_cv_file__dev_ptmx=no}
ac_cv_func_malloc_0_nonnull=${ac_cv_func_malloc_0_nonnull=yes}
ac_cv_func_memcmp_working=${ac_cv_func_memcmp_working=yes}
ac_cv_func_mkfifo=${ac_cv_func_mkfifo=no}
ac_cv_func_stat_empty_string_bug=${ac_cv_func_stat_empty_string_bug=no}
ac_cv_have_dev_ptc=${ac_cv_have_dev_ptc=no}
ac_cv_have_dev_ptmx=${ac_cv_have_dev_ptmx=no}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}
ac_cv_search_dlopen=${ac_cv_search_dlopen=no}
ac_cv_type_struct_sockaddr_storage=${ac_cv_type_struct_sockaddr_storage=yes}
ac_exeext=${ac_exeext=}
libltdl_cv_lib_dl_dlopen=${libltdl_cv_lib_dl_dlopen=yes}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_prefix)s/lib %(system_prefix)s/lib/w32api %(system_root)s/lib"'"}
lt_cv_dlopen=${lt_cv_dlopen=LoadLibrary}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
'''
}

config_cache['linux-64'] = config_cache['linux-x86']
config_cache['freebsd-64'] = config_cache['freebsd-x86']

config_cache['arm'] += config_cache['32']
config_cache['cygwin'] += config_cache['32']
config_cache['darwin-ppc'] += config_cache['32']
config_cache['darwin-x86'] += config_cache['32']
config_cache['freebsd-64'] += config_cache['64']
config_cache['freebsd-x86'] += config_cache['32']
config_cache['linux-64'] += config_cache['64']
config_cache['linux-x86'] += config_cache['32']
config_cache['linux-ppc'] += config_cache['32']
config_cache['mingw'] += config_cache['32']
config_cache['mipsel'] += config_cache['32']

config_cache['debian'] = config_cache['linux-x86']
config_cache['debian-arm'] = config_cache['arm']
config_cache['debian-mipsel'] = config_cache['mipsel']
config_cache['linux-mipsel'] = config_cache['mipsel']
config_cache['linux-arm'] = config_cache['arm']
config_cache['linux-arm-softfloat'] = config_cache['arm']
config_cache['linux-arm-vfp'] = config_cache['arm']

config_cache['freebsd4-x86'] = config_cache['freebsd-x86']
config_cache['freebsd6-x86'] = config_cache['freebsd-x86']
config_cache['freebsd6-64'] = config_cache['freebsd-64']
