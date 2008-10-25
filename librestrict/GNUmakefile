CC = gcc -W -Wall
INSTALL = install
TARGET = librestrict.so
prefix = /usr


all: $(TARGET)

install: all

test: test-librestrict

install:
	$(INSTALL) -m 755 -d $(DESTDIR)$(prefix)/lib
	$(INSTALL) -m 755 $(TARGET) $(DESTDIR)$(prefix)/lib/$(TARGET)

$(TARGET): restrict.c 
	$(CC) -shared -fPIC -o $@ $<

test-librestrict: restrict.c 
	$(CC) -o $@ -DTEST_SELF $< 
