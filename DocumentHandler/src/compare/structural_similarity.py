'''
Created on Nov 29, 2014

@author: ygor
'''

from src.model.container import Bag, Set
from src.compare.alignment import align_words, align_sentences, align_paragraphs, cos_similarity, normalized_sequential_levenshtein
import numpy as np
from pprint import pprint


def bag_of_words(s_content, t_content):
    return align_words(s_content, t_content, cos_similarity)

def list_of_words(s_content, t_content):
    return align_words(s_content, t_content, normalized_sequential_levenshtein)

def bag_of_sentences(s_content, t_content):
    return align_sentences(s_content, t_content, cos_similarity)

def list_of_sentences(s_content, t_content):
    return align_sentences(s_content, t_content, normalized_sequential_levenshtein)

def bag_of_paragraphs(s_content, t_content, granule_alignment_funcion, threshold):
    if granule_alignment_funcion == None and threshold == None:
        return align_paragraphs(s_content, t_content, cos_similarity)
    else:
        # Get the paragraphs
        s_itens = s_content.get_paragraphs()
        t_itens = t_content.get_paragraphs()
        
        s_bag = s_itens.to_bag()
        t_bag = t_itens.to_bag()
        
        s_set = s_itens.to_set()
        t_set = t_itens.to_set()
        
        keys = s_set.union(t_set)
        
        array_s = np.zeros(len(keys))
        array_t = np.zeros(len(keys))
        
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
                        if s_similarity_bucket.has_key(s_item):
                            # make union
                            s_similarity_bucket[s_item].add(t_item)
                        else: 
                            # initialize bucket
                            s_similarity_bucket[s_item] = Set([t_item])
                    
                        if t_similarity_bucket.has_key(t_item):
                            # make union
                            t_similarity_bucket[t_item].add(s_item)
                        else:
                            # initialize bucket
                            t_similarity_bucket[t_item] = Set([s_item]) 
                            
        
        
        i = 0
        for k in keys:
            if s_bag.has_key(k):
                array_s[i] = s_bag.get(k)
            else:
                if t_similarity_bucket.has_key(k):
                    for b in t_similarity_bucket[k]:
                        array_s[i] += s_bag.get(b)
            if t_bag.has_key(k):
                array_t[i] = t_bag.get(k)
            else:       
                if s_similarity_bucket.has_key(k):
                    for b in s_similarity_bucket[k]:
                        array_t[i] += t_bag.get(b)
            i = i + 1
                               
        dotted = np.dot(array_s, np.transpose(array_t))
        norms = np.linalg.norm(array_s) * np.linalg.norm(array_t)

        return dotted/norms

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

