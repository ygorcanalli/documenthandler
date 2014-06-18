all:
	gcc -fpic -c liblevensthein.c parallel_levenshtein.c sequential_levenshtein.c -Wall -Werror -pthread -I/usr/include/python2.7 -lpython2.7
	gcc -shared -o liblevenshtein.so *.o
	rm *.o
