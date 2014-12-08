'''
Created on Nov 29, 2014

@author: ygor
'''

from alignment import *
from pprint import pprint


def bag_of_words(s_content, t_content):
    return align_words(s_content, t_content, cos_similarity)

def list_of_words(s_content, t_content):
    return align_words(s_content, t_content, normalized_sequential_levenshtein)

def bag_of_sentences(s_content, t_content):
    return align_sentences(s_content, t_content, cos_similarity)

def list_of_sentences(s_content, t_content):
    return align_sentences(s_content, t_content, normalized_sequential_levenshtein)

def bag_of_paragraphs(s_content, t_content):
    return align_sentences(s_content, t_content, cos_similarity)

def list_of_paragraphs(s_content, t_content, granule_alignment_funcion, threshold):
    if granule_alignment_funcion == None and threshold == None:
        return align_paragraphs(s_content, t_content, normalized_sequential_levenshtein)
    else:
        # Get the paragraphs
        s_itens = s_content.get_paragraphs()
        t_itens = t_content.get_paragraphs()
    
        s_itens_set = s_itens.to_set()
        t_itens_set = t_itens.to_set()

    
        itens_equality = {}

    
        for s_item in s_itens_set:
            for t_item in t_itens_set:
                
                s_hash = s_item.__hash__()
                t_hash = t_item.__hash__()
                                   
                # Align the words of paragraphs   
                if (s_hash != t_hash):
                    simil = granule_alignment_funcion(s_item, t_item)
                    
                    # Verify equality by threshold and accumule
                    itens_equality[(s_hash,t_hash)] = (simil >= threshold)
                else:
                    itens_equality[(s_hash,t_hash)] = 1
                     
        return normalized_sequential_levenshtein(s_itens.to_hash_list(), t_itens.to_hash_list(), equality_dict=itens_equality, set_s=s_itens_set.to_hash_list(), set_t=t_itens_set.to_hash_list())       

