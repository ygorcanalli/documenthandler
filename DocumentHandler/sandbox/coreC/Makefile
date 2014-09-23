all:
	gcc in.c parallel_levenshtein.c -Wall -pthread -D_GNU_SOURCE -lpapi -o parallel_levenshtein
	gcc in.c sequential_levenshtein.c -Wall -pthread -D_GNU_SOURCE -lpapi -o sequential_levenshtein

