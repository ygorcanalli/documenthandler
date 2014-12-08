#ifndef MATRIX_MAP_H
#define MATRIX_MAP_H

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

	} MatrixMap; 


	MatrixMap* createMatrixMap(long* s_keys, unsigned int s_len, long* t_keys, unsigned int t_len);
	void matrixMapPut(MatrixMap* equality_map, long s_key, long t_key, byte value);
	void freeMatrixMap(MatrixMap* equality_map);
	unsigned short matrixMapGet(MatrixMap* equality_map, long s_key, long t_key);
	int compareLong (const void * a, const void * b);
	void sort(long* array, unsigned int length);
	unsigned int search(long* array, unsigned int length, long key);

	void printMatrixMap(MatrixMap* equality_map);

#endif
