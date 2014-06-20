/*
Universidade Federal Rural do Rio de Janeiro.
Instituto Multidisciplinar.
Departamento de Tecnologia e Linguagens.
Curso de Ciência da Computaćão.

Autores: Alexsander Andrade de Melo e Ygor de Mello Canalli.
Data (última atualização): 16/06/2014

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
#include <sched.h>
#include "in.h"

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
	void* s;
	unsigned int len_s;
	void* t;
	unsigned int len_t;
}levenshtein_args;
/*==========================================================*/


/*====================Functions headers=====================*/
unsigned short int levenshtein(void*, unsigned int, void*, unsigned int);
void* hlevenshtein(void*);
void* vlevenshtein(void*);
void defineCPUAffinity(unsigned int*, unsigned int);
void swap(void**, unsigned int*, void**, unsigned int*);
/*==========================================================*/


/*====================Shared memory=========================*/
unsigned short int* md;	/*main diagonal distance*/
unsigned short int* sd;	/*secondary diagonal distance*/
pthread_mutex_t vmux; /*mutex*/
pthread_mutex_t hmux; /*mutex*/

unsigned short int verticalReturn; /*return of vertical side*/
/*==========================================================*/


/*===========General Constants==============================*/
unsigned int hcpu_list[] = {0};
unsigned int vcpu_list[] = {1};
unsigned int hcpu_list_size = 1;
unsigned int vcpu_list_size = 1;
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


int main(int argc, char** argv)
{
	int c;
	char* s;
	char* t;
	
	unsigned short int distance = 0;

	unsigned int len_s;
	unsigned int len_t;

	string* strs;
	string* strt; 

	/*for measuring time*/
	long_long start_usec, end_usec;

	while ((c = getopt (argc, argv, "s:t:")) != -1)
	{
		switch(c)
		{
			case 's':
				strs = readTextFromFile(optarg);
				s = strs->content;
				len_s = strs->len;
				break;
			case 't':
				strt = readTextFromFile(optarg);
				t = strt->content;
				len_t = strt->len;
				break;
			case '?':
				if ((optopt == 's') || (optopt == 't'))
		       			fprintf(stderr, "Option -%c requires an argument.\n", optopt);
				else
		       			fprintf(stderr, "Unknown option `-%c'.\n", optopt);
				return 1;
		}
	}


	/*get initial time*/
	start_usec = PAPI_get_real_usec();

	/*computing levenshtein*/
	distance = levenshtein(s, len_s, t, len_t);

	/*get final time*/
	end_usec = PAPI_get_real_usec();

	printf("\nThe levesthein distance: %d", distance);
	printf("\nTotal time spent: %.8f (s)\n", (end_usec - start_usec) / 1000000.0);

	return 0;
}


unsigned short int levenshtein(void* s, unsigned int len_s, void* t, unsigned int len_t)
{
	pthread_t vthread;
	pthread_t hthread;
	levenshtein_args varg; 
	levenshtein_args harg;

	int sizeSD;
	unsigned short int distance; /*return value*/

	/*initalization horizontal semaphore*/
	pthread_mutex_init(&vmux, NULL);

	/*initalization horizontal semaphore*/
	pthread_mutex_init(&hmux, NULL);
	pthread_mutex_lock(&hmux);


	/*Always the lowest string is horizontal*/
	if(len_t < len_s)
		swap(&s, &len_s, &t, &len_t);

	sizeSD = (len_s == len_t ? len_s : len_s + 1);

	/*allocate main diagonal*/
	md = (unsigned short int*) malloc (sizeof(unsigned short int) * (len_s + 1));
	/*allocate secondary diagonal*/
	sd = (unsigned short int*) malloc (sizeof(unsigned short int) * (sizeSD));

	/*initialization of diagonals distance*/
	md[0] = 0; sd[0] = 1;

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

	if(len_t == len_s)
		distance = md[len_s];
	else if((len_s + 1) < len_t)
		distance = verticalReturn;
	else
		distance = sd[len_s];

	/*free memory*/
	free(md);
	free(sd);

	return distance;
}


void* hlevenshtein(void* arg)
{
	defineCPUAffinity(hcpu_list, hcpu_list_size);

	unsigned short int **hm;
	levenshtein_args* la = (levenshtein_args*) arg;
	char* s = la->s;
	unsigned int len_s = la->len_s;
	char* t = la->t;

	unsigned int i, j, k;

	/*alocate horizontal distance matrix*/
	hm = (unsigned short int**) malloc (sizeof(unsigned short int*) * len_s);
	for (i = 0; i < len_s; i++)
			hm[i] = (unsigned short int*) malloc (sizeof(unsigned short int) * (len_s - i));

	/*initialization of horizontal distance matrix*/
	for(j = 0; j < len_s; j++)
		hm[0][j] = j + 1;

	for (i = 1;  i < (len_s); i++)
	{
		/*decrease vertical semaphore*/
		pthread_mutex_lock(&vmux);
	
		/*computing levenshtein distante for main diagonal*/
		j = i;
		k = 0;

		if (t[i-1] == s[j-1])
			md[i] = MIN3(hm[i-1][k] + DEL_COST, sd[i-1] + INS_COST, md[i-1]);
		else
			md[i] = MIN3(hm[i-1][k] + DEL_COST, sd[i-1] + INS_COST, md[i-1] + EXC_COST);


		/*increase horizontal sempahore*/
		pthread_mutex_unlock(&hmux);
	
		/*computing levenshtein distante for imediate after main diagonal*/
		j++;
		/*k = 0*/

		if(j < (len_s + 1))
		{
			if (t[i-1] == s[j-1])
				hm[i][k] = MIN3(hm[i-1][k+1] + DEL_COST, md[i] + INS_COST, hm[i-1][k]);
			else
				hm[i][k] = MIN3(hm[i-1][k+1] + DEL_COST, md[i] + INS_COST, hm[i-1][k] + EXC_COST);
		}

		
		/*computing levenshtein distante for horizontal matrix*/
		for (++j, ++k;  j < (len_s + 1); j++, k++)
		{				
			if (t[i-1] == s[j-1])
				hm[i][k] = MIN3(hm[i-1][k+1] + DEL_COST, hm[i][k-1] + INS_COST, hm[i-1][k]);
			else
				hm[i][k] = MIN3(hm[i-1][k+1] + DEL_COST, hm[i][k-1] + INS_COST, hm[i-1][k] + EXC_COST);
		}
	}

	/*===========Computation last element of main diagonal==============================*/
	/*decrease vertical semaphore*/
	pthread_mutex_lock(&vmux);

	/*computing levenshtein distante for main diagonal*/
	/*In this case i = len_s */
	j = i;
	k = 0;

	if (t[i-1] == s[j-1])
		md[i] = MIN3(hm[i-1][k] + DEL_COST, sd[i-1] + INS_COST, md[i-1]);
	else
		md[i] = MIN3(hm[i-1][k] + DEL_COST, sd[i-1] + INS_COST, md[i-1] + EXC_COST);

	/*increase horizontal sempahore*/
	pthread_mutex_unlock(&hmux);
	/*==================================================================================*/

	/*free memory*/
	for (i = 0; i < len_s; i++)
		free(hm[i]);
	free(hm);

	return 0;
}


void* vlevenshtein(void* arg)
{
	defineCPUAffinity(vcpu_list, vcpu_list_size);

	unsigned short int **vm;
	levenshtein_args* la = (levenshtein_args*) arg;
	char* s = la->s;
	unsigned int len_s = la->len_s;
	char* t = la->t;
	unsigned int len_t = la->len_t;

	unsigned int i, j, k;

	unsigned int sizeVM = (len_s + 1 < len_t ? len_s + 1 : len_t - 1);
	
	/*Wrong*/
	if(sizeVM <= 0)
		return 0;


	/*alocate vertical distance matrix*/
	vm = (unsigned short int**) malloc (sizeof(unsigned short int*) * (sizeVM));
	for (i = 0, k = len_t - 1; i < (sizeVM); i++, k--)
			vm[i] = (unsigned short int*) malloc (sizeof(unsigned short int) * k);

	/*initialization of vertical distance matrix*/
	for(k = 0; k < (len_t - 1); k++)
		vm[0][k] = len_t - k;

	for (i = 1;  i < sizeVM; i++)
	{
		/*decrease vertical semaphore*/
		pthread_mutex_lock(&hmux);

		/*computing levenshtein distante for secondary diagonal*/
		j = i + 1;
		k = (len_t - 1) - i;

		if (s[i-1] == t[j-1])
			sd[i] = MIN3(md[i] + DEL_COST, vm[i-1][k] + INS_COST, sd[i-1]);
		else
			sd[i] = MIN3(md[i] + DEL_COST, vm[i-1][k] + INS_COST, sd[i-1] + EXC_COST);

		/*increase horizontal sempahore*/
		pthread_mutex_unlock(&vmux);

		/*computing levenshtein distante for imediate after secondary diagonal*/
		j++;
		k--;

		if(j < (len_t + 1))
		{
			if (s[i-1] == t[j-1])
				vm[i][k] = MIN3(sd[i] + DEL_COST, vm[i-1][k] + INS_COST, vm[i-1][k+1]);
			else
				vm[i][k] = MIN3(sd[i] + DEL_COST, vm[i-1][k] + INS_COST, vm[i-1][k+1] + EXC_COST);
		}
		
		/*computing levenshtein distante for others case*/
		for (++j, --k; j < (len_t + 1); j++, k--)
		{			
			if (s[i-1] == t[j-1])
				vm[i][k] = MIN3(vm[i][k+1] + DEL_COST, vm[i-1][k] + INS_COST, vm[i-1][k+1]);
			else
				vm[i][k] = MIN3(vm[i][k+1] + DEL_COST, vm[i-1][k] + INS_COST, vm[i-1][k+1] + EXC_COST);

		}
	}


	/*===========Computation last element of secondary diagonal=========================*/
	if(len_s + 1 >= len_t)
	{
		/*decrease horizontal semaphore*/
		pthread_mutex_lock(&hmux);

		/*computing levenshtein distante for main diagonal*/
		/*In this case i = sizeVM*/
		j = i + 1;
		k = 0;

		if (s[i-1] == t[j-1])
			sd[i] = MIN3(md[i] + DEL_COST, vm[i-1][k] + INS_COST, sd[i-1]);
		else
			sd[i] = MIN3(md[i] + DEL_COST, vm[i-1][k] + INS_COST, sd[i-1] + EXC_COST);

		/*increase vertical sempahore*/
		pthread_mutex_unlock(&vmux);
	}
	/*==================================================================================*/
	else
	{
		/*return to shared memory*/
		verticalReturn = vm[sizeVM - 1][0];
	}

	/*free memory*/
	for (i = 0; i < (sizeVM); i++)
		free(vm[i]);
	free(vm);

	return 0;
}


void defineCPUAffinity(unsigned int* cpu_list, unsigned int size)
{
	cpu_set_t cpuset;
	CPU_ZERO(&cpuset);       //clears the cpuset

	short int i = 0;

	for(i = 0; i < size; i++)
		CPU_SET(cpu_list[i], &cpuset);   //set CPU 'cpu_list[i]' on cpuset

	/*
	* cpu affinity for the calling thread 
	* first parameter is the pid, 0 = calling thread
	* second parameter is the size of your cpuset
	* third param is the cpuset in which your thread will be
	* placed. Each bit represents a CPU
	*/
	sched_setaffinity(0, sizeof(cpuset), &cpuset);
	//pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
}


void swap(void** s, unsigned int* len_s, void** t, unsigned int* len_t)
{
	void* aux;
	unsigned int len_aux;

	aux = *t;
	len_aux = *len_t;

	*t = *s;
	*len_t = *len_s;

	*s = aux;
	*len_s = len_aux;
}

