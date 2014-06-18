"""
Created on Apr 30, 2014

@author: ygor
"""
from core import liblevenshtein

class Levenshtein(object):

    def parallel_alignment(self, list_s, list_t):
        s_len = len(list_s)
        t_len = len(list_t)

        # Call function
        return liblevenshtein.parallel_levenshtein(list_s, s_len, list_t, t_len)

    def sequential_alignment(self, list_s, list_t):
        s_len = len(list_s)
        t_len = len(list_t)

        # Call function
        return liblevenshtein.sequential_levenshtein(list_s, s_len, list_t, t_len)
