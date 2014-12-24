'''
Created on Nov 29, 2014

@author: ygor
'''

from model.container import Set
from compare.alignment import align_words, align_sentences, align_paragraphs
from compare.distance import cos_similarity, normalized_sequential_levenshtein
import numpy as np

def bag_of_words(s_content, t_content,  *args, **kwargs):
    return align_words(s_content, t_content, cos_similarity)

def list_of_words(s_content, t_content,  *args, **kwargs):
    return align_words(s_content, t_content, normalized_sequential_levenshtein)

def bag_of_sentences(s_content, t_content,  *args, **kwargs):
    
    granule_alignment_funcion = kwargs.get('granule_alignment_funcion', None)
    threshold = kwargs.get('threshold', None)
    if granule_alignment_funcion == None and threshold == None:
        return align_sentences(s_content, t_content, cos_similarity)
    else:
        # Get the sentences
        s_itens = s_content.get_sentences()
        t_itens = t_content.get_sentences()
        
        return _hierarchical_cossine_similarity(s_itens, t_itens, granule_alignment_funcion, threshold)

def list_of_sentences(s_content, t_content,  *args, **kwargs):
    
    granule_alignment_funcion = kwargs.get('granule_alignment_funcion', None)
    threshold = kwargs.get('threshold', None)
    
    if granule_alignment_funcion == None and threshold == None:
        return align_sentences(s_content, t_content, normalized_sequential_levenshtein)
    else:
        # Get the sentences
        s_itens = s_content.get_sentences()
        t_itens = t_content.get_sentences()
        
        return _hierarchical_levenshtein(s_itens, t_itens, granule_alignment_funcion, threshold)

def bag_of_paragraphs(s_content, t_content,  *args, **kwargs):
    
    granule_alignment_funcion = kwargs.get('granule_alignment_funcion', None)
    threshold = kwargs.get('threshold', None)
    
    if granule_alignment_funcion == None and threshold == None:
        return align_paragraphs(s_content, t_content, cos_similarity)
    else:
        # Get the paragraphs
        s_itens = s_content.get_paragraphs()
        t_itens = t_content.get_paragraphs()
        
        return _hierarchical_cossine_similarity(s_itens, t_itens, granule_alignment_funcion, threshold)

def list_of_paragraphs(s_content, t_content,  *args, **kwargs):
    
    granule_alignment_funcion = kwargs.get('granule_alignment_funcion', None)
    threshold = kwargs.get('threshold', None)
    
    if granule_alignment_funcion == None and threshold == None:
        return align_paragraphs(s_content, t_content, normalized_sequential_levenshtein)
    else:
        # Get the paragraphs
        s_itens = s_content.get_paragraphs()
        t_itens = t_content.get_paragraphs()
        
        return _hierarchical_levenshtein(s_itens, t_itens, granule_alignment_funcion, threshold)
    

def _hierarchical_cossine_similarity(s_itens, t_itens, granule_alignment_funcion, threshold):
    s_bag = s_itens.to_bag()
    t_bag = t_itens.to_bag()
    
    s_set = s_itens.to_set()
    t_set = t_itens.to_set()
    
    # get all different itens in s and t
    keys = s_set.union(t_set)
    
    # create zeros arrays
    array_s = np.zeros(len(keys))
    array_t = np.zeros(len(keys))
    
    # create similarity buckets for store the remilarity relationships
    s_similarity_bucket = {}
    t_similarity_bucket = {}
    
    for s_item in s_bag:            
        for t_item in t_bag: 
            
            # if itens are differents, measure similarity
            if (s_item != t_item):
                
                # similarity measurement
                simil = granule_alignment_funcion(s_item, t_item)
                      
                # Verify equality by threshold and build the buckets
                if simil >= threshold:
                    if s_item in s_similarity_bucket:
                        # make union
                        s_similarity_bucket[s_item].add(t_item)
                    else: 
                        # initialize bucket
                        s_similarity_bucket[s_item] = Set([t_item])
                
                    if t_item in t_similarity_bucket:
                        # make union
                        t_similarity_bucket[t_item].add(s_item)
                    else:
                        # initialize bucket
                        t_similarity_bucket[t_item] = Set([s_item]) 
                        
    i = 0
    
    # build the arrays to cossine sinilarity
    for k in keys:
        # if the item is in document s, counts the normal occurrences
        if k in s_bag:
            array_s[i] = s_bag.get(k)
        # if the item is not in s, accumulate the occurrence of itens in s that are similar to that item in t (that is, the documents in t_bucket for the item) 
        else:
            if k in t_similarity_bucket:
                for b in t_similarity_bucket[k]:
                    array_s[i] += s_bag.get(b)
                    
        # if the item is in document t, counts the normal occurrences
        if k in t_bag:
            array_t[i] = t_bag.get(k)
        # if the item is not in t, accumulate the occurrence of itens in t that are similar to that item in s (that is, the documents in s_bucket for the item) 
        else:       
            if k in s_similarity_bucket:
                for b in s_similarity_bucket[k]:
                    array_t[i] += t_bag.get(b)
        i = i + 1
                           
    dotted = np.dot(array_s, np.transpose(array_t))
    norms = np.linalg.norm(array_s) * np.linalg.norm(array_t)
    
    return dotted/norms
    
def _hierarchical_levenshtein(s_itens, t_itens, granule_alignment_funcion, threshold):
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