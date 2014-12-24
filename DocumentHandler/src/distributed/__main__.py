import os
import sys
import getopt
from time import strftime
from pprint import pprint


import util
from compare import structural_similarity
from mpi4py import MPI
from time import time
from compare.distance import *
from compare.alignment import *
import model
import json

# MPI initializations
comm   = MPI.COMM_WORLD            # MPI communicator
size   = comm.Get_size()           # Total number of processes
rank   = comm.Get_rank()           # Process rank
name   = MPI.Get_processor_name()  # Processor identifier

WORKLOAD = 0
RESULTS = 1
INFO = 2
OK = 3

def interpolated_precision_recall(precision_by_recall):
    
    # creates array of 11 elements
    interpolation = [0] * 11
    
    for i in range(0, 11):
        percentil = i / 10.0
        possible_precision = []
        for recall in precision_by_recall:
            if percentil <= recall:
                possible_precision.append(precision_by_recall[recall]) 
        if len(possible_precision) > 0:
            interpolation[i] = max(possible_precision)   
            
    return interpolation
        
def average_interpolated_precision_recall(discrete_precisions_list):
    interpolation = [0] * 11
    
    n_queries = len(discrete_precisions_list)
    for i in range(0, 11):
        accum = 0
        for discrete_precisions in discrete_precisions_list:
            accum += discrete_precisions[i]
            
        interpolation[i] = accum / n_queries
    return interpolation

def split_workload(workload, n_workers):

    splited_workload = []

    len_workload = len(workload)
    # floor division
    workload_split_size = len_workload // n_workers
    remainder_workload = len_workload % n_workers

    for i in range(0, n_workers):
        
        if i < remainder_workload:
            begin = workload_split_size*i + i
        else:
            begin = workload_split_size*i + remainder_workload

        if i < remainder_workload: 
            end = begin + workload_split_size + 1
        else:
            end = begin + workload_split_size

        splited_workload.append(workload[begin:end])

    return splited_workload


def create_list_of_pairs(queries_path, corpus_path):
    # List files in database
    queries = util.list_dir(queries_path, "*.pkl")
    corpus = util.list_dir(corpus_path, "*.pkl")
    
    pairs = []
    for query in queries:
        for document in corpus:
            pairs.append( (query, document) )
    return pairs

def run_alignment(alignment_mode, query, document, alignment_function): 
    return None


def master(n_workers, config):
    
    queries_path = config["queries_path"]
    corpus_path = config["corpus_path"]
    
    start_time = time() 
    results = {}
        
    '''    
    relevants = json.load(open(os.path.join(database_root_path, "pickled", "en", "relevants_map.json"), "r"))
    
    new_queries = []
    new_documents = []
    new_relevants = {}

    for key, value in relevants.items():
        new_relevants[key] = value
        new_queries.append(key)
        new_documents += value
        if len(new_queries) == 2:
            break 
        
    '''
    pairs = create_list_of_pairs(queries_path, corpus_path)
    
    splited_workload = split_workload(pairs, n_workers)

    # Send workload to workers
    for n_retrived in range(0, n_workers):
        comm.send(splited_workload.__getitem__(n_retrived), dest = n_retrived + 1, tag=WORKLOAD)

    # Receive results and merge the result map
    for n_retrived in range(0, n_workers):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=RESULTS)
        results.update(worker_results)

    end_time = time()
    spent_time = (end_time - start_time)

    print(spent_time)

    queries_results = {}
    
    for query, document in results:
        
        if query not in queries_results:
            queries_results[query] = []
        
        # store query results for ranking
        simil = results[ (query, document) ]
        queries_results[query].append( (document, simil) )
     
    pprint(queries_results)    
    #precision_recall_map = {}
    #interpolate_precisions_list = []
    
    #sort results
    '''
    for query, query_result in queries_results.items(): 
        precision_recall_map[query] = {}
        
        query_result.sort(key=lambda tup: tup[1],reverse=True)
        
        n_retrived = 1
        n_relevants = len(relevants[query])
        n_relevants_retrived = 0
        
        for result, simil in query_result:
            
            # if the result is relevant for query, increment
            if result in relevants[query]:
                n_relevants_retrived += 1    
            
            precision = float(n_relevants_retrived) / float(n_retrived)
            recall = float(n_relevants_retrived) / float(n_relevants)
            
            #print("Precision: %d/%d=%f Recall: %d/%d=%f\n") % (n_relevants_retrived, n_retrived, precision, n_relevants_retrived, n_relevants, recall)
            
            # store the max precision for each recall
            if recall not in precision_recall_map[query]:
                precision_recall_map[query][recall] = precision
            else:
                precision_recall_map[query][recall] = max(precision_recall_map[query][recall],precision)
            

            n_retrived += 1
        
        # store the interpolated precision for each query
        interpolate_precisions_list.append(interpolated_precision_recall(precision_recall_map[query]))
    
    average_interpolated_precision = average_interpolated_precision_recall(interpolate_precisions_list)
    '''      
    
    info = {}
    
    # Recive info from workers
    '''
    for n_retrived in range(0, n_workers):
        info.extend(comm.recv(source=MPI.ANY_SOURCE, tag=INFO))
    '''
    info["time"] = spent_time
    #info["average_interpolated_precision_recall"] = average_interpolated_precision

    return info


def worker(config):

    queries_path = config["queries_path"]
    corpus_path = config["corpus_path"]
    compare_mode = getattr(structural_similarity, config["compare_mode"])
    granule_mode = None
    threshold = None
        
    if "granule_mode" in config and "threshold" in config:
        granule_mode = getattr(structural_similarity, config["granule_mode"])
        threshold = config["threshold"]
        
    
    corpus = {}
    queries = {}
    results = {}

    workload = comm.recv(source=0, tag=WORKLOAD)

    # Load corpus from pickle avoiding repeated corpus
    for query, document in workload:

        if not query in queries:
            queries[query] = model.document_from_pkl(os.path.join(queries_path, query))

        if not document in corpus:
            corpus[document] = model.document_from_pkl(os.path.join(corpus_path, document))

        # Fill the result map with similaritys
        simil = compare_mode(queries[query], corpus[document], granule_alignment_funcion=granule_mode, threshold=threshold)        
        
        results[ (query, document) ] = simil

    # Send result to master
    comm.send(results, 0, tag=RESULTS)


def write_output_results(info, config):
    #convert info from workers and master in string

    info["number_of_process"] = size
    info["queries_path"] = config["queries_path"]
    info["corpus_path"] = config["corpus_path"]
    info["compare_mode"] = config["compare_mode"]
    
    if "granule_mode" in config and "threshold" in config:
        info["granule_mode"] = config["granule_mode"]
        info["threshold"] = config["threshold"]

    output_file_path = config["results_path"]

    output_file = open(output_file_path, "w")
    json.dump(info, output_file)
    output_file.close()     
    

# Read arguments from command line
def __main__(argv):
    
    try:
        opts, args = getopt.getopt(argv, "c:", ["config_file="])
    except getopt.GetoptError:
        print('Illegal arguments')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('no_distributed -D <database_path>')
            sys.exit()
        elif opt in ("-c", "--config_file"):
            config_file = open(arg, "r")
            config = json.load(config_file)
            config_file.close()
    

    if rank == 0:
        info = master(size - 1, config)
        write_output_results(info, config)
    else:
        worker(config)
    

if __name__ == "__main__":
    __main__(sys.argv[1:])
