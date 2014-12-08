/*
Universidade Federal Rural do Rio de Janeiro.
Instituto Multidisciplinar.
Departamento de Tecnologia e Linguagens.
Curso de Ciência da Computaćão.

Autores: Alexsander Andrade de Melo e Ygor de Mello Canalli.
Data (última atualização): 19/06/2014

dL'essentiel est invisible pour les yeux
*/


#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <semaphore.h>
#include <sys/types.h>
#include <sched.h>
#include "triangular_matrix_map.h"

/*====================Macros================================*/
#define MIN3(v1, v2, v3) MIN(MIN(v1, v2), v3)
#define MIN(v1, v2) (v1 <= v2 ? v1 : v2)
/*==========================================================*/


/*====================Operations cost=======================*/
#define INS_COST 1
#define DEL_COST 1
#define EXC_COST 1
/*==========================================================*/


/*====================Structs===============================*/
typedef struct
{
	long* s;
	unsigned int len_s;
	long* t;
	unsigned int len_t;
	TriangularMatrixMap* equality_map;
}levenshtein_args;
/*==========================================================*/


/*====================Functions headers=====================*/
unsigned short int sequential_levenshtein(long*, unsigned int, long*, unsigned int, TriangularMatrixMap* equality_map);
unsigned short int parallel_levenshtein(long*, unsigned int, long*, unsigned int, TriangularMatrixMap* equality_map);
void* hlevenshtein(void*);
void* vlevenshtein(void*);
byte equals(TriangularMatrixMap*, long, long);
void defineCPUAffinity(unsigned int*, unsigned int);
/*==========================================================*/


/*====================Shared memory=========================*/
unsigned short int* md;	/*main diagonal distance*/
unsigned short int* sd;	/*secondary diagonal distance*/
pthread_mutex_t vmux; /*mutex*/
pthread_mutex_t hmux; /*mutex*/

unsigned short int verticalReturn; /*return of vertical side*/
/*==========================================================*/


/*====================Assumptions===========================*/
/*
	s => string in horizontal
	t => string in vertical

	Always len(s) <= len(t), otherwise make swap
	len(diagonal(s, t)) = min(len(s), len(t) =>
		len(diagonal(s, t)) = len(s)

	Levenshtein for horizontal side is priority
*/
/*==========================================================*/
