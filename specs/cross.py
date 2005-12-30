import gub

cross_config_cache = {
	'all': '''

ac_16bit_type=${ac_16bit_type=short}
ac_32bit_type=${ac_32bit_type=int}
ac_64bit_type=${ac_64bit_type=none}
ac_cv_c_long_size_t=${ac_cv_c_long_size_t=no}
ac_cv_c_long_time_t=${ac_cv_c_long_time_t=yes}
ac_cv_c_stack_direction=${ac_cv_c_stack_direction=-1}
ac_cv_exeext=${ac_cv_exeext=}
ac_cv_func_getpgrp_void=${ac_cv_func_getpgrp_void=yes}
ac_cv_func_select=${ac_cv_func_select=yes} # but in mingw only if winsock2.h
ac_cv_func_setvbuf_reversed=${ac_cv_func_setvbuf_reversed=no}
ac_cv_lib_dld_shl_load=${ac_cv_lib_dld_shl_load=no}
ac_cv_search_dlopen=${ac_cv_search_dlopen="none required"}
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
ac_cv_spinlocks=${ac_cv_spinlocks=no}
ac_cv_sprintf_count=${ac_cv_sprintf_count=yes}
ac_cv_sys_restartable_syscalls=${ac_cv_sys_restartable_syscalls=yes}
ac_exeext=${ac_exeext=}

# libtool searches not only in the cross libpath
#     /cygwin/usr/lib:/cygwin/usr/lib/w32api:/usr/i686-cygwin/lib
# but also in /usr/lib.  there it finds libdl.a and adds -ldl
# to LIBS
# it seems that libtool is broken wrt cross compilation:
#    sys_lib_search_path_spec="/usr/lib /lib/w32api /lib /usr/local/lib"
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib /lib /usr/lib"'"}

lt_cv_dlopen=${lt_cv_dlopen="dlopen"}
''',
	'freebsd' : '''
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}
lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-lc"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
##libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(framework_root)s/usr/lib /lib /usr/lib"'"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(framework_root)s/usr/lib /lib /usr/lib"'"}
''',
	'linux' : '''
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
##libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(framework_root)s/usr/lib /lib /usr/lib"'"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(framework_root)s/usr/lib /lib /usr/lib"'"}
''',
	'darwin' : '''
ac_cv_c_bigendian=${ac_cv_c_bigendian=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_type_socklen_t=${ac_cv_type_socklen_t=yes}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
	'cygwin': '''
ac_cv_func_mkfifo=${ac_cv_func_mkfifo=yes}
ac_cv_have_dev_ptc=${ac_cv_have_dev_ptc=}
ac_cv_have_dev_ptmx=${ac_cv_have_dev_ptmx=}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
	'mingw': '''
ac_cv_func_malloc_0_nonnull=${ac_cv_func_malloc_0_nonnull=yes}
ac_cv_func_memcmp_working=${ac_cv_func_memcmp_working=yes}
ac_cv_func_mkfifo=${ac_cv_func_mkfifo=no}
ac_cv_func_stat_empty_string_bug=${ac_cv_func_stat_empty_string_bug=no}
ac_cv_have_dev_ptc=${ac_cv_have_dev_ptc=no}
ac_cv_have_dev_ptmx=${ac_cv_have_dev_ptmx=no}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
'''
}
