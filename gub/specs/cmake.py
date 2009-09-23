%_mingw32_cmake %{_mingw32_env} ; \
cmake
-DCMAKE_SYSTEM_NAME="Windows"
-DCMAKE_VERBOSE_MAKEFILE=ON
-DCMAKE_INSTALL_PREFIX:PATH=%{_mingw32_prefix}
-DCMAKE_INSTALL_LIBDIR:PATH=%{_mingw32_libdir}
-DINCLUDE_INSTALL_DIR:PATH=%{_mingw32_includedir}
-DLIB_INSTALL_DIR:PATH=%{_mingw32_libdir}
-DSYSCONF_INSTALL_DIR:PATH=%{_mingw32_sysconfdir}
-DSHARE_INSTALL_PREFIX:PATH=%{_mingw32_datadir}
-DBUILD_SHARED_LIBS:BOOL=ON
-DCMAKE_C_COMPILER="%{_bindir}/%{_mingw32_cc}"
-DCMAKE_CXX_COMPILER="%{_bindir}/%{_mingw32_cxx}"
-DCMAKE_FIND_ROOT_PATH="%{_mingw32_prefix}"
-DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY
-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY
-DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER


%{_mingw32_cmake}
	-DQMAKESPEC=win32-%{_mingw32_cxx}
	-DQTDIR=%{_mingw32_prefix}
	-DQT_LIBRARY_DIR="%{_mingw32_libdir}"
	-DQT_INCLUDE_DIR="%{_mingw32_includedir}"
	-DQT_QTCORE_INCLUDE_DIR="%{_mingw32_includedir}/QtCore"
	-DQT_QTGUI_INCLUDE_DIR="%{_mingw32_includedir}/QtGui"
