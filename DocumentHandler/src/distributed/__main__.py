import os
import sys
import getopt
from pprint import pformat
from collections import OrderedDict


import util
from compare import structural_similarity
from mpi4py import MPI
from time import time
from compare.distance import *
from compare.alignment import *
from compare.metrics import *
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

def split_corpus_index(corpus_index, n_workers, rank):

    length = len(corpus_index)
    
    # floor division
    split_size = length // n_workers
    remainder = length % n_workers

    if rank < remainder:
        begin = split_size*rank + rank
    else:
        begin = split_size*rank + remainder

    if rank < remainder: 
        end = begin + split_size + 1
    else:
        end = begin + split_size

    splited_corpus_index = corpus_index[begin:end]

    return splited_corpus_index

def master(n_workers, config):
    
    queries_path = config["queries_path"]
    corpus_index_path = config["corpus_index_path"]
    
    target_path = config["target_path"]
    target = json.load(open(target_path, "r"))
    target = np.array(target)
    
    # List files in database
    queries = util.list_dir(queries_path, "*.pkl")
    corpus_index = util.list_dir(corpus_index_path, "*.pkl")
             
    start_time = time()
    
    # work on first slice
    results = do_work(n_workers, config)
    
    # Receive results and merge the result map
    for rank in range(0, n_workers - 1):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=RESULTS)
        results.update(worker_results)

    end_time = time()
    spent_time = (end_time - start_time)

    print(spent_time)
    
    queries_similarities = np.zeros( (len(queries),len(corpus_index)))
    queries_ranking = []
    
    # initialize ranking OrderedDicts
    for i in range(len(queries)):
        queries_ranking.append({})
        
    for query, document in results:
        
        # store query results and rankings
        simil = results[ (query, document) ]
        i = int(query.replace(".pkl", ""))
        j = int(document.replace(".pkl", ""))
        
        # Store similarities
        queries_similarities[i][j] = simil
        
        # Store similarities for ranking
        queries_ranking[i][j] = simil
    
    # Order rankings
    for i in range(len(queries)):
        queries_ranking[i] = OrderedDict(sorted(queries_ranking[i].items(), key=lambda t: t[1], reverse=True)) 
    
    # Calculate interpolated precision recall
    interpolated_precision, auc = interpolated_precision_recall_curve(queries_ranking, queries_similarities, target)
    
    # Calculate highest false matching and separation
    hfm_sep_matrix = highest_false_match_and_separation(queries_ranking, queries_similarities, target)
    
    info = {}
    
    info["time"] = spent_time
    info["workers"] = []
    
    # Recive info from workers 
    for i in range(0, n_workers - 1):
        info["workers"].append(comm.recv(source=MPI.ANY_SOURCE, tag=INFO))
    
    return interpolated_precision, hfm_sep_matrix, info

def do_work(n_workers, config):
    queries_path = config["queries_path"]
    corpus_index_path = config["corpus_index_path"]
    compare_mode = getattr(structural_similarity, config["compare_mode"])
    granule_mode = None
    threshold = None
        
    if "granule_mode" in config and "threshold" in config:
        granule_mode = getattr(structural_similarity, config["granule_mode"])
        threshold = config["threshold"]  
    
    corpus_index = util.list_dir(corpus_index_path, "*.pkl")
    queries = util.list_dir(queries_path, "*.pkl")
    results = {}
        
    corpus_index_slice = split_corpus_index(corpus_index, n_workers, rank)

    pickled_corpus_index = {}
    # Load corpus_index from pickle
    for document in corpus_index_slice:
        pickled_corpus_index[document] = model.document_from_pkl(os.path.join(corpus_index_path, document))
        
    for query_path in queries:
        #Load query from pickle
        query = model.document_from_pkl(os.path.join(queries_path, query_path))
        
        for document in pickled_corpus_index:          
            # Fill the result map with similarities        
            simil = compare_mode(queries[query], corpus_index[document], granule_alignment_funcion=granule_mode, threshold=threshold)        
            results[ (query, document) ] = simil
    
    return results

def worker(n_workers, config):
    
    start_time = time()
    
    # work on rank-th slice
    results = do_work(n_workers, config)
    end_time = time()
    spent_time = (end_time - start_time)
    
    # Send result to master
    comm.send(results, 0, tag=RESULTS)
    
    # Send info to master
    info = {}
    info["name"] = name
    info["rank"] = rank
    info["time"] = spent_time
    comm.send(info, 0, tag=INFO)


def write_output_results(interpolated_precision, hfm_sep_matrix, info, config):
    #convert output_json from workers and master in string
    output_json = {}
    
    output_json["time"] = info["time"]
    output_json["workers"] = info["workers"]
    output_json["number_of_process"] = size
    output_json["queries_path"] = config["queries_path"]
    output_json["corpus_index_path"] = config["corpus_index_path"]
    output_json["compare_mode"] = config["compare_mode"]
    
    if "granule_mode" in config and "threshold" in config:
        output_json["granule_mode"] = config["granule_mode"]
        output_json["threshold"] = config["threshold"]
        
    output_json["interpolated_precision"] = interpolated_precision
    output_json["hfm_sep_matrix"] = hfm_sep_matrix

    output_path = config["output_path"]

    output_file = open(output_path, "w")
    json.dump(output_json, output_file)
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
        interpolated_precision, hfm_sep_matrix, info = master(size, config)
        write_output_results(interpolated_precision, hfm_sep_matrix, info, config)
    else:
        worker(size, config)
    

if __name__ == "__main__":
    __main__(sys.argv[1:])
