def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['cross/gcc']

def change_target_package (package):
    from gub import cross
    cross.change_target_package (package)

# FIXME: download from sane place; or rather download only kernel
# headers and build full toolchain from source?
def get_sdk():
    '''

#FIXME: how to get libc+kernel headers package contents on freebsd?
# * remove zlib.h, zconf.h or include libz and remove Zlib from src packages?
# * remove gmp.h, or include libgmp and remove Gmp from src packages?
# bumb version number by hand, sync with freebsd.py
freebsd-runtime:
	ssh xs4all.nl tar -C / --exclude=zlib.h --exclude=zconf.h --exclude=gmp.h -czf public_html/freebsd-runtime-4.10-2.tar.gz /usr/lib/{lib{c,c_r,m}{.a,.so{,.*}},crt{i,n,1}.o} /usr/include

    '''
