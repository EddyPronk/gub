prefix = /usr

CC = gcc
NM = nm
CFLAGS = -W -Wall

ALL_CFLAGS = $(CFLAGS)
INSTALL = install

FLAVOURS = exec open stat
TARGETS = librestrict.so $(FLAVOURS:%=librestrict-%.so)

have_fno_stack_protector = $(strip $(shell echo 'int i;' | gcc -fno-stack-protector -c -xc -o /dev/null - 2> /dev/null && echo yes || echo no))

ifeq ($(have_fno_stack_protector),yes)
ALL_CFLAGS += -fno-stack-protector
endif

ifeq ($(LIBRESTRICT),)
LIBRESTRICT_ADDINS = open
else
LIBRESTRICT_ADDINS = $(subst :, ,$(LIBRESTRICT))
endif

LIBRESTRICT_SOURCES = $(LIBRESTRICT_ADDINS:%=restrict-%.c)

all: $(TARGETS)

install: all

test: test-librestrict

install:
	$(INSTALL) -m 755 -d $(DESTDIR)$(prefix)/lib
	$(INSTALL) -m 755 $(TARGET) $(DESTDIR)$(prefix)/lib/$(TARGET)

#%.os: %.c restrict.c
#	$(CC) $(ALL_CFLAGS) -c -fPIC -o $@ $<
#
#lib%.so: %.os
#	$(CC) $(ALL_CFLAGS) -shared -fPIC -o $@ $^

#librestrict.so: $(LIBRESTRICT_OBJECTS)
#	$(CC) $(ALL_CFLAGS) -shared -fPIC -o $@ $^

lib%.so: %.c restrict.c
	$(CC) $(ALL_CFLAGS) -shared -fPIC -o $@ $<

librestrict.c: $(LIBRESTRICT_SOURCES)
	cat $(LIBRESTRICT_SOURCES) > $@

librestrict.so: librestrict.c restrict.c
	$(CC) $(ALL_CFLAGS) -shared -fPIC -o $@ $<
	rm -f librestrict.c

test-librestrict: restrict.c 
	$(CC) $(ALL_CFLAGS) -o $@ -DTEST_SELF $< 
	have_24_symbols=$$($(NM) $@ | grep '@GLIBC_2\.4' || :); echo "2.4 symbols: $$have_24_symbols" && test -z "$$have_24_symbols"
	rm -f $@

clean:
	rm -f librestrict-all.c *.os *.so
