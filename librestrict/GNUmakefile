CC = gcc -W -Wall
librestrict.so: restrict.c 
	$(CC) -shared -fPIC -o $@ $<

test-librestrict: restrict.c 
	$(CC) -o $@ -DTEST_SELF $< 
