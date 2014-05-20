#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MIN3(v1, v2, v3) MIN(MIN(v1, v2), v3)
#define MIN(v1, v2) (v1 <= v2 ? v1 : v2)

#define INS_COST 1
#define DEL_COST 1
#define EXC_COST 1

int levenshtein(char*, int, char*, int);
int levenshteinD(char*, int, char*, int);

int main(int argc, char** argv)
{
	int c;

	unsigned int flagDynamic = 0;
	char* s;
	char* t;
	
	unsigned int distance = 0;

	unsigned int len_s;
	unsigned int len_t;

	while ((c = getopt (argc, argv, "s:t:D")) != -1)
	{
		switch(c)
		{
			case 's':
				s = optarg;
				break;
			case 't':
				t = optarg;
				break;
			case 'D':
				flagDynamic = 1;
				break;
			case '?':
				if ((optopt == 's') || (optopt == 't'))
		       			fprintf(stderr, "Option -%c requires an argument.\n", optopt);
				else
		       			fprintf(stderr, "Unknown option `-%c'.\n", optopt);
				return 1;
		}
	}

	len_s = strlen(s);
	len_t = strlen(t);

	if(flagDynamic)
		distance = levenshtein(s, len_s, t, len_t);
	else
		distance = levenshteinD(s, len_s, t, len_t);

	printf("The levesthein distance between words: '%s' and '%s' is %d\n", s, t, distance);

	return 0;
}

int levenshtein(char* s, int len_s, char* t, int len_t)
{
	int i, j;
	unsigned int** d; //[len_s + 1][len_t + 1];

	/*allocate distance matrix*/
	d = (unsigned int**) malloc (sizeof(unsigned int*) * (len_s + 1));
	for (i = 0; i < len_s + 1; i++)
			d[i] = (unsigned int*) malloc (sizeof(unsigned int) * (len_t + 1));


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

	return d[len_s][len_t];
}


int levenshteinD(char* s, int len_s, char* t, int len_t)
{
	unsigned int cost = 0;

	if (len_s == 0)
		return len_t;

	if (len_t == 0)
		return len_s;

	if (s[len_s - 1] == t[len_t - 1])
		cost = 0;
	else
		cost = EXC_COST;

	return MIN3(levenshteinD(s, len_s-1, t, len_t-1) + cost, levenshteinD(s, len_s, t, len_t-1) + INS_COST, levenshteinD(s, len_s-1, t, len_t -1) + DEL_COST);

}
