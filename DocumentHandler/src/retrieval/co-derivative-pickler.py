import os
import json
import numpy as np
from co_derivative_extractor import extract_co_derivative_to_ranking_task

def extract_dev_set(queries,corpus_index,target,num_queries = None):
    if (num_queries == None):
        num_queries = len(queries)
        
    queries_teste, corpus_index_teste, target_teste = [], [], np.zeros((num_queries,num_queries*9))
    
    for i in range(0,num_queries):
        queries_teste.append(queries[i])

        for j in range(0,len(target[i])):
            if (target[i][j] == 1):
                corpus_index_teste.append(corpus_index[j])
                target_teste[len(queries_teste)-1][len(corpus_index_teste)-1] = 1
    
    print('dev set:')
    print("#queries:",target_teste.shape[0],",#doc_index:",target_teste.shape[1])
    
    return queries_teste, corpus_index_teste, target_teste

if __name__ == '__main__':
    #do dataset original (sem extracoes)
    #root = "/media/dados/Colecoes de Dados/PAN/co-derivative/wik-coderiv-corpus-original/en"
    root = "/home/ygor/Datasets/wik-coderiv-corpus-original/en"
    
    queries, corpus_index, target, labels = extract_co_derivative_to_ranking_task(root)   
    print("#queries:",target.shape[0],",#doc_index:",target.shape[1])
    
    queries_root = os.path.join(root, "..", "documenthandler", "en", "queries")
    corpus_root = os.path.join(root, "..", "documenthandler", "en", "corpus_index") 
    
    #Try to create the directories
    try:
        os.makedirs(os.path.join(queries_root, "plain"))
    except FileExistsError as e:
        print(e)
    
    try:
        os.makedirs(os.path.join(queries_root, "pickled"))
    except FileExistsError as e:
        print(e)
    
    try:
        os.makedirs(os.path.join(corpus_root, "plain"))
    except FileExistsError as e:
        print(e)
    
    try:
        os.makedirs(os.path.join(corpus_root, "pickled"))
    except FileExistsError as e:
        print(e)    
        
    #Extract articles to txt files    
    for i in range(0, len(queries)):
        query = queries[i]
        query_file = open(os.path.join(queries_root, "plain", "%d.txt" % i), "w")
        query_file.write(query)
        query_file.close()
    
    for i in range(0, len(corpus_index)):
        document = corpus_index[i]
        document_file = open(os.path.join(corpus_root, "plain", "%d.txt" % i), "w")
        document_file.write(document)
        document_file.close()
        
    json.dump(target.tolist(), open(os.path.join(root, "..", "documenthandler", "en", "target.json"), "w"))
        
    