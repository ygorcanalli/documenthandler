'''
Created on Dec 29, 2014

@author: ygor
'''
import numpy as np
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
        
        for rank in range(0,11):
            prec_ati = 0
            for j in range(0,len(recall)):
                if rank <= recall[j]*10:
                    prec_ati =  max(prec_ati,precision[j])
                    
            precision_levels.append(prec_ati)
            interpolated_precision[rank] += prec_ati/queries_count
            
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
