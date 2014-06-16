"""
Created on Apr 30, 2014

@author: ygor
"""
<<<<<<< HEAD

class Levenshtein(object):

	# Load the library
    liblevenshtein = ctypes.CDLL(LIBRARY_PATH)

	# Define function arguments types
    liblevenshtein.parallel_levenshtein.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]

	# Define function return type.
	liblevenshtein.parallel_levenshtein.restype = ctypes.c_int

	def parallel_alignment(self, list_s, list_t):
        #  Get the lenth
        s_len = len(list_s)
        t_len = len(list_t)

        # Convert the values to typec
        s_c = (ctypes.c_char_p * s_len)(*list_s)
        t_c = (ctypes.c_char_p * t_len)(*list_t)

        # Get the length in typec
        s_len_c = ctypes.c_int(s_len)
        t_len_c = ctypes.c_int(t_len)

        # Call function
        return liblevenshtein.parallel_levenshtein(s_c, s_len_c, t_c, t_len_c)
=======
import ctypes

class Levenshtein(object):

    def __init__(self):
        # Load the library
        liblevenshtein = ctypes.CDLL('liblevenshtein.so')

        # Define function arguments types
        liblevenshtein.parallel_levenshtein.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
        liblevenshtein.sequential_levenshtein.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        # Define function return type.
        liblevenshtein.parallel_levenshtein.restype = ctypes.c_int
        liblevenshtein.sequential_levenshtein.restype = ctypes.c_int

    def _get_ctype_args(self, list_s, list_t):
        #  Get the lenth
        s_len = len(list_s)
        t_len = len(list_t)

        # Convert the values to typec
        s_c = (ctypes.c_char_p * s_len)(*list_s)
        t_c = (ctypes.c_char_p * t_len)(*list_t)

        # Get the length in typec
        s_len_c = ctypes.c_int(s_len)
        t_len_c = ctypes.c_int(t_len)

        return s_c, s_len_c, t_c, t_len_c

    def parallel_alignment(self, list_s, list_t):
        s_c, s_len_c, t_c, t_len_c = self._get_ctype_args(list_s, list_t)
        # Call function
        return self.liblevenshtein.parallel_levenshtein(s_c, s_len_c, t_c, t_len_c)

    def sequential_alignment(self, list_s, list_t):
        s_c, s_len_c, t_c, t_len_c = self._get_ctype_args(list_s, list_t)

        # Call function
        return self.liblevenshtein.sequential_levenshtein(s_c, s_len_c, t_c, t_len_c)
>>>>>>> be73cb6a5c70356aadf12876d6a9d48793e43353
