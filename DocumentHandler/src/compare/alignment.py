"""
Created on Jun 20, 2014

@author: ygor
"""

def align_paragraphs(s_content, t_content, alignment_function):
    s_words = s_content.get_paragraphs()
    t_words = t_content.get_paragraphs()

    # Call function
    return  alignment_function(s_words.to_hash_list(), t_words.to_hash_list())
    

def align_sentences(s_content, t_content, alignment_function):
    s_words = s_content.get_sentences()
    t_words = t_content.get_sentences()

    # Call function
    return  alignment_function(s_words.to_hash_list(), t_words.to_hash_list())

def align_words(s_content, t_content, alignment_function):
    s_words = s_content.get_words()
    t_words = t_content.get_words()

    # Call function
    return  alignment_function(s_words.to_hash_list(), t_words.to_hash_list())

def align_chars(s_content, t_content, alignment_function):
    s_chars = s_content.get_chars()
    t_chars = t_content.get_chars()

    # Call function
    return alignment_function(s_chars.to_hash_list(), t_chars.to_hash_list())
