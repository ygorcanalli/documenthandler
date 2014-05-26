all:
    gcc -fpic -c parallel_levenshtein.c -Wall -Werror -pthread
    gcc -fpic -c sequential_levenshtein.c -Wall -Werror -pthread
    gcc -shared -o liblevenshtein.so *.o