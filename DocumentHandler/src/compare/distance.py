"""
Created on Apr 30, 2014

@author: ygor
"""

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
