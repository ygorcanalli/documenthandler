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
        s_paragraphs = s_content.get_paragraphs()
        t_paragraphs = t_content.get_paragraphs()
    
        s_paragraphs_set = s_paragraphs.to_set()
        t_paragraphs_set = t_paragraphs.to_set()

    
        paragraphs_equality = {}

    
        for s_item in s_paragraphs_set:
            for t_item in t_paragraphs_set:
                
                s_hash = s_item.__hash__()
                t_hash = t_item.__hash__()
                                   
                # Align the words of paragraphs   
                if (s_item != t_item):
                    simil = granule_alignment_funcion(s_item, t_item)
                    
                    # Verify equality by threshold
                    #  results accumulation
                    paragraphs_equality[(s_hash,t_hash)] = (simil >= threshold)
                else:
                    paragraphs_equality[(s_hash,t_hash)] = 1
                    
                #print s_item
                #print t_item
                #print str(simil) + "\n"
                     
        return normalized_sequential_levenshtein(s_paragraphs.to_hash_list(), t_paragraphs.to_hash_list(), equality_dict=paragraphs_equality, set_s=s_paragraphs_set.to_hash_list(), set_t=t_paragraphs_set.to_hash_list())
        
 
        

