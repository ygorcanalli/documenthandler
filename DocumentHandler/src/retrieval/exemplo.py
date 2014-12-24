from pprint import pprint
import numpy as np
from extractors_per_dataset.co_derivative_extractor import extract_co_derivative_to_ranking_task
import time
from model.content import Document
from collections import OrderedDict
from compare.structural_similarity import list_of_paragraphs, bag_of_words
from sklearn.metrics import metrics

def interpolated_precision_recall_curve(queries_ranking, queries_similarities, relevants):
    
    queries_count = np.shape(queries_ranking)[0]
    interpolated_precision = np.zeros(11,dtype = np.float128) 
    
    for qindex in range(0,queries_count):

        tp = 0
        precision, recall = [0],[0]
        
        relevants_count = np.shape(np.nonzero(relevants[qindex]))[1]
        retrieved_count = 1
        
        for ranki in queries_ranking[qindex]:
            if (queries_similarities[qindex][ranki] > 0) and (relevants[qindex][ranki] == 1):
                tp += 1
                
            precisioni = tp / retrieved_count
            if relevants_count == 0:
                recalli = 1
            else:
                recalli = tp / relevants_count
            
            retrieved_count += 1

            precision += [precisioni]
            recall += [recalli]
              
        # query's 11 levels of precision recall precision_levels[0] = max precision in recall > 0                  
        precision_levels = []
        
        for i in range(0,11):
            prec_ati = 0
            for j in range(0,len(recall)):
                if i <= recall[j]*10:
                    prec_ati =  max(prec_ati,precision[j])
                    
            precision_levels.append(prec_ati)
            interpolated_precision[i] += prec_ati/queries_count
            
        del precision
        del recall
                 
    
    auc = float("{0:1.4f}".format(metrics.auc([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1],interpolated_precision)))
    
    return interpolated_precision, auc

def highest_false_match_and_separation(queries_ranking, queries_similarities, relevants):
    # rows = queries, col[0] = HFM and col[1] = SEP
    hfm_sep_matrix = np.zeros((relevants.shape[0],2))
    
    for queryi_index in range(0,relevants.shape[0]):
        queryi_ranking = queries_ranking[queryi_index]
        queryi_similarities = queries_similarities[queryi_index]
        max_similarity = queryi_similarities[queryi_ranking[0]]
        
        lowest_relevant = -1
        highest_irrelevant = -1
        
        for j in range(0,relevants.shape[1]):
            ranki_pos = queryi_ranking[j]
            
            if (highest_irrelevant == -1 and relevants[queryi_index][ranki_pos] == 0):
                highest_irrelevant = ranki_pos
                
            if (relevants[queryi_index][ranki_pos] == 1):
                lowest_relevant = ranki_pos
                
        LTM = 100*queryi_similarities[lowest_relevant] / max_similarity
        HFM = 100*queryi_similarities[highest_irrelevant] / max_similarity
        SEP = LTM - HFM
        
        hfm_sep_matrix[queryi_index][0] = HFM
        hfm_sep_matrix[queryi_index][1] = SEP
        
    return hfm_sep_matrix

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
    
    #o dataset inteiro 
    #queries_teste, corpus_index_teste, target_teste = extract_dev_set(queries, corpus_index, target)
    # 2 consultas e seus relevantes
    queries_teste, corpus_index_teste, target_teste = extract_dev_set(queries, corpus_index, target,2)      

    
    '''
    BAG OF WORDS
    '''
    distance = "bag of words"
    queries_similarities = np.zeros( (len(queries_teste),len(corpus_index_teste)))
    queries_ranking = []
    ranking_elapsed_time = 0
    # execucao da comparacao hierarquica que gerara queries_similarities
    #calcular queries_ranking , onde queries_ranking[0][0] é a posicao do documento no indice com maior similaridade para consulta 0 (primeira consulta)
    for i in range(0, len(queries_teste)):
        query = Document(queries_teste[i])
        queries_ranking.append({})
        for j in range(0, len(corpus_index_teste)):
        
            document = Document(corpus_index_teste[j])
    
            start_time = time.process_time()
            # Fill the result map with similaritys
            simil = bag_of_words(query, document)#, granule_alignment_funcion=bag_of_words, threshold=0.8)        
            ranking_elapsed_time += time.process_time() - start_time
            
            queries_similarities[i][j] = simil
            queries_ranking[i][j] = simil
        #ordena a o ranking para i
        queries_ranking[i] = OrderedDict(sorted(queries_ranking[i].items(), key=lambda t: t[1], reverse=True)) 
        
    #pprint(target_teste)
    #pprint(queries_ranking)
    #pprint(queries_similarities)
    interpolated_precision, auc = interpolated_precision_recall_curve(queries_ranking, queries_similarities, target_teste)
    hfm_sep_matrix = highest_false_match_and_separation(queries_ranking, queries_similarities, target_teste)
    
    print("auc(%s) = %4.2f in %d s"%(distance,auc,ranking_elapsed_time))
    pprint(interpolated_precision)    
    for queryi_index in range (0,hfm_sep_matrix.shape[0]):
        print("query(%d).(HFM|SEP) = (%4.4f | %4.4f) "%(queryi_index,hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1]))