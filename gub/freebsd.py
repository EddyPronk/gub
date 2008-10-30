from gub import cross

def get_cross_build_dependencies (settings):
    return ['cross/gcc', 'freebsd-runtime']

def change_target_package (package):
    cross.change_target_package (package)

# FIXME: download from sane place; or rather download only kernel
# headers and build full toolchain from source?
def get_sdk ():
    '''
#! /bin/sh

if test $# != '3'; then
    cat <<EOF
Usage: get-freebsd ARCH VERSION BUILD

Example:
  get-freebsd i386 4.11 1
  get-freebsd amd64 6.2 2
EOF
    exit 2
fi

arch=$1
version=$2
build=$3

tmp=tmp-freebsd-$arch-$version-$build
mkdir -p $tmp && cd $tmp
wget ftp://ftp.surfnet.nl/pub/os/FreeBSD/releases/$arch/$version-RELEASE/base/base.??
wget ftp://ftp-archive.freebsd.org/pub/FreeBSD-Archive/old-releases/$arch/$version-RELEASE/bin/bin.??
rm -rf root
mkdir -p root
cat base.?? bin.?? | tar --unlink -xpzf - -C root
cd root && tar --exclude=zlib.h --exclude=zconf.h --exclude=gmp.h --exclude=curses.h --exclude=ncurses.h --exclude=c++ --exclude=g++ -czf ../../downloads/freebsd-runtime/freebsd-runtime-$version-$build.$arch.tar.gz {,usr/}lib/{lib{c,c_r,m,pthread}{.a,.so{,.*}},crt{i,n,1}.o} usr/include
#rm -rf $tmp
'''
