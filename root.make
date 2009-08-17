## booting binary [fake]root setup

ROOT = GUB
FAKEROOT_CACHE = $(ROOT)/fakeroot.save
#FAKEROOT = $(ROOT)/usr/bin/fakeroot -i $(FAKEROOT_CACHE) -s $(FAKEROOT_CACHE)
#FAKECHROOT = $(ROOT)/usr/bin/fakechroot chroot $(ROOT)
ID=$(shell id -u)
ifneq ($(ID),00)
FAKEROOT = $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/fakeroot-ng -p $(FAKEROOT_CACHE)
endif
FAKECHROOT = $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/chroot $(ROOT)
BUILD_ARCHITECTURE = $(shell $(PYTHON) bin/build-architecture)
UNTAR = cd $(ROOT)/$(BUILD_ARCHITECTURE) && set -x && for i in $$(find packages -name "*.gup" | grep core; find packages -name "*.gup" | grep -v core); do tar xzf $$i; done


boot_packs =\
 gub-utils\
 librestrict\
 dash\
 gawk\
 grep\
 patch\
 coreutils\
 texinfo\
 cross/binutils\
 cross/gcc-core\
 linux-headers\
 glibc-core\
 cross/gcc\
 glibc\
 bash\
 tar\
 make\
 sed\
 ncurses\
 findutils\
 libtool\
 util-linux\
 fakeroot-ng\
 expat\
 zlib\
 gzip\
 bzip2\
 db\
 gdbm\
 python\
 perl\
 m4\
 autoconf\
 automake\
 makedev\
#

# Hmm.  Some of these are not needed in the final root per se
# but are needed to rebuild the root to get context-free checksums
# Such as: bzip2, gzip, m4, autoconf, patch?
root_packs =\
 autoconf\
 automake\
 bash\
 bzip2\
 coreutils\
 cross/binutils\
 cross/gcc-core\
 dash\
 db\
 expat\
 gdbm\
 gub-utils\
 fakeroot-ng\
 glibc-core\
 gzip\
 make\
 makedev\
 patch\
 perl\
 python\
 tar\
 util-linux\
 zlib\

#

# build GUB packages to populate root [eventually for distribution]
boot:
	mkdir -p $(ROOT)
	#sudo ln -sf $(PWD)/GUB /
	set -x; $(foreach i,$(boot_packs),BOOTSTRAP=TRUE bin/gub -x --keep --lax-checksums $(i) &&) :
	mkdir -p BOOTSTRAP/$(BUILD_ARCHITECTURE)/packages
	rsync -az $(ROOT)/$(BUILD_ARCHITECTURE)/packages/ BOOTSTRAP/$(BUILD_ARCHITECTURE)/packages
	rm -f $$(find BOOTSTRAP/$(BUILD_ARCHITECTURE)/packages -name 'glibc' -o -name 'gcc' -o -name 'librestrict' -o -name 'linux-headers' -o -name 'sed' -o -name 'libtool' -o -name 'findutils' | grep -v core)
	mv --backup=t $(ROOT) BOOT || mkdir $(ROOT)

root:
	$(MAKE) setup-root
	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/bash -l -c 'python gbin/gub --keep cross/gcc'
#	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) python gbin/gub --keep cross/gcc
	rsync -az $(ROOT)/$(BUILD_ARCHITECTURE)/packages/ BOOTSTRAP/$(BUILD_ARCHITECTURE)/packages
	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/bash -l -c 'python gbin/gub --keep glibc'
#	BOOTSTRAP=TRUE $(FAKECHROOT) python gbin/gub --keep glibc
	rsync -az $(ROOT)/$(BUILD_ARCHITECTURE)/packages/ BOOTSTRAP/$(BUILD_ARCHITECTURE)/packages
	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/bash -l -c 'python gbin/gub --keep fakeroot-ng'
#	BOOTSTRAP=TRUE $(FAKECHROOT) python gbin/gub --keep fakeroot-ng
	rsync -az $(ROOT)/$(BUILD_ARCHITECTURE)/packages/ BOOTSTRAP/$(BUILD_ARCHITECTURE)/packages

setup-root:
	mkdir -p $(ROOT)
	# Symlink setup
	BOOTSTRAP=$(ROOT) bin/gub > /dev/null || :
	rsync -az ./BOOTSTRAP/ $(ROOT)
	mkdir -p $(ROOT)/downloads/cross/gcc-core
	rsync -az downloads/cross/gcc-core/ $(ROOT)/downloads/cross/gcc-core
	# let's not clutter /bin
	rsync -az bin/ $(ROOT)/gbin
	rsync -az gub librestrict nsis patches sourcefiles $(ROOT)
	$(UNTAR)
	cp -pv sourcefiles/inspect.py $(ROOT)/$(BUILD_ARCHITECTURE)/usr/lib/python2.4/inspect.py
	rm -f $(FAKEROOT_CACHE)
	touch $(FAKEROOT_CACHE)
	$(FAKEROOT) $(FAKECHROOT) /$(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/bash -l -c 'cd /dev && ./MAKEDEV standard'
#	$(FAKEROOT) $(FAKECHROOT) /bin/bash -l -c '($UNTAR)'
#	mv $(ROOT)/dev/urandom $(ROOT)/dev/urandom- || :

# run test build in root
run:
	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) 'python gbin/gub cross/gcc'

# run test build in root
rebuildrun: setup-root
	rm -f $(ROOT)/$(BUILD_ARCHITECTURE)/etc/gup/*
	rsync -az ./BINARIES/ $(ROOT)
	$(UNTAR)
	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/bash -l -c 'python gbin/gub --keep --fresh perl cross/gcc'
	rsync -az $(ROOT)/$(BUILD_ARCHITECTURE)/packages/ BINARIES/$(BUILD_ARCHITECTURE)/packages

# enter into root
chroot:
	BOOTSTRAP=TRUE $(FAKEROOT) $(FAKECHROOT) $(ROOT)/$(BUILD_ARCHITECTURE)/usr/bin/bash -l
