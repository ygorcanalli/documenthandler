from pprint import pprint
from numpy import nonzero, zeros
from extractors_per_dataset.co_derivative_extractor import extract_co_derivative_to_ranking_task
from transformers.retrieval_task import RetrievalTask
import time
from model.content import Document
from compare.structural_similarity import *
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from compare.structural_similarity import list_of_paragraphs, bag_of_words
from Onboard import WordSuggestions

def extract_dev_set(queries,corpus_index,target,num_queries = None):
    if (num_queries == None):
        num_queries = len(queries)
        
    queries_teste, corpus_index_teste, target_teste = [], [], zeros((num_queries,num_queries*9))
    
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
#     queries_teste, corpus_index_teste, target_teste = extract_dev_set(queries, corpus_index, target)
    # 2 consultas e seus relevantes
    queries_teste, corpus_index_teste, target_teste = extract_dev_set(queries, corpus_index, target,2)      

    #tokenizando com o sckitlearn (bow)
        
    cv = CountVectorizer(ngram_range=(1,1)) # extraindo o bow
    index_td_matrix = cv.fit_transform(corpus_index_teste, target_teste) #matrix termo-documento do indice
    queries_td_matrix = cv.transform(queries_teste) #matrix termo-documento das consultas
    
    distance = 'cosine'
    jobs = 1
    rt = RetrievalTask(distance,jobs,index_td_matrix)
    start_time = time.process_time()
    queries_ranking, queries_similarities = rt.execute_retrieval(queries_td_matrix, target_teste)
    ranking_elapsed_time = time.process_time() - start_time
        
    interpolated_precision, auc = rt.interpolated_precision_recall_curve(queries_ranking, queries_similarities, target_teste)
    hfm_sep_matrix = rt.highest_false_match_and_separation(queries_ranking, queries_similarities, target_teste)
    
    print("auc(%s) = %4.2f in %d s"%(distance,auc,ranking_elapsed_time))
        
    for queryi_index in range (0,hfm_sep_matrix.shape[0]):
        print("query(%d).(HFM|SEP) = (%4.4f | %4.4f) "%(queryi_index,hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1]))


    print("\'Resultados Ygor\'")
    
    '''
    BAG OF WORDS
    '''
    queries_similarities = zeros( (len(queries_teste),len(corpus_index_teste)))
    queries_ranking = []
    ranking_elapsed_time = 0
    # execucao da comparacao hierarquica do ygor que gerara queries_similarities
    for i in range(0, len(queries_teste)):
        query = Document(queries_teste[i])
        queries_ranking.append([])
        queries_ranking_simil = []
        for j in range(0, len(corpus_index_teste)):
        
            document = Document(corpus_index_teste[j])
    
            start_time = time.process_time()
            # Fill the result map with similaritys
            simil = bag_of_words(query, document)        
            ranking_elapsed_time += time.process_time() - start_time
            
            queries_similarities[i][j] = simil
            queries_ranking[i].append(j)
            queries_ranking_simil.append(j)
        #ordena a o ranking para i
        queries_ranking[i] = [k[0] for k in sorted(zip(queries_ranking[i], queries_ranking_simil), key=lambda l: l[1])]
        print(queries_ranking[i])
        print(queries_ranking_simil)
        print("\n")
    
    
    #adaptar para : 
    #calcular queries_ranking , onde queries_ranking[0][0] é a posicao do documento no indice com maior similaridade para consulta 0 (primeira consulta)  
    
    #queries_ranking, queries_similarities = ...

    distance = "bag of words"
    
    interpolated_precision, auc = rt.interpolated_precision_recall_curve(queries_ranking, queries_similarities, target_teste)
    hfm_sep_matrix = rt.highest_false_match_and_separation(queries_ranking, queries_similarities, target_teste)
    
    print("auc(%s) = %4.2f in %d s"%(distance,auc,ranking_elapsed_time))
        
    for queryi_index in range (0,hfm_sep_matrix.shape[0]):
        print("query(%d).(HFM|SEP) = (%4.4f | %4.4f) "%(queryi_index,hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1]))
    '''
    LIST OF WORDS
    '''
    queries_similarities = zeros( (len(queries_teste),len(corpus_index_teste)))
    queries_ranking = []
    ranking_elapsed_time = 0
    # execucao da comparacao hierarquica do ygor que gerara queries_similarities
    for i in range(0, len(queries_teste)):
        query = Document(queries_teste[i])
        queries_ranking.append([])
        queries_ranking_simil = []
        for j in range(0, len(corpus_index_teste)):
        
            document = Document(corpus_index_teste[j])
    
            start_time = time.process_time()
            # Fill the result map with similaritys
            simil = list_of_words(query, document)
            ranking_elapsed_time += time.process_time() - start_time       
            
            queries_similarities[i][j] = simil
            queries_ranking[i].append(j)
            queries_ranking_simil.append(j)
        #ordena a o ranking para i
        queries_ranking[i] = [k[0] for k in sorted(zip(queries_ranking[i], queries_ranking_simil), key=lambda l: l[1])]
        print(queries_ranking[i])
        print(queries_ranking_simil)
        print("\n")
    
    
    #adaptar para : 
    #calcular queries_ranking , onde queries_ranking[0][0] é a posicao do documento no indice com maior similaridade para consulta 0 (primeira consulta)  
    
    #queries_ranking, queries_similarities = ...

    distance = "list of words"
    
    interpolated_precision, auc = rt.interpolated_precision_recall_curve(queries_ranking, queries_similarities, target_teste)
    hfm_sep_matrix = rt.highest_false_match_and_separation(queries_ranking, queries_similarities, target_teste)
    
    print("auc(%s) = %4.2f in %d s"%(distance,auc,ranking_elapsed_time))
        
    for queryi_index in range (0,hfm_sep_matrix.shape[0]):
        print("query(%d).(HFM|SEP) = (%4.4f | %4.4f) "%(queryi_index,hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1]))  
    '''
    BAG OF PARAGRAPHS / BAG OF WORDS
    '''
    queries_similarities = zeros( (len(queries_teste),len(corpus_index_teste)))
    queries_ranking = []
    ranking_elapsed_time = 0
    # execucao da comparacao hierarquica do ygor que gerara queries_similarities
    for i in range(0, len(queries_teste)):
        query = Document(queries_teste[i])
        queries_ranking.append([])
        queries_ranking_simil = []
        for j in range(0, len(corpus_index_teste)):
        
            document = Document(corpus_index_teste[j])
    
            start_time = time.process_time()
            # Fill the result map with similaritys
            simil = bag_of_paragraphs(query, document, granule_alignment_funcion=bag_of_words, threshold=0.8)
            ranking_elapsed_time += time.process_time() - start_time     
            
            queries_similarities[i][j] = simil
            queries_ranking[i].append(j)
            queries_ranking_simil.append(j)
        #ordena a o ranking para i
        queries_ranking[i] = [k[0] for k in sorted(zip(queries_ranking[i], queries_ranking_simil), key=lambda l: l[1])]
        print(queries_ranking[i])
        print(queries_ranking_simil)
        print("\n")
    
    
    #adaptar para : 
    #calcular queries_ranking , onde queries_ranking[0][0] é a posicao do documento no indice com maior similaridade para consulta 0 (primeira consulta)  
    
    #queries_ranking, queries_similarities = ...

    distance = "bag of paragraph / bag of words"
    
    interpolated_precision, auc = rt.interpolated_precision_recall_curve(queries_ranking, queries_similarities, target_teste)
    hfm_sep_matrix = rt.highest_false_match_and_separation(queries_ranking, queries_similarities, target_teste)
    
    print("auc(%s) = %4.2f in %d s"%(distance,auc,ranking_elapsed_time))
        
    for queryi_index in range (0,hfm_sep_matrix.shape[0]):
        print("query(%d).(HFM|SEP) = (%4.4f | %4.4f) "%(queryi_index,hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1])) 
    '''
    LIST OF PARAGRALHS / BAG OF WORDS
    '''    
    queries_similarities = zeros( (len(queries_teste),len(corpus_index_teste)))
    queries_ranking = []
    ranking_elapsed_time = 0
    # execucao da comparacao hierarquica do ygor que gerara queries_similarities
    for i in range(0, len(queries_teste)):
        query = Document(queries_teste[i])
        queries_ranking.append([])
        queries_ranking_simil = []
        for j in range(0, len(corpus_index_teste)):
        
            document = Document(corpus_index_teste[j])
    
            start_time = time.process_time()
            # Fill the result map with similaritys
            simil = list_of_paragraphs(query, document, granule_alignment_funcion=bag_of_words, threshold=0.8)
            ranking_elapsed_time += time.process_time() - start_time      
            
            queries_similarities[i][j] = simil
            queries_ranking[i].append(j)
            queries_ranking_simil.append(j)
        #ordena a o ranking para i
        queries_ranking[i] = [k[0] for k in sorted(zip(queries_ranking[i], queries_ranking_simil), key=lambda l: l[1])]
        print(queries_ranking[i])
        print(queries_ranking_simil)
        print("\n")
    
    
    #adaptar para : 
    #calcular queries_ranking , onde queries_ranking[0][0] é a posicao do documento no indice com maior similaridade para consulta 0 (primeira consulta)  
    
    #queries_ranking, queries_similarities = ...

    distance = "list of paragraph / bag of words"
    
    interpolated_precision, auc = rt.interpolated_precision_recall_curve(queries_ranking, queries_similarities, target_teste)
    hfm_sep_matrix = rt.highest_false_match_and_separation(queries_ranking, queries_similarities, target_teste)
    
    print("auc(%s) = %4.2f in %d s"%(distance,auc,ranking_elapsed_time))
        
    for queryi_index in range (0,hfm_sep_matrix.shape[0]):
        print("query(%d).(HFM|SEP) = (%4.4f | %4.4f) "%(queryi_index,hfm_sep_matrix[queryi_index][0],hfm_sep_matrix[queryi_index][1]))
