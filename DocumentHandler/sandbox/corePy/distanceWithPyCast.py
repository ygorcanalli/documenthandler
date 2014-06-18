"""
Created on Apr 30, 2014

@author: ygor
"""
import ctypes

class Levenshtein(object):

    def __init__(self):
        # Load the library
        self.liblevenshtein = ctypes.CDLL('compare/corePy/liblevenshtein.so')

        # Define function arguments types
        self.liblevenshtein.parallel_levenshtein.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
        self.liblevenshtein.sequential_levenshtein.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
        # Define function return type.
        self.liblevenshtein.parallel_levenshtein.restype = ctypes.c_ushort
        self.liblevenshtein.sequential_levenshtein.restype = ctypes.c_ushort

    def _get_ctype_args(self, list_s, list_t):
        #  Get the lenth
        s_len = len(list_s)
        t_len = len(list_t)

        # Convert the values to typec
        s_c = (ctypes.c_void_p * s_len)(*list_s)
        t_c = (ctypes.c_void_p * t_len)(*list_t)

        # Get the length in typec
        s_len_c = ctypes.c_uint(s_len)
        t_len_c = ctypes.c_uint(t_len)

        return s_c, s_len_c, t_c, t_len_c

    def parallel_alignment(self, list_s, list_t):
        s_c, s_len_c, t_c, t_len_c = self._get_ctype_args(list_s, list_t)
        # Call function
        return self.liblevenshtein.parallel_levenshtein(s_c, s_len_c, t_c, t_len_c)

    def sequential_alignment(self, list_s, list_t):
        s_c, s_len_c, t_c, t_len_c = self._get_ctype_args(list_s, list_t)

        # Call function
        return self.liblevenshtein.sequential_levenshtein(s_c, s_len_c, t_c, t_len_c)
