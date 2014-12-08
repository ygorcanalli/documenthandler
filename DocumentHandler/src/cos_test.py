# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 23:59:57 2014

@author: ygor
"""
#%%
from src.model import document_from_pkl
from src.model import container
from src.model import content
#from src.compare.distance import *
from src.compare.structural_similarity import *

#%%
t = document_from_pkl("../instances/hierarchical_test/pickled/genesis1.pkl")
s = document_from_pkl("../instances/hierarchical_test/pickled/copy-of-genesis1.pkl")

s_words_hash = s.get_words().to_hash_list()
t_words_hash = t.get_words().to_hash_list()

#print list_of_paragraphs(s, t, threshold=None, granule_alignment_funcion=None)
#print list_of_paragraphs(s, t, threshold=0.8, granule_alignment_funcion=bag_of_words)
print list_of_paragraphs(s, t, threshold=0.8, granule_alignment_funcion=list_of_words)
#%%
#print "Cosine similarity: %f" % cos_similarity(s_words_hash, t_words_hash)

#print "Jaccard similarity: %f" % jaccard_similarity(s_words_hash, t_words_hash)

#%%