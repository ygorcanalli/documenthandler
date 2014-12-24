'''
Created on 21/03/2014

@author: fellipe
'''"ene"
import os
import csv
import xml.dom.minidom
import html.parser
import glob
from pprint import pprint
from extractors_per_dataset import write_on_file
from numpy import shape, nonzero, array, transpose, uint16, uint8
import json
import math
from numpy import zeros, nonzero
import pickle
import time
import re
import psutil
from scipy.spatial import distance

def read_content(paperi,encoding ='latin1'):
    content = ""
    with open(paperi['content_txt_path'],'r', encoding=encoding) as content_file:
        content = re.sub(r"[0-9]","",content_file.read())
    content_file.close()
    return content

def extract_co_derivative(root):
    dir_list = os.listdir(root)
    papers =[]
    for dirName in dir_list:
        file_path = os.path.join(root, dirName)
#         print(file_path)
        docs = glob.glob(file_path)
        for doc in docs:
            DOMTree = xml.dom.minidom.parse(doc)
            document = DOMTree.documentElement
            revisions_list = document.getElementsByTagName("rev")
            revisions = {}
            
#             print('reference : ',document.getAttribute('reference'))
#             print('revisions_list : ', len(revisions_list))
            
            for revisioni in revisions_list:
                section_list = revisioni.getElementsByTagName("section")
                key = revisioni.getAttribute('timestamp')
                content = ""
                for sectioni in section_list:
                    content += sectioni.firstChild.data
                revisions[key] = content
                    
#             pprint(revisions.keys())
            papers.append(revisions)
            
    return papers
      
def extract_co_derivative_to_ranking_task(root):
    labels = ['index','queries']
#     print(psutil.virtual_memory())
    papers = extract_co_derivative(root)
#     print(psutil.virtual_memory())
#     print(len(papers))
#     pprint(papers[0].keys())
#     print(min(papers[0].keys()))
    corpus_index = []
    queries = []
    
    queries_to_relevants = {}
    for paperi in papers:
        max_key = max(paperi.keys())
        query_id = len(queries)
        queries.append(paperi.get(max_key))
        queries_to_relevants[query_id] = []
#         counter = 0
        for keyi in paperi.keys():
            if (keyi != max_key):
                queries_to_relevants[query_id].append(len(corpus_index))
                corpus_index.append(paperi.get(keyi))
#                 counter += 1
#                 if counter >= 2:
#                     break
    
    target = zeros((len(queries),len(corpus_index)),dtype= uint8)
    
    for query_id in queries_to_relevants.keys():
        for index_id in queries_to_relevants.get(query_id):
            target[query_id][index_id] = 1
            
    return queries, corpus_index, target, labels 
            
if __name__ == '__main__':
    root = "/ygor/Datasets/wik-coderiv-corpus-original/en"
    queries, corpus_index, target, labels = extract_co_derivative_to_ranking_task(root)   
    print(target.shape[0],',',target.shape[1]) 
    
#         print(query_id,'x',index_id)
        
#     print(query_id,'->',len(queries_to_relevants.get(query_id)))
         
    pprint(target)
    pprint(nonzero(target))
    
    num_queries = 2
    queries_teste, corpus_index_teste, target_teste = [], [], zeros((num_queries,num_queries*9))
    
    for i in range(0,num_queries):
        queries_teste.append(queries[i])

        for j in range(0,len(target[i])):
            if (target[i][j] == 1):
                corpus_index_teste.append(corpus_index[j])
                target_teste[len(queries_teste)-1][len(corpus_index_teste)-1] = 1
    
    print(target_teste.shape[0],',',target_teste.shape[1])     
    print(target_teste)      
    
