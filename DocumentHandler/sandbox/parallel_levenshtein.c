/*
Universidade Federal Rural do Rio de Janeiro.
Instituto Multidisciplinar.
Departamento de Tecnologia e Linguagens.
Curso de Ciência da Computaćão.

Autores: Alexsander Andrade de Melo e Ygor de Mello Canalli.
Data (última atualização): 02/04/2014

dL'essentiel est invisible pour les yeux
*/


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <semaphore.h>
#include <sys/types.h>

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
/*==========================================================*/


/*====================Shared memory=========================*/
unsigned int** d; /*distance matrix*/
sem_t vsem;		  /*vertical semaphore*/
sem_t hsem;		  /*horizontal semaphore*/
/*==========================================================*/



int main(int argc, char** argv)
{
	int c;
	char* s;
	char* t;
	
	unsigned int distance = 0;

	unsigned int len_s;
	unsigned int len_t;

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

	distance = levenshtein(s, len_s, t, len_t);

	printf("The levesthein distance between words: '%s' and '%s' is %d\n", s, t, distance);

	return 0;
}



int levenshtein(char* s, int len_s, char* t, int len_t)
{
	int i, j;
	pthread_t vthread;
	levenshtein_args varg; 
	levenshtein_args harg;

	/*allocate distance matrix*/
	d = (unsigned int**) malloc (sizeof(unsigned int*) * (len_s + 1));
	for (i = 0; i < len_s + 1; i++)
			d[i] = (unsigned int*) malloc (sizeof(unsigned int) * (len_t + 1));

	/*initialization of distance matrix*/
	for (j = 0;  j < len_t + 1; j++)
		d[0][j] = j;

	for (i = 0;  i < len_s + 1; i++)
		d[i][0] = i;

	/*define threads args*/
	varg.s = harg.s = s;
	varg.len_s = harg.len_s = len_s;
	varg.t = harg.t = t;
	varg.len_t = harg.len_t = len_t;

	/*initalization horizontal semaphore*/
	sem_init(&hsem, 0, 0);

	/*initalization horizontal semaphore*/
	sem_init(&vsem, 0, 0);

	/*call levenshtein*/
	pthread_create(&vthread, NULL, vlevenshtein, (void*) &varg);	/*vertical in new thread*/
	hlevenshtein(&harg); 	/*horizontal in main thread*/
	pthread_join(vthread, NULL);

	/*close semaphores*/
	sem_close(&hsem);
	sem_close(&vsem);

	return d[len_s][len_t];
}


void* hlevenshtein(void* arg)
{
	levenshtein_args* la = (levenshtein_args*) arg;
	char* s = la->s;
	int len_s = la->len_s;
	char* t = la->t;
	int len_t = la->len_t;

	int i, j;
	int range = MIN(len_s, len_t);
	int flagMin = len_t <= len_s;

	for (i = 1;  i < range + 1; i++)
	{
		/*decrease vertical semaphore*/
		if((!flagMin) || (i > 1))
			sem_wait(&vsem);

		
		/*computing levenshtein distante for first case*/
		j = i + (!flagMin);
		if(j < len_t + 1)
		{
			if (s[i-1] == t[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}

		/*increase horizontal sempahore*/
		sem_post(&hsem);
		
		/*computing levenshtein distante for others case*/
		for (++j;  j < len_t + 1; j++)
		{				
			if (s[i-1] == t[j-1])
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
	int range = MIN(len_s, len_t);
	int flagMin = len_s < len_t; //len_t >= len_S

	for (j = 1;  j < range + 1; j++)
	{	
		
		/*decrease vertical semaphore*/
		if((!flagMin) || (j > 1))
			sem_wait(&hsem);

		/*computing levenshtein distante for first case*/
		i = j + (!flagMin);
		if(i < len_s + 1)
		{
			if (s[i-1] == t[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}

		/*increase horizontal sempahore*/
		sem_post(&vsem);
		
		/*computing levenshtein distante for others cases*/
		for (++i;  i < len_s + 1; i++)
		{
			if (s[i-1] == t[j-1])
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1]);
			else
				d[i][j] = MIN3(d[i-1][j] + DEL_COST, d[i][j-1] + INS_COST, d[i-1][j-1] + EXC_COST);
		}
	}

	return 0;
}


