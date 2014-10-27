# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 23:59:57 2014

@author: ygor
"""
#%%
from src.model import document_from_pkl
from src.model import container
from src.model import content
from src.compare.distance import *

#%%
s = document_from_pkl("../instances/loren/pickled/02.pkl")
t = document_from_pkl("../instances/loren/pickled/03.pkl")

s_words_hash = s.get_words().to_hash_list()
t_words_hash = t.get_words().to_hash_list()
#%%
print "Cosine similarity: %f" % cos_similarity(s_words_hash, t_words_hash)

print "Jaccard similarity: %f" % jaccard_similarity(s_words_hash, t_words_hash)

#%%