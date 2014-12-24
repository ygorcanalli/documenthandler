all:
	gcc -fpic -c liblevensthein.c levenshtein.c matrix_map.c -Wall -pthread -D_GNU_SOURCE -I/usr/include/python3.4 -lpython3.4
	gcc -shared -o liblevenshtein.so *.o
	rm *.o
