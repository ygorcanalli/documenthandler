#include <Python.h>
#include "sequential_levenshtein.h"
#include "parallel_levenshtein.h"

long* convertPySequenceToCArray(PyObject*, unsigned int);

static PyObject* liblevenshtein_parallel_levensthein(PyObject *self, PyObject *args)
{
	PyObject* seq_s;
	PyObject* seq_t;

	unsigned int len_s;
	unsigned int len_t;

	long* s;
	long* t;

	unsigned short int distance;

	if (!PyArg_ParseTuple(args, "OIOI", &seq_s, &len_s, &seq_t, &len_t))
		return NULL;

	s = convertPySequenceToCArray(seq_s, len_s);
	t = convertPySequenceToCArray(seq_t, len_t);

	/*error*/
	if((s == NULL) || (t == NULL))
	{
		printf("\nerror: invalid sequence!");
		exit(0);
		//return NULL;
	}

	/*calling function*/
	distance = parallel_levenshtein(s, len_s, t, len_t);

	free(s);
	free(t);

	/*return in Python type*/
	return Py_BuildValue("H", distance);
}

static PyObject* liblevenshtein_sequential_levensthein(PyObject *self, PyObject *args)
{
	PyObject* seq_s;
	PyObject* seq_t;

	unsigned int len_s;
	unsigned int len_t;

	long* s;
	long* t;

	unsigned short int distance;

	if (!PyArg_ParseTuple(args, "OIOI", &seq_s, &len_s, &seq_t, &len_t))
		return NULL;

	s = convertPySequenceToCArray(seq_s, len_s);
	t = convertPySequenceToCArray(seq_t, len_t);

	/*error*/
	if((s == NULL) || (t == NULL))
	{
		printf("\nerror: invalid sequence!");
		exit(0);
		//return NULL;
	}

	/*calling function*/
	distance = sequential_levenshtein(s, len_s, t, len_t);

	free(s);
	free(t);

	/*return in Python type*/
	return Py_BuildValue("H", distance);
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
