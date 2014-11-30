'''
Created on Nov 29, 2014

@author: ygor
'''

from alignment import *
from distance import normalized_sequential_levenshtein, cos_similarity

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
        
        i=0
        j=0
    
        for s_paragraphsi in s_paragraphs_set:
            for t_paragraphsi in t_paragraphs_set:
    
                #print s_paragraphsi
                #print t_paragraphsi
                # Align the words of paragraphs
                simil = granule_alignment_funcion(s_paragraphsi, t_paragraphsi)
                #print "Simil[%d][%d]=%0.4f\n" % (i,j,simil)
                # Verify equality by threshold
                if(simil >= threshold):
                    equality = 1
                else:
                    equality = 0
    
                #  results accumulation
                paragraphs_equality[(s_paragraphsi.__hash__(),t_paragraphsi.__hash__())] = equality
    
        return normalized_sequential_levenshtein(s_paragraphs.to_hash_list(), t_paragraphs.to_hash_list(), equality_dict=paragraphs_equality, set_s=s_paragraphs_set.to_hash_list(), set_t=t_paragraphs_set.to_hash_list())
        

