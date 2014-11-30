"""
Created on Jun 20, 2014

@author: ygor
"""

from distance import *

def align_paragraphs(s_content, t_content, alignment_function):
    s_words = s_content.get_paragraphs()
    t_words = t_content.get_paragraphs()

    s_len = len(s_words)
    t_len = len(t_words)

    # Call function
    return  alignment_function(s_words.to_hash_list(), t_words.to_hash_list())

    

def align_sentences(s_content, t_content, alignment_function):
    s_words = s_content.get_sentences()
    t_words = t_content.get_sentences()

    s_len = len(s_words)
    t_len = len(t_words)

    # Call function
    return  alignment_function(s_words.to_hash_list(), t_words.to_hash_list())

def align_words(s_content, t_content, alignment_function):
    s_words = s_content.get_words()
    t_words = t_content.get_words()

    s_len = len(s_words)
    t_len = len(t_words)

    # Call function
    return  alignment_function(s_words.to_hash_list(), t_words.to_hash_list())

def align_chars(s_content, t_content, alignment_function):
    s_chars = s_content.get_chars()
    t_chars = t_content.get_chars()

    s_len = len(s_chars)
    t_len = len(t_chars)

    # Call function
    return alignment_function(s_chars.to_hash_list(), t_chars.to_hash_list())


def align_paragraph_by_words(s_content, t_content, treshold, alignment_function):

    # Get the paragraphs
    s_paragraphs = s_content.get_paragraphs()
    t_paragraphs = t_content.get_paragraphs()

    s_paragraphs_set = s_paragraphs.to_set()
    t_paragraphs_set = t_paragraphs.to_set()

    paragraphs_equality = {}

    s_len = len(s_paragraphs)
    t_len = len(t_paragraphs)

    for s_paragraphsi in s_paragraphs_set:
        for t_paragraphsi in t_paragraphs_set:

            # Align the words of paragraphs
            simil = align_words(s_paragraphsi, t_paragraphsi, alignment_function)

            # Verify equality by treshold
            if(simil >= treshold):
                equality = 1
            else:
                equality = 0

            #  results accumulation
            paragraphs_equality[(s_paragraphsi.__hash__(),t_paragraphsi.__hash__())] = equality

    distance = alignment_function(s_paragraphs.to_hash_list(), t_paragraphs.to_hash_list(), equality_dict=paragraphs_equality, set_s=s_paragraphs_set.to_hash_list(), set_t=t_paragraphs_set.to_hash_list())

    return similarity(s_len, t_len, distance)
