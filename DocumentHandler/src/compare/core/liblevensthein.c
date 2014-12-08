#include <Python.h>
#include "levenshtein.h"


void convertArgs(PyObject *, long**, unsigned int*, long**, unsigned int*, MatrixMap**);
long* convertPySequenceToCArray(PyObject*, unsigned int);
MatrixMap* convertPyDictToMatrixMap(PyObject*, PyObject*, unsigned int, PyObject*, unsigned int);
void splitKey(PyObject*, long*, long*);
void swap(void** s, unsigned int* len_s, void** t, unsigned int* len_t);


unsigned short _swap = 0;

static PyObject* liblevenshtein_parallel_levensthein(PyObject *self, PyObject *args)
{
	unsigned int len_s;
	unsigned int len_t;

	long* s;
	long* t;
	MatrixMap* equality_map;

	unsigned short int distance;

	convertArgs(args, &s, &len_s, &t, &len_t, &equality_map);

	/*calling function*/
	distance = parallel_levenshtein(s, len_s, t, len_t, equality_map);

	free(s);
	free(t);
	freeMatrixMap(equality_map);

	/*return in Python type*/
	return Py_BuildValue("H", distance);
}

static PyObject* liblevenshtein_sequential_levensthein(PyObject *self, PyObject *args)
{
	unsigned int len_s;
	unsigned int len_t;

	long* s;
	long* t;
	MatrixMap* equality_map;

	unsigned short int distance;

	convertArgs(args, &s, &len_s, &t, &len_t, &equality_map);

	/*calling function*/
	distance = sequential_levenshtein(s, len_s, t, len_t, equality_map);

	free(s);
	free(t);
	freeMatrixMap(equality_map);

	/*return in Python type*/
	return Py_BuildValue("H", distance);
}

void convertArgs(PyObject *args, long** s, unsigned int* len_s, long** t, unsigned int* len_t, MatrixMap** equality_map)
{
	PyObject* seq_s;
	PyObject* seq_t;

	PyObject* equality_dict = NULL;

	PyObject* set_s = NULL;
	PyObject* set_t = NULL;
	unsigned int len_set_s;
	unsigned int len_set_t;

	if (!PyArg_ParseTuple(args, "OIOI|OOIOI", &seq_s, len_s, &seq_t, len_t, &equality_dict, &set_s, &len_set_s, &set_t, &len_set_t))
	{
		printf("\nerror: invalid parameters!");
		exit(1);
		//return NULL;
	}

	*s = convertPySequenceToCArray(seq_s, *len_s);
	*t = convertPySequenceToCArray(seq_t, *len_t);

	if(*len_t < *len_s)
	{
		_swap = 1;
		swap((void**) s, len_s, (void**) t, len_t);
		swap((void**) &set_s, &len_set_s, (void**) &set_t, &len_set_t);
	}

	if((equality_dict != NULL) && (set_s != NULL) && (set_t != NULL))
	{
		*equality_map = convertPyDictToMatrixMap(equality_dict, set_s, len_set_s, set_t, len_set_t);

	}
	else
		*equality_map = NULL;

	/*error*/
	if((s == NULL) || (t == NULL) || (equality_map == NULL && equality_dict != NULL))
	{
		printf("\nerror: invalid sequence!");
		exit(1);
		//return NULL;
	}
}



static PyMethodDef LiblevenshteinMethods[] = {
	{"parallel_levenshtein", liblevenshtein_parallel_levensthein, METH_VARARGS, "Description.."},
	{"sequential_levenshtein", liblevenshtein_sequential_levensthein, METH_VARARGS, "Description.."},
	{NULL,NULL,0,NULL}
};


PyMODINIT_FUNC initliblevenshtein(void)
{
	PyObject *m;
	m = Py_InitModule("liblevenshtein", LiblevenshteinMethods);
	
	if (m == NULL)
		return;
}


long* convertPySequenceToCArray(PyObject* seq_x, unsigned int len_x)
{
	int i;
	long* x;

	x = (long*) malloc (len_x * sizeof(long));

	if(x == NULL)
	{
		printf("\nUnable to allocate memory");
		Py_DECREF(seq_x);
		return NULL;
		//return PyErr_NoMemory();
	}

	for(i = 0; i < len_x; i++)
	{
		PyObject *fitem;
		PyObject *item = PySequence_Fast_GET_ITEM(seq_x, i);

		if(item == NULL)
		{
			printf("\nCould not get item in the sequence");
			Py_DECREF(seq_x);
			free(x);
			return NULL;
		}

		/*Instead PyNumber_Long is deprecate?*/
		fitem = PyNumber_Long(item);

		if(fitem == NULL)
		{
			printf("\nall items must be integers numbers");
			Py_DECREF(seq_x);
			free(x);
			PyErr_SetString(PyExc_TypeError, "all items must be integers numbers");
			return NULL;
		}

		x[i] = PyLong_AsLong(fitem);
		Py_DECREF(fitem);
	}    

	Py_DECREF(seq_x);

	return x;
}


MatrixMap* convertPyDictToMatrixMap(PyObject* equality_dict, PyObject* set_s, unsigned int len_set_s, PyObject* set_t, unsigned int len_set_t)
{
	MatrixMap* equality_map;

	PyObject *key, *value;
	Py_ssize_t pos = 0;

	long* s_keys;
	long* t_keys;

	long s_key;
	long t_key;

	byte byte_value;

	s_keys = convertPySequenceToCArray(set_s, len_set_s);
	t_keys = convertPySequenceToCArray(set_t, len_set_t);

	equality_map = createMatrixMap(s_keys, len_set_s, t_keys, len_set_t);

	while (PyDict_Next(equality_dict, &pos, &key, &value))
	{
		byte_value = (byte) PyLong_AsLong(value);

		//Swap
		if(!_swap)
			splitKey(key, &s_key, &t_key);
		else
			splitKey(key, &t_key, &s_key);
		
		if ((byte_value != EQUALS) && (byte_value != DIFFERENT))
		{
			printf("Worng value on map: %u\n", (unsigned int) byte_value);
			return NULL;
		}

		matrixMapPut(equality_map, s_key, t_key, byte_value);
	}

	//printMatrixMap(equality_map);

	Py_DECREF(equality_dict);

	return equality_map;
}

void splitKey(PyObject* key, long* s_key, long* t_key)
{
	PyObject *s_number, *t_number;
	PyObject *s_item = PySequence_Fast_GET_ITEM(key, 0);
	PyObject *t_item = PySequence_Fast_GET_ITEM(key, 1);

	if(s_item == NULL || t_item == NULL)
	{
		printf("\nCould not split the key");
		Py_DECREF(key);
	}

	s_number = PyNumber_Long(s_item);
	t_number = PyNumber_Long(t_item);

	if(s_number == NULL || t_number == NULL)
	{
		printf("\nall items must be integers numbers");
		Py_DECREF(key);
	}

	*s_key = PyLong_AsLong(s_number);
	*t_key = PyLong_AsLong(t_number);
	
	Py_DECREF(s_number);
	Py_DECREF(t_number);
	Py_DECREF(key);
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
