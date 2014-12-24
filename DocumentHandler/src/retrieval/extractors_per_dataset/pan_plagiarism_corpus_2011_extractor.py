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
from ufrrj.extractors_per_dataset import write_on_file
from numpy import shape, nonzero, array, transpose, uint16, uint8
import json
import math
from numpy import zeros
import pickle
import time
import re

def read_content(paperi,encoding ='latin1'):
    content = ""
    with open(paperi['content_txt_path'],'r', encoding=encoding) as content_file:
        content = re.sub(r"[0-9]","",content_file.read())
    content_file.close()
    return content

def extract_pan_2011(root):
    filenames_list =[
                ('external-detection-corpus', 'source-document', 'suspicious-document'),
                ('intrinsic-detection-corpus','suspicious-document')
    ]
    
    papers = {'external-detection-corpus':{'source-document':[], 'suspicious-document':[]}, 
            'intrinsic-detection-corpus':{'suspicious-document':[]}
    }
     
    for filenamesi in filenames_list:
        folder_path = os.path.join(root,filenamesi[0])
        for i in range(1,len(filenamesi)):
            path = os.path.join(folder_path,filenamesi[i])
#             print('->',path)
            
            dir_list = os.listdir(path)
            for dirName in dir_list:
                file_pattern = os.path.join(path, dirName, filenamesi[i]+'?????.xml')
#                 print(file_pattern)
                docs = glob.glob(file_pattern)
                for doc in docs:
#                     print('->',doc)
                    DOMTree = xml.dom.minidom.parse(doc)
                    document = DOMTree.documentElement

                    paperi = {'reference':document.getAttribute('reference'),'task':filenamesi[0], 'class':filenamesi[i], 'features':[]}
                    papers.get(paperi.get('task')).get(paperi.get('class')).append(paperi)
                    
                    feature_list = document.getElementsByTagName("feature")
                    for fi in feature_list:
                        featurei = {}
                        for featurei_attrj in fi.attributes.keys():
#                             print(featurei_attrj,fi.getAttribute(featurei_attrj))
                            featurei[featurei_attrj] = fi.getAttribute(featurei_attrj)
#                           if featurei_attrj == 'source_reference':
#                             featurei['source_reference_txt_path'] = os.path.join(path, 'source-document',dirName, featurei['source_reference'])
#                             print(paperi['reference'],featurei['source_reference'],featurei['source_reference_txt_path'])                            
#                             exit()
                          
#                         pprint(featurei)
#                         if  featurei.get('lang')=='en':
#                             paperi.get('features').append(featurei)
                        
                        paperi.get('features').append(featurei)
                        
                    txt_path = os.path.join(path, dirName, document.getAttribute('reference'))
                    paperi['content_txt_path'] = txt_path
#                     paperi['content'] = read_content(paperi)
#                 break
    return papers

'''
    split extract_pan_2011 extracted dataset in dev_set and test_set 
'''
def split_dataset(queries, target, dev_set_size):
    if (dev_set_size <=0 or dev_set_size >= 1):
            raise Exception("dev_set_size must between 0 and 1 !")
    else:
        threshold = math.floor(len(queries)*dev_set_size)
        dev_set_queries = queries[0:threshold]
        test_set_queries = queries[threshold:]
        dev_set_target = target[0:threshold,:]
        test_set_target = target[threshold:,:]
        
#         print('     dev_set_queries:',len(dev_set_queries))
#         print('      dev_set_target: %d x %d'%(dev_set_target.shape[0],dev_set_target.shape[1]))
#         print('     test_set_queries:',len(test_set_queries))
#         print('      test_set_target: %d x %d'%(test_set_target.shape[0],test_set_target.shape[1]))
        
        return {'dev_set':(dev_set_queries,dev_set_target),'test_set':(test_set_queries,test_set_target),}

def to_ranking_task(papers):
    queries = []
    corpus_index = []
    labels = ['index','queries']
    path_to_index = {'index':{},'queries':{}}
    target = zeros((len(papers['suspicious-document']),len(papers['source-document'])),dtype= uint8)
    
    for paperi in papers['source-document']:
        indexi = len(corpus_index)
        corpus_index.append(read_content(paperi))
        path_to_index['index'][paperi['reference']] = indexi
        
#     pprint(path_to_index) 

    for paperi in papers['suspicious-document']:
        indexi = len(queries)
        queries.append(read_content(paperi))
        path_to_index['queries'][paperi['reference']] = indexi
#         print('query :',indexi)

        # pode ter mais de uma passagem plagiada do mesmo documento!
        for featj in paperi['features']:
            if (featj['name'] == 'plagiarism'):
                relevant_pathi = featj['source_reference']
                
                # reduced dataset can remove some source documents!
                if relevant_pathi in path_to_index['index'].keys(): 
                    relevant_indexi = path_to_index['index'][relevant_pathi]
                    target[indexi][relevant_indexi] = 1
#                     print('\t',featj['name'], ' : ', relevant_pathi,' => ', relevant_indexi)

    return queries, corpus_index, target, labels
        
def extract_pan_2011_external_detection_ranking_task(path):
    
    complete_output_path = os.path.join(path+'_per_task','raking','external-detection-corpus')
    
    print(" Exists ",complete_output_path, " ?")
    if (os.path.exists(os.path.join(complete_output_path,'queries.json'))):
        print('Already exists! Loading...')
        f = open(os.path.join(complete_output_path,'queries.json'))
        queries = json.load(f)
        f.close()
        f = open(os.path.join(complete_output_path,'corpus_index.json'))
        corpus_index = json.load(f)
        f.close()
        f = open(os.path.join(complete_output_path,'labels.json'))
        labels = json.load(f)
        f.close()
        
        f = open(os.path.join(complete_output_path,'target.pkl'), 'rb')
        target = pickle.load(f)
        f.close()
            
    else:
        print("... doesn't exists! Creating...")
        papers = extract_pan_2011(path)

        intrinsic = papers.get('intrinsic-detection-corpus')
        del intrinsic

        external = papers.get('external-detection-corpus')
                        
        queries, corpus_index, target, labels = to_ranking_task(external)
        
        del external
        print('writting queries.json')
        write_on_file(path = complete_output_path,file_name='queries.json', encoding='latin1',content = json.dumps(queries))
        print('writting corpus_index.json')
        write_on_file(path = complete_output_path,file_name='corpus_index.json', encoding='latin1',content = json.dumps(corpus_index))
        print('writting labels.json')
        write_on_file(path = complete_output_path,file_name='labels.json', encoding='latin1',content = json.dumps(labels))

        print('writting target.pkl')
        output = open(os.path.join(complete_output_path,'target.pkl'), 'wb')
        pickle.dump(target, output)
        output.close()

#     pprint(len(corpus_index))
#     pprint(len(queries))
#     pprint(shape(target))
#     nz = nonzero(target)
#     pprint(shape(nz))
#     pprint(nz)
    
     
    return queries, corpus_index, target, labels
        
        
# if __name__ == '__main__':
#     
#     root = "/media/dados/Colecoes de Dados/PAN/Plagiarism detection/pan-plagiarism-corpus-2011"
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
