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
    corpus_index = util.list_dir(corpus_path, "*.pkl")
    
    pairs = []
    for query in queries:
        for document in corpus_index:
            pairs.append( (query, document) )
    return queries, corpus_index, pairs

def run_alignment(alignment_mode, query, document, alignment_function): 
    return None


def master(n_workers, config):
    
    queries_path = config["queries_path"]
    corpus_index_path = config["corpus_index_path"]
    
    target_path = config["target_path"]
    target = json.load(open(target_path, "r"))
    target = np.array(target)
        
    queries, corpus_index, pairs = create_list_of_pairs(queries_path, corpus_index_path)
    splited_workload = split_workload(pairs, n_workers)
    results = {}
    
    start_time = time() 
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
    for n_retrived in range(0, n_workers):
        info["workers"].append(comm.recv(source=MPI.ANY_SOURCE, tag=INFO))
    
    return interpolated_precision, hfm_sep_matrix, info


def worker(config):

    queries_path = config["queries_path"]
    corpus_index_path = config["corpus_index_path"]
    compare_mode = getattr(structural_similarity, config["compare_mode"])
    granule_mode = None
    threshold = None
        
    if "granule_mode" in config and "threshold" in config:
        granule_mode = getattr(structural_similarity, config["granule_mode"])
        threshold = config["threshold"]
        
    
    corpus_index = {}
    queries = {}
    results = {}
    spent_time = 0
    workload = comm.recv(source=0, tag=WORKLOAD)

    # Load corpus_index from pickle avoiding repeated corpus_index
    for query, document in workload:

        if not query in queries:
            queries[query] = model.document_from_pkl(os.path.join(queries_path, query))

        if not document in corpus_index:
            corpus_index[document] = model.document_from_pkl(os.path.join(corpus_index_path, document))

        # Fill the result map with similarities
        start_time = time()
        simil = compare_mode(queries[query], corpus_index[document], granule_alignment_funcion=granule_mode, threshold=threshold)        
        end_time = time()
        spent_time += (end_time - start_time)
        
        results[ (query, document) ] = simil

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
        interpolated_precision, hfm_sep_matrix, info = master(size - 1, config)
        write_output_results(interpolated_precision, hfm_sep_matrix, info, config)
    else:
        worker(config)
    

if __name__ == "__main__":
    __main__(sys.argv[1:])
