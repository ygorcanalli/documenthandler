"""
Created on Jun 20, 2014

@author: ygor
"""

from distance import *

def align_words(s_content, t_content, alignment_function):
    s_words = s_content.get_words()
    t_words = t_content.get_words()

    s_len = len(s_words)
    t_len = len(t_words)

    # Call function
    distance = alignment_function(s_words.to_hash_list(), t_words.to_hash_list())

    return similarity(s_len, t_len, distance)