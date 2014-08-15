#include "triangular_matrix_map.h"

TriangularMatrixMap* createTriangularMatrixMap(long* s_keys, unsigned int s_len, long* t_keys, unsigned int t_len)
{
	TriangularMatrixMap* triangularMatrixMap = (TriangularMatrixMap*) malloc (sizeof(TriangularMatrixMap));
	
	sort(s_keys, s_len);
	sort(t_keys, t_len);

	if(t_len < s_len)
		swap(&s_keys, &s_len, &t_keys, &t_len);

	triangularMatrixMap->s_keys = s_keys;
	triangularMatrixMap->t_keys = t_keys;

	triangularMatrixMap->s_len = s_len;
	triangularMatrixMap->t_len = t_len;

	int i;
	int lineLenght;

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
	int i = search(equality_map->s_keys, equality_map->s_len, s_key);
	int j = search(equality_map->t_keys, equality_map->t_len, t_key);

	// confere if needs to swap parameters
	if (i <= j)
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
	int i = search(equality_map->s_keys, equality_map->s_len, s_key);
	int j = search(equality_map->t_keys, equality_map->t_len, t_key);

	// confere if needs to swap parameters
	if (i <= j)
		return equality_map->values[i][j];
	
	return	equality_map->values[j][i];
}

int compareLong(const void * a, const void * b)
{
	return  *(long*)a - *(long*)b;
}

void sort(long* array, unsigned int length)
{
	qsort(array, length, sizeof(long), compareLong);	
}

unsigned int search(long* array, unsigned int length, long key)
{
	return *((unsigned int*) bsearch(&key, array, length, sizeof (long), compareLong));
}

void swap(long** s, unsigned int* len_s, long** t, unsigned int* len_t)
{
	long* aux;
	unsigned int len_aux;

	aux = *t;
	len_aux = *len_t;

	*t = *s;
	*len_t = *len_s;

	*s = aux;
	*len_s = len_aux;
}
