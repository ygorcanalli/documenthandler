#ifndef TRIANGULAR_MATRIX_MAP_H
#define TRIANGULAR_MATRIX_MAP_H

	#include<stdlib.h>

	#define EQUALS 1
	#define DIFFERENT 0

	typedef unsigned char byte;

	typedef struct
	{
		long* s_keys;
		long* t_keys;
		unsigned int s_len;
		unsigned int t_len;

		byte** values;

	} TriangularMatrixMap; 


	TriangularMatrixMap* createTriangularMatrixMap(long* s_keys, unsigned int s_len, long* t_keys, unsigned int t_len);
	void triangularMatrixMapPut(TriangularMatrixMap* equality_map, long s_key, long t_key, byte value);
	void freeTriangularMatrixMap(TriangularMatrixMap* equality_map);
	unsigned short triangularMatrixMapGet(TriangularMatrixMap* equality_map, long s_key, long t_key);
	int compareLong (const void * a, const void * b);
	void sort(long* array, unsigned int length);
	unsigned int search(long* array, unsigned int length, long key);
	void swap(long** s, unsigned int* len_s, long** t, unsigned int* len_t);

#endif
