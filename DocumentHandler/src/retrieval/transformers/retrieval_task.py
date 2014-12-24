from sklearn.base import TransformerMixin, BaseEstimator
from pprint import pprint
from numpy import shape, cos, nonzero, transpose, math, ones, array, matrix,\
    where, zeros
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer,\
    TfidfVectorizer
from scipy.sparse.csc import csc_matrix
from scipy.sparse.lil import lil_matrix
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.metrics.metrics import confusion_matrix, precision_recall_curve
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors.classification import KNeighborsClassifier
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from time import localtime, strftime
import time
import pywt
from extractors_per_dataset.meter_extractor import extract_meter_to_corpus_target_labels
from sklearn.metrics.pairwise import pairwise_distances
from sklearn import preprocessing
from sklearn.metrics import metrics

class SimilarityTransformer(BaseEstimator,TransformerMixin):
    """
       computes similarity between transform documents and fit documents.
       returns a document X similarity matrix.
       index = fix X ( atribute-document matrix)
       queries = tranform X (atribute-document matrix)
       foreach query pairwise_distances_metrics to index documents
    """
    def __init__(self, pairwise_distances_metrics, pairwise_distances_n_jobs):
        self.pairwise_distances_metrics = pairwise_distances_metrics
        self.pairwise_distances_n_jobs = pairwise_distances_n_jobs
        self.train_X = None
        
    def fit_transform(self, X, y):
        print('fittransform!')
        self.fit(X, y)
        return self.transform(X)
        
    def fit(self, X, y=None):
        self.train_X = X
         
    def transform(self, X):
        return self.predict_queries_ranking(X)[1]
    
    def predict_queries_ranking(self, X):
        if shape(X)[1] != shape(self.train_X)[1]:
            raise Exception("Transform #features (%d) must be the same as trainning (%d)! "%(shape(X)[1] , shape(self.train_X)[1]))
        else:
            x_distances = pairwise_distances(X, self.train_X, metric=self.pairwise_distances_metrics, n_jobs=self.pairwise_distances_n_jobs)
            
            ranking = np.argsort(x_distances, axis=1)
            
            x_similarities = ones(shape(x_distances)) - x_distances
            
#             pprint(x_similarities[0,ranking[0,:]])
#             pprint(x_similarities[1,ranking[1,:]])
#             exit()         
        return ranking, x_similarities
        
    
class RetrievalTask():
    
    def __init__(self, pairwise_distances_metrics, pairwise_distances_n_jobs,instance_index):
        self.pairwise_distances_metrics = pairwise_distances_metrics
        self.pairwise_distances_n_jobs = pairwise_distances_n_jobs
        self.instance_index = instance_index
        self.relevant_list = None
        
        self.similarity_transformer = SimilarityTransformer(pairwise_distances_metrics,pairwise_distances_n_jobs)
        self.similarity_transformer.fit(instance_index)
    
    def execute_retrieval(self, queries, relevants):
        if (relevants == None):
            raise Exception("relevants = relevant set indexes can not be None!")
        
        nonzero_indexes = nonzero(array(relevants)>1)
        if shape(nonzero_indexes)[1] > 0:
            raise Exception("relevants = relevant set indexes must be binary(0,1)!" )

        queries_ranking, queries_similarities = self.similarity_transformer.predict_queries_ranking(queries)

#         print('relevants : ', shape(relevants))
#         print('queries_ranking : ', shape(queries_ranking))
#         print(queries_ranking)
#         print('----X---')

        return queries_ranking, queries_similarities

            # 11 levels of precision recall interpolated_precision[0] = max precision in recall > 0
    def interpolated_precision_recall_curve(self,queries_ranking, queries_similarities, relevants):
#         precision_per_query = []
#         recall_per_query = []
#         precision_leves_per_query = []
        
        queries_count = shape(queries_ranking)[0]
        interpolated_precision = zeros(11,dtype = np.float128) 
        
        for qindex in range(0,queries_count):

            tp = 0
            precision, recall = [0],[0]
            
            relevants_count = shape(nonzero(relevants[qindex]))[1]
#             print('relevants_count : ',relevants_count)
            retrieved_count = 1
            
            for ranki in queries_ranking[qindex]:
#                 print('queries_similarities.shape(%d,%d)'%(queries_similarities.shape[0],queries_similarities.shape[1]))
#                 print('relevants.shape(%d,%d)'%(relevants.shape[0],relevants.shape[1]))
#                 print('[qindex][ranki]',qindex,ranki)
                if (queries_similarities[qindex][ranki] > 0) and (relevants[qindex][ranki] == 1):
                    tp += 1
                    
                precisioni = tp / retrieved_count
                if relevants_count == 0:
                    recalli = 1
                else:
                    recalli = tp / relevants_count
                
                retrieved_count += 1
                
#                 if (recalli != 1.0):
#                     print('precisioni : ',precisioni,'recalli : ',recalli,"!!!!!!!!!!!!!!!!!!!!!!!")
#                 else:
#                     print('precisioni : ',precisioni,'recalli : ',recalli,)
#                 print('tp : ',tp,'retrieved_count : ',retrieved_count, 'relevants_count : ',relevants_count)

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
                  
#             precision_leves_per_query.append(precision_levels)  

#             print(precision_levels)
#             print(interpolated_precision)
#             print("**************")
            
#             precision_per_query.append(precision)
#             recall_per_query.append(recall)
#             
#         print('precision_per_query : ',shape(precision_per_query))
#         print('recall_per_query : ',shape(recall_per_query))
#         print('precision_leves_per_query : ',shape(precision_leves_per_query))
        
        
        auc = float("{0:1.4f}".format(metrics.auc([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1],interpolated_precision)))
        
        return interpolated_precision, auc

    def highest_false_match_and_separation(self,queries_ranking, queries_similarities, relevants):
        
#         print(queries_ranking)
#         print(queries_similarities)

        # rows = queries, col[0] = HFM and col[1] = SEP
        hfm_sep_matrix = zeros((relevants.shape[0],2))
        
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
            
#             print("(HFM|SEP) = (%4.4f | %4.4f) "%(hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1]))
            
        return hfm_sep_matrix

# if __name__ == '__main__':
#     
# #         X, y, labels = qualify_code.load_other_corpus("/media/dados/Colecoes de Dados/toidataset/")
# #         X, y, labels = qualify_code.load_other_corpus("/media/dados/Colecoes de Dados/Authorship/Federalist Papers/papers_per_author")
#         queries, corpus_index, relevants, labels = qualify_code.load_meter_corpus_to_ranking()
#         cv = CountVectorizer()#TfidfVectorizer() #CountVectorizer() #
#         tm = TfidfTransformer()#WaveletModelSignalTransformer(level=1,mother_wavelet='db1') #HighCorrelationModelSignalTransformer()
# #         print(shape(corpus_index))
# #         print(shape(queries))
# #         print(shape(corpus_index+queries))
# #         exit()
#         corpus_index_and_queries = cv.fit_transform(corpus_index+queries, None)
#         x_corpus_index = cv.transform(corpus_index)
#         x_queries  = cv.transform(queries)
#         
#         corpus_index_and_queries1 = tm.fit_transform(corpus_index_and_queries, None)
#         x_corpus_index = tm.transform(x_corpus_index)
#         x_queries  = tm.transform(x_queries)
#         
#         print('corpus_index : ',shape(corpus_index))
#         print('queries : ',shape(queries))
#         print('x_corpus_index : ',shape(x_corpus_index))
#         print('x_queries : ',shape(x_queries))
#         print('relevants : ',shape(relevants))
#         print('nonzero relevants : ',shape(nonzero(relevants)))
#         
#         exit()
#         
#         import matplotlib.pyplot as plt
#         plt.clf()
#         
#         distances_auc = {}
#         
#         for distance in (
# #                         'jaccard',
# #                         'euclidean',
#                         'dice',
#                         'cosine', 
# #                          'mahalanobis', 
#                         
#                          ):
#             rt = RetrievalTask(distance,3,x_corpus_index)
#             queries_ranking, queries_similarities = rt.execute_retrieval(x_queries, relevants)
#             
#             interpolated_precision, auc = rt.interpolated_precision_recall_curve(queries_ranking, queries_similarities)
#             
#             print(distance, '.interpolated_precision : ',interpolated_precision)
#             plt.plot((0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1), interpolated_precision, label=distance+' Precision-Recall curve(%4.4f)'%(auc))
# 
# #             print(distance, '.auc = ',auc)
#             
#             distances_auc[distance] = auc
#         pprint(distances_auc)
# 
#         plt.xlabel('Recall')
#         plt.ylabel('Precision')
#         plt.ylim([0.0, 1.05])
#         plt.xlim([0.0, 1.0])
#         plt.legend(loc="lower left")
#         plt.show()
#             
# #         lb = preprocessing.LabelBinarizer()
# #         lb.fit(y)
# #         biny = lb.transform(y)
# #         pprint(biny)
# #         print(shape(biny))
# # #         print(shape(raking))
# # #         print(biny[raking[0]])
# #         
# #         rt = RetrievalTask()
# #         rt.fit(X, biny)
# #         exit()
#         
#         
# #         for i in range(0,shape(Xt)[0]):
# #             for j in range(0,shape(Xt)[1]):
# #                 print(i,',',j,'=',Xt[i,j])
# #         print(Xt)