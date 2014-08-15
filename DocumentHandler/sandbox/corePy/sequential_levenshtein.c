#include "sequential_levenshtein.h"

unsigned short int sequential_levenshtein(long* s, unsigned int len_s, long* t, unsigned int len_t)
{
	unsigned int i, j;
	unsigned short int** d; //[len_s + 1][len_t + 1];
	unsigned short int distance;

	/*allocate distance matrix*/
	d = (unsigned short int**) malloc (sizeof(unsigned short int*) * (len_s + 1));
	for (i = 0; i < len_s + 1; i++)
			d[i] = (unsigned short int*) malloc (sizeof(unsigned short int) * (len_t + 1));


	for (i = 0;  i < (len_s + 1); i++)
		d[i][0] = i;

	for (j = 0;  j < (len_t + 1); j++)
		d[0][j] = j;

	for (i = 1;  i < (len_s + 1); i++)
	{
		for (j = 1;  j < (len_t + 1); j++)
		{
			if (s[i-1] == t[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}
	}

	distance = d[len_s][len_t];

	/*free memory*/
	for (i = 0; i < len_s + 1; i++)
		free(d[i]);

	return distance;
}
