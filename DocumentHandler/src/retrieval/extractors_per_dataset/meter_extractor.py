'''
Created on 21/03/2014

@author: fellipe
'''
import os
import csv
import xml.dom.minidom
import html.parser
from pprint import pprint
from numpy import shape, nonzero, zeros, float128
import re
from sklearn import metrics

def extract_meter(root, content_type = 'rawtexts'):
    filenames_list =[
                ('courts','PA_court_files.txt'),
                ('showbiz','PA_showbiz_files.txt')
        ]
    content_type_extensions = {'rawtexts': '.txt','annotated':'.sgml'}
    
#     root = "/media/dados/Colecoes de Dados/meter_corpus"
    
    papers = {}
    
    for filenamesi in filenames_list:
        folder_path = os.path.join(root,'file_index',filenamesi[0])
        pa_file = open(os.path.join(folder_path,filenamesi[1]), 'r')
        
        for linei in pa_file.readlines():
            linei = linei.replace('\n','')
            features = linei.split('/')
            paperi = {'path':linei, 'newspaper':features[2], 'domain':features[4], 'date':features[5], 'catchline':features[6], 'filename':features[7],'classification':'source'}
#             pprint(paperi)
# 
#             exit(0)
            with open(root.replace('/meter_corpus', linei),'r', encoding ='latin1') as content_file:
#                 content = content_file.read()
                content = re.sub(r"[0-9]","",content_file.read())
                paperi['content'] = content
                
            papers[linei] = paperi
        
        print("folder_path:%s"%folder_path)
        
        for classification_file in ('partially_derived', 'wholly_derived', 'non_derived'):
            pa_file = open(os.path.join(folder_path,classification_file+'.txt'), 'r')
            for linei in pa_file.readlines():
                linei = linei.replace('\n','').replace('rawtexts',content_type).replace('.txt',content_type_extensions[content_type])
                features = linei.split('/')
                #meter_corpus/newspapers/rawtexts/showbiz/27.09.99/beegees/beegees119_times.txt
                newspaper_name = features[6].split('_')[1].replace('.txt','') 
                paperi = {'path':linei, 'newspaper':newspaper_name, 'domain':features[3], 'date':features[4], 'catchline':features[5], 'filename':features[6],'classification':classification_file}
    
#                 print(classification_file)
#                 print(root.replace('meter_corpus', linei))
#                 exit(0) 
                with open(root.replace('meter_corpus', linei),'r', encoding ='latin1') as content_file:
#                     content = content_file.read()
                    content = re.sub(r"[0-9]","",content_file.read())
                    paperi['content'] = content
                    
                papers[linei] = paperi
    return papers


def extract_meter_to_corpus_target_labels(path):
    papers = extract_meter(path)
    corpus = []
    target = []
    labels = [] 
    
    for keyi in papers:
#         print(keyi)
        class_name = papers[keyi]["domain"] +"_"+ papers[keyi]["classification"]
        if class_name in labels:
            class_index = labels.index(class_name, )
        else:
            class_index = len(labels)
            labels.append(class_name)
        target.append(class_index)
        corpus.append(papers[keyi]['content'])
        
#         print(X)
#         print(target)
#         print(labels)
#         exit()    

          
    return corpus, target, labels

def extract_meter_to_corpus_ranking_task(path):
    papers = extract_meter(path)
    queries = []
    corpus_index = []
    
    labels = ['index','queries']
    path_to_index = {'index':{},'queries':{}} 
    
    for keyi in papers:
        
#         if (papers[keyi]['classification'] == 'non_derived'):
#             continue
#             print(papers[keyi])
#             exit()
            
        if (papers[keyi]["newspaper"] == 'PA'):
            indexi = len(corpus_index) 
            corpus_index.append(papers[keyi]['content'])
            doc_type = 'index'
        else:
            indexi = len(queries)  
            queries.append(papers[keyi]['content'])
            doc_type = 'queries'
            
        path_to_index[doc_type][keyi] = indexi
#     print(path_to_index)
#     print(len(path_to_index['index']),len(path_to_index['queries']))
#     print(shape(queries))
#     print(shape(corpus_index))
    
    target = zeros((len(queries),len(corpus_index))) #[[0]*len(corpus_index)]*len(queries)
#     print(shape(target))
    
    for query_keyi in path_to_index['queries']:
        relevant_pathi = query_keyi.replace(papers[query_keyi]["filename"],'').replace('newspapers','PA')
        query_indexi = path_to_index['queries'][query_keyi]
        count = 0
        for index_keyi in path_to_index['index']:
            if relevant_pathi in index_keyi:
#                 print('match : ', query_keyi, "=>",relevant_pathi,' x ', index_keyi)                
                relevant_indexi = path_to_index['index'][index_keyi]
                target[query_indexi][relevant_indexi] = 1
                count += 1
#         print(nonzero(target[query_indexi]))
#         print("%s = %d != %s ? total(%s)"%(query_keyi,count,shape(nonzero(target[query_indexi])),shape(target[query_indexi])))
            
#     exit(0)
    return queries, corpus_index, target, labels

def minha_metrica_exemplo(texto1,texto2):
    '''
        metrica de exemplo muito inocente : diferenca do tamanho e a dessimilaridade 
    '''
    #diferenca do tamanho e a dessimilaridade
    len_diff = abs(len(texto1)-len(texto2))
    # normalizando pelo maior tamanho
    len_diff /= max(len(texto1),len(texto2))
    # transformando em similaridade
    len_diff = 1 - len_diff
    
    return len_diff


if __name__ == '__main__':
    root = "/media/dados/Colecoes de Dados/meter_corpus"
    
    queries, corpus_index, target, labels = extract_meter_to_corpus_ranking_task(root)   
    print(target.shape[0],',',target.shape[1]) 
    pprint(target)
    pprint(nonzero(target))
    '''
     queries = lista das consultas (texto de cada notícia Wholly e Part. derived)
     corpus_index = lista dos documentos que serão ordenados (texto da P.A.)
     target = quais documentos deveriam ser retornados pelo "mecanismo de busca" para cada consulta (os documentos relevante, isto e dos quais a consulta derivou, da consulta)
     target[0][0] = 1 significa que para a consulta 0 o documento do indice 0 é relevante
     target[0][1] = 0 significa que para a consulta 0 o documento do indice 1 não é relevante
     * usamos target para calcular precision, recall, accuracy entre outros 
    '''
    
    for qi in queries:
        ranking = []
        for j in range(0,len(corpus_index)):
            dj = corpus_index[j]
            similaridade = minha_metrica_exemplo(qi,dj)
            ranking.append((j,similaridade))
            
        ranking.sort(key=lambda tup: tup[1],reverse=True)
        print('ranking da consulta qi(id no corpus_index, similaridade)')
        print(ranking)
        print('------------------')
        
        #comparar ranking X target para calcular a precision X recall de cada consulta
        
        
    #objetivo final é gerar a curva de precision recall de 11 níveis, precision at k (p@k) e recall at k (r@k) para as consultas como um todo (tem no livro modern information retrieval)
    
    
        
    
