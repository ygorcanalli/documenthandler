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

print "List of paragraphs: ", list_of_paragraphs(s, t, threshold=None, granule_alignment_funcion=None)
print "List of paragraphs|bag of words: ", list_of_paragraphs(s, t, threshold=0.8, granule_alignment_funcion=bag_of_words)
print "List of paragraphs|list of words: ", list_of_paragraphs(s, t, threshold=0.8, granule_alignment_funcion=list_of_words)
print "Bag of paragraphs: ", bag_of_paragraphs(s, t, threshold=None, granule_alignment_funcion=None)
print "Bag of paragraphs|bag of words: ", bag_of_paragraphs(s, t, threshold=0.8, granule_alignment_funcion=bag_of_words)
print "Bag of paragraphs|list of words: ", bag_of_paragraphs(s, t, threshold=0.8, granule_alignment_funcion=list_of_words)
