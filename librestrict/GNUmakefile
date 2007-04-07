
librestrict.so: restrict.c 
	gcc -shared -fPIC -o $@ $<

test-librestrict: restrict.c 
	gcc -o $@ -DTEST_SELF $< 
