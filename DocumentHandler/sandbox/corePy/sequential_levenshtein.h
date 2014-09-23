#ifndef SEQUENTIAL_LEVENSHTEIN_H
#define SEQUENTIAL_LEVENSHTEIN_H

	#include <stdio.h>
	#include <stdlib.h>
	#include <unistd.h>
	#include <string.h>

	#define MIN3(v1, v2, v3) MIN(MIN(v1, v2), v3)
	#define MIN(v1, v2) (v1 <= v2 ? v1 : v2)

	#define INS_COST 1
	#define DEL_COST 1
	#define EXC_COST 1

	unsigned short int sequential_levenshtein(long*, unsigned int, long*, unsigned int);

#endif
