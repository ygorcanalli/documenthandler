#include "triangular_matrix_map.h"
#include <stdio.h>

#define min(v1, v2) (v1 <= v2 ? v1 : v2)

TriangularMatrixMap* createTriangularMatrixMap(long* s_keys, unsigned int s_len, long* t_keys, unsigned int t_len)
{
	TriangularMatrixMap* triangularMatrixMap = (TriangularMatrixMap*) malloc (sizeof(TriangularMatrixMap));
	int i;
	int lineLenght;
	
	sort(s_keys, s_len);
	sort(t_keys, t_len);

	triangularMatrixMap->s_keys = s_keys;
	triangularMatrixMap->t_keys = t_keys;

	triangularMatrixMap->s_len = s_len;
	triangularMatrixMap->t_len = t_len;

	triangularMatrixMap->values = (byte**) malloc (sizeof(byte*) * t_len);

	for(i = 0; i < t_len; i++)
	{
		if (i < s_len)
			lineLenght = i + 1;
		else
			lineLenght = s_len;

		triangularMatrixMap->values[i] = (byte*) malloc (sizeof(byte) * lineLenght);
	}

	return triangularMatrixMap;
}

void triangularMatrixMapPut(TriangularMatrixMap* equality_map, long s_key, long t_key, byte value)
{

	int i, j;

	i = search(equality_map->t_keys, equality_map->t_len, t_key);
	j = search(equality_map->s_keys, equality_map->s_len, s_key);

	// confere if needs to swap parameters
	if (j <= i)
		equality_map->values[i][j] = value;
	else
		equality_map->values[j][i] = value;
}

void freeTriangularMatrixMap(TriangularMatrixMap* equality_map)
{
	int i;

	if(equality_map != NULL)
	{
		free(equality_map->s_keys);
		free(equality_map->t_keys);

		for(i = 0; i < equality_map->t_len; i++)
			free(equality_map->values[i]);
		free(equality_map->values);

		free(equality_map);
	}
}

unsigned short triangularMatrixMapGet(TriangularMatrixMap* equality_map, long s_key, long t_key)
{
	int i = search(equality_map->t_keys, equality_map->t_len, t_key);
	int j = search(equality_map->s_keys, equality_map->s_len, s_key);

	// confere if needs to swap parameters
	if (j <= i)
		return equality_map->values[i][j];

	return	equality_map->values[j][i];
}

int compareLong(const void * a, const void * b)
{
	//this way does'nt works!
	//return  ( *(long*)a - *(long*)b );
	long* arg1 = (long*) a;
	long* arg2 = (long*) b;
	if( *arg1 < *arg2 ) return -1;
	else if( *arg1 == *arg2 ) return 0;
	else return 1;
}

void sort(long* array, unsigned int length)
{
	qsort(array, length, sizeof(long), compareLong);
}

unsigned int search(long* array, unsigned int length, long key)
{
	// bsearch does'nt return the index of element, but the pointer
	return (unsigned int) ( (long*) bsearch(&key, array, length, sizeof (long), compareLong) - array);
}


void printTriangularMatrixMap(TriangularMatrixMap* equality_map)
{
	int i, j;

	for(i = 0; i < equality_map->t_len; i++)
	{
		for (j = 0; j < min(i+1, equality_map->s_len); j++)
			printf("%u\t", equality_map->values[i][j]);

		printf("\n");
	}
}
