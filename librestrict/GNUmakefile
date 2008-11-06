prefix = /usr

CC = gcc
NM = nm
CFLAGS = -W -Wall

ALL_CFLAGS = $(CFLAGS)
INSTALL = install
TARGET = librestrict.so

have_fno_stack_protector = $(strip $(shell echo 'int i;' | gcc -fno-stack-protector -c -xc -o /dev/null - 2> /dev/null && echo yes || echo no))

ifeq ($(have_fno_stack_protector),yes)
ALL_CFLAGS += -fno-stack-protector
endif

all: $(TARGET)

install: all

test: test-librestrict

install:
	$(INSTALL) -m 755 -d $(DESTDIR)$(prefix)/lib
	$(INSTALL) -m 755 $(TARGET) $(DESTDIR)$(prefix)/lib/$(TARGET)

$(TARGET): restrict.c 

	$(CC) $(ALL_CFLAGS) -shared -fPIC -o $@ $<

test-librestrict: restrict.c 
	$(CC) $(ALL_CFLAGS) -o $@ -DTEST_SELF $< 
	have_24_symbols=$$($(NM) $@ | grep '@GLIBC_2\.4' || :); echo "2.4 symbols: $$have_24_symbols" && test -z "$$have_24_symbols"
	rm -f $@
