"""
Created on Apr 30, 2014

@author: ygor
"""

from .core import liblevenshtein
import numpy as np


def normalized_sequential_levenshtein(list_s, list_t, *args, **kwargs):
    return similarity(len(list_s), len(list_t), sequential_levenshtein(list_s, list_t, *args, **kwargs))

def parallel_levenshtein(list_s, list_t, *args, **kwargs):
    s_len = len(list_s)
    t_len = len(list_t)
    equality_dict = kwargs.get('equality_dict', None);
    set_s = kwargs.get('set_s', None);
    set_t = kwargs.get('set_t', None);

    # Call function
    if(equality_dict != None):
        s_set_len = len(set_s)
        t_set_len = len(set_t)

        return liblevenshtein.parallel_levenshtein(list_s, s_len, list_t, t_len, equality_dict, set_s, s_set_len, set_t, t_set_len)	

    return liblevenshtein.parallel_levenshtein(list_s, s_len, list_t, t_len)


def sequential_levenshtein(list_s, list_t, *args, **kwargs):
    s_len = len(list_s)
    t_len = len(list_t)
    equality_dict = kwargs.get('equality_dict', None);
    set_s = kwargs.get('set_s', None);
    set_t = kwargs.get('set_t', None);

    # Call function
    if(equality_dict != None):
        s_set_len = len(set_s)
        t_set_len = len(set_t)

        return liblevenshtein.sequential_levenshtein(list_s, s_len, list_t, t_len, equality_dict, set_s, s_set_len, set_t, t_set_len)	

    return liblevenshtein.sequential_levenshtein(list_s, s_len, list_t, t_len)


def cos_similarity(list_s, list_t):
    bag_s = list_s.to_bag()
    bag_t = list_t.to_bag()
    
    set_s = list_s.to_set()
    set_t = list_t.to_set()
    
    keys = set_s.union(set_t)
    
    array_s = np.zeros(len(keys))
    array_t = np.zeros(len(keys))
    
    rank = 0
    
    for k in keys:
        if k in bag_s:
            array_s[rank] = bag_s.get(k)
        if k in bag_t:
            array_t[rank] = bag_t.get(k)
        rank = rank + 1
    
    dotted = np.dot(array_s, np.transpose(array_t))
    norms = np.linalg.norm(array_s) * np.linalg.norm(array_t)

    return dotted/norms
    
def jaccard_similarity(list_s, list_t):
    set_s = list_s.to_set()
    set_t = list_t.to_set()
    
    len_insersection = len(set_s.intersection(set_t))
    len_union = len(set_s.union(set_t))
     
    dis = float(len_insersection) / float(len_union)
    
    return dis


def dissimilarity(s_len, t_len, distance):
    return float(distance)/max(s_len, t_len)


def similarity(s_len, t_len, distance):
    return 1 - dissimilarity(s_len, t_len, distance)

