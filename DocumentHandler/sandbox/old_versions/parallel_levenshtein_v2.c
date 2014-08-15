/*
Universidade Federal Rural do Rio de Janeiro.
Instituto Multidisciplinar.
Departamento de Tecnologia e Linguagens.
Curso de Ciência da Computaćão.

Autores: Alexsander Andrade de Melo e Ygor de Mello Canalli.
Data (última atualização): 21/05/2014

dL'essentiel est invisible pour les yeux
*/


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <semaphore.h>
#include <sys/types.h>
#include <papi.h>

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
	char* s;
	int len_s;
	char* t;
	int len_t;
}levenshtein_args;
/*==========================================================*/


/*====================Functions headers=====================*/
int levenshtein(char*, int, char*, int);
void* hlevenshtein(void*);
void* vlevenshtein(void*);
void swap(char**, int*, char**, int*);
/*==========================================================*/


/*====================Shared memory=========================*/
unsigned int** d; 		/*distance matrix*/
//sem_t vsem;		  /*vertical semaphore*/
//sem_t hsem;		  /*horizontal semaphore*/
pthread_mutex_t vmux; /*mutex*/
pthread_mutex_t hmux; /*mutex*/
/*==========================================================*/

/*====================Assumptions===========================*/
/*
	s => string in horizontal
	t => string in vertical

	Always len(s) <= len(t), otherwise make swap
	len(diagonal(s, t)) = min(len(s), len(t) =>
		len(diagonal(s, t) = len(s)

	Levenshtein for horizontal side is priority
*/
/*==========================================================*/


int main(int argc, char** argv)
{
	int c;
	char* s;
	char* t;
	
	unsigned int distance = 0;

	unsigned int len_s;
	unsigned int len_t;

	/*for measuring time*/
	long_long start_usec, end_usec;

	while ((c = getopt (argc, argv, "s:t:")) != -1)
	{
		switch(c)
		{
			case 's':
				s = optarg;
				break;
			case 't':
				t = optarg;
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

	/*get initial time*/
	start_usec = PAPI_get_real_usec();

	/*computing levenshtein*/
	distance = levenshtein(s, len_s, t, len_t);

	/*computing final time*/
	end_usec = PAPI_get_real_usec();

	printf("\nThe levesthein distance: %d", distance);
	printf("\nTotal time spent: %.8f (s)\n", (end_usec - start_usec) / 1000000.0);

	return 0;
}



int levenshtein(char* s, int len_s, char* t, int len_t)
{
	int i, j;

	pthread_t vthread;
	pthread_t hthread;
	levenshtein_args varg; 
	levenshtein_args harg;

	/*initalization horizontal semaphore*/
	pthread_mutex_init(&vmux, NULL);

	/*initalization horizontal semaphore*/
	pthread_mutex_init(&hmux, NULL);
	pthread_mutex_lock(&hmux);


	/*Always the lowest string is horizontal*/
	if(len_t <= len_s)
		swap(&s, &len_s, &t, &len_t);

	/*allocate distance matrix*/
	d = (unsigned int**) malloc (sizeof(unsigned int*) * (len_t + 1));
	for (i = 0; i < len_t + 1; i++)
			d[i] = (unsigned int*) malloc (sizeof(unsigned int) * (len_s + 1));

	/*initialization of distance matrix*/
	for (i = 0;  i < len_t + 1; i++)
		d[i][0] = i;

	for (j = 0;  j < len_s + 1; j++)
		d[0][j] = j;

	/*define threads args*/
	varg.s = harg.s = s;
	varg.len_s = harg.len_s = len_s;
	varg.t = harg.t = t;
	varg.len_t = harg.len_t = len_t;

	/*call levenshtein*/
	pthread_create(&hthread, NULL, hlevenshtein, (void*) &harg);
	pthread_create(&vthread, NULL, vlevenshtein, (void*) &varg);
	
	pthread_join(hthread, NULL);
	pthread_join(vthread, NULL);


	return d[len_t][len_s];
}


void* hlevenshtein(void* arg)
{
	levenshtein_args* la = (levenshtein_args*) arg;
	char* s = la->s;
	int len_s = la->len_s;
	char* t = la->t;

	int i, j;

	for (i = 1;  i < len_s + 1; i++)
	{
		/*decrease vertical semaphore*/
		pthread_mutex_lock(&vmux);
	
		/*computing levenshtein distante for first case*/
		j = i;
		if(j < len_s + 1)
		{
			if (t[i-1] == s[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}

		/*increase horizontal sempahore*/
		pthread_mutex_unlock(&hmux);
		
		/*computing levenshtein distante for others case*/
		for (++j;  j < len_s + 1; j++)
		{				
			if (t[i-1] == s[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}
	}

	return 0;
}


void* vlevenshtein(void* arg)
{
	levenshtein_args* la = (levenshtein_args*) arg;
	char* s = la->s;
	int len_s = la->len_s;
	char* t = la->t;
	int len_t = la->len_t;

	int i, j;

	for (j = 1;  j < len_s + 1; j++)
	{
		/*decrease vertical semaphore*/
		pthread_mutex_lock(&hmux);
	
		/*computing levenshtein distante for first case*/
		i = j + 1;

		if(i < len_t + 1)
		{
			if (t[i-1] == s[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}

		/*increase horizontal sempahore*/
		pthread_mutex_unlock(&vmux);
		
		/*computing levenshtein distante for others case*/
		for (++i;  i < len_t + 1; i++)
		{				
			if (t[i-1] == s[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}
	}

	return 0;
}


void swap(char** s, int* len_s, char** t, int* len_t)
{
	char* aux;
	unsigned int len_aux;

	aux = *t;
	len_aux = *len_t;

	*t = *s;
	*len_t = *len_s;

	*s = aux;
	*len_s = len_aux;
}


