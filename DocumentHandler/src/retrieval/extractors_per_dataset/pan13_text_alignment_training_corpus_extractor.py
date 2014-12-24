'''
Created on 21/03/2014

@author: fellipe
'''
import os
import csv
import xml.dom.minidom
import html.parser
import glob
from pprint import pprint
from ufrrj.extractors_per_dataset import write_on_file
from numpy import shape, nonzero, array
import json
import math
from numpy import zeros
import pickle
import time
import re

def read_content(pathi,encoding ='latin1'):
    content = ""
    with open(pathi,'r', encoding=encoding) as content_file:
        content = re.sub(r"[0-9]","",content_file.read())
    content_file.close()
    return content

def extract_pan_2013_text_alignment(root):
    labels = [
#               '01-no-plagiarism',
            '02-no-obfuscation','03-random-obfuscation','04-translation-obfuscation','05-summary-obfuscation'
              ]

    queries = []
    corpus_index = []
    inverted_index = {}

    folder_path = os.path.join(root,'src')
    for filenamei in os.listdir(folder_path):
        file_path = os.path.join(folder_path,filenamei)
        inverted_index[filenamei] = len(corpus_index)
        corpus_index.append(read_content(file_path))
        
        
    folder_path = os.path.join(root,'susp')
    for filenamei in os.listdir(folder_path):
        file_path = os.path.join(folder_path,filenamei)
        inverted_index[filenamei] = len(queries)
        queries.append(read_content(file_path))
                
    target = zeros((len(queries),len(corpus_index)))
    
    for folderi in labels:
        with open(os.path.join(root,folderi,'pairs'),'r') as content_file:
            content = content_file.read()
            content_file.close()

#             print(folderi,'lines:',len(content.split('\n')))

            for linei in content.split('\n')[0:-1]:
                temp = linei.split(' ')
#                 print(temp)
                i = inverted_index[temp[0]]
                j = inverted_index[temp[1]]
                target[i][j] = 1
#                 print(i,j)
#                 print(queries[i],corpus_index[j])
                
#     print(target.shape)

    return queries, corpus_index, target, ['index','queries']
        

#     queries = []
#     corpus_index = []
#     labels = ['index','queries']
#     path_to_index = {'index':{},'queries':{}}
#     target = zeros((len(papers['suspicious-document']),len(papers['source-document'])))
    
    
#     folder_path = os.path.join(root,filenamesi[0])
#         for i in range(1,len(filenamesi)):
#             path = os.path.join(folder_path,filenamesi[i])
# #             print('->',path)
#             
#             dir_list = os.listdir(path)
# 
#     
#     for doc_keyi in doc_type.keys():
#         temp = doc_type.get(doc_keyi)[1]%(2)
#         print(temp)
        
    
#     return corpus, target, labels


    
if __name__ == '__main__':
     
    root = "/media/dados/Colecoes de Dados/PAN/Text alignment/pan13-text-alignment-training-corpus-2013-01-21"
    
    queries, corpus_index, target, labels = extract_pan_2013_text_alignment(root)
#     pprint(queries)get
#     pprint(corpus_index)
#     print(queries, corpus_index, target, labels)
#     
#     i = 0.4
#     queries, corpus_index, target, labels = extract_pan_2011_external_detection_ranking_task(root,i)
#     
#     while ( i < 1.0):
#         queries, corpus_index, target, labels = extract_pan_2011_external_detection_ranking_task(root,i)
#         i += 0.1
#         
#     #extraction all the dataset!     
#     queries, corpus_index, target, labels = extract_pan_2011_external_detection_ranking_task(root)
