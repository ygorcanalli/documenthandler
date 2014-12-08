all:
	gcc -fpic -c liblevensthein.c levenshtein.c triangular_matrix_map.c -Wall -pthread -D_GNU_SOURCE -I/usr/include/python2.7 -lpython2.7
	gcc -shared -o liblevenshtein.so *.o
	rm *.o
