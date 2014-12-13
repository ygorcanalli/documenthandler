from __future__ import division
import sys
import os
import getopt
import datetime
from time import strftime
from pprint import pprint, pformat
sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))

from util import *
import util.meter_handler as meter_handler 
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
    
    for i in xrange(0, 11):
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
    for i in xrange(0, 11):
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

"""
def create_list_of_pairs(query_database_name, document_database_name):
    # List files in database
    query_names = list_dir(query_database_name + "/pickled/", "*.pkl")
    document_names = list_dir(document_database_name + "/pickled/", "*.pkl")
    
    pairs = []
    for q in query_names:
        for d in document_names:
            pairs.append( (q, d) )
    return pairs
"""

def create_list_of_pairs(queries, documents):
    # List files in database
    #queries_path = list_dir(query_database_name + "/pickled/", "*.pkl")
    #documents_path = list_dir(document_database_name + "/pickled/", "*.pkl")
    
    pairs = []
    for q in queries:
        for d in documents:
            pairs.append( (meter_handler.pickled_path(q), meter_handler.pickled_path(d)) )
    return pairs

def run_alignment(alignment_mode, query, document, alignment_function): 
    return None


def master(n_workers, config):
    
    database_root_path = config["database_root_path"]
    
    start_time = time()
    splited_workload = []   

    pairs = []
    analysis = {}
    analysis_str = ''
    
    wholly_derived = set()
    partial_derived = set()
    non_derived = set()

    queries, relevants = meter_handler.get_queries_path(database_root_path)
    documents = meter_handler.get_documents_path(database_root_path)
        
    pairs = create_list_of_pairs(queries, documents)
    
    splited_workload = split_workload(pairs, n_workers)

    # Send workload to workers
    for n_retrived in range(0, n_workers):
        comm.send(splited_workload.__getitem__(n_retrived), dest = n_retrived + 1, tag=WORKLOAD)

    # Receive analysis and merge the result map
    for n_retrived in range(0, n_workers):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=RESULTS)
        analysis.update(worker_results)

    end_time = time()
    spent_time = (end_time - start_time)

    print spent_time

    queries_results = {}
    
    for query_file_name, document_file_name in analysis:
        
        real_name_query = meter_handler.real_path(query_file_name)
        real_name_document = meter_handler.real_path(document_file_name)
        
        if not queries_results.has_key(real_name_query):
            queries_results[real_name_query] = []
        
        # store query results for ranking
        simil = analysis[(query_file_name, document_file_name)]
        queries_results[real_name_query].append( (real_name_document, simil) )
        
    precision_recall_map = {}
    interpolate_precisions_list = []
    
    #sort results
    for query, query_result in queries_results.iteritems(): 
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
            if not precision_recall_map[query].has_key(recall):
                precision_recall_map[query][recall] = precision
            else:
                precision_recall_map[query][recall] = max(precision_recall_map[query][recall],precision)
            

            n_retrived += 1
            
        analysis_str +=  "\n------------------Query------------------\n" + query + "\nResults:\t" + pformat(query_result) + "\nPrecision recall map:\t" + pformat(precision_recall_map[query])
        
        # store the interpolated precision for each query
        interpolate_precisions_list.append(interpolated_precision_recall(precision_recall_map[query]))
    
    average_interpolated_precision = average_interpolated_precision_recall(interpolate_precisions_list)
           
    # Recive info from workers
    info = []
    for n_retrived in range(0, n_workers):
        info.extend(comm.recv(source=MPI.ANY_SOURCE, tag=INFO))

    info.append("\nTime: %0.4f s\n" % spent_time)
    info.append("\n\nAverage interpolated precision by recall: " + str(average_interpolated_precision))

    return info, analysis_str


def worker(config):

    database_root_path = config["database_root_path"]
    compare_mode = getattr(structural_similarity, config["compare_mode"])
    granule_mode = None
    threshold = None
        
    if config.has_key("granule_mode") and config.has_key("threshold"):
        granule_mode = getattr(structural_similarity, config["granule_mode"])
        threshold = config["threshold"]
        
    
    documents = {}
    queries = {}
    results = {}

    start_time = time()

    workload = comm.recv(source=0, tag=WORKLOAD)

    # Load documents from pickle avoiding repeated documents
    for q, d in workload:

        if not q in queries:
            queries[q] = model.document_from_pkl(database_root_path + q)

        if not d in documents:
            documents[d] = model.document_from_pkl(database_root_path + d)

        # Fill the result map with similaritys
        simil = compare_mode(queries[q], documents[d], granule_alignment_funcion=granule_mode, threshold=threshold)        
        
        results[(q, d)] = simil

    # Send result to master
    comm.send(results, 0, tag=RESULTS)

    end_time = time()
    spent_time = (end_time - start_time)

    info = []
    info.append("---------------------------------------------------------------")
    info.append("Host name: %s rank: %d" % (name, rank)) 
    info.append("Compare mode: " + compare_mode.__name__)
    
    if granule_mode != None and threshold != None:
        info.append("Granule mode: " + granule_mode.__name__)
        info.append("Threshold: " + str(threshold))
        
    info.append("Spend time: %0.4f s\n" % spent_time)

    # Send info to master
    comm.send(info, 0, tag=INFO)
    

def write_output_results(info, analysis, config):
    #convert info from workers and master in string
    info_str = '\n'.join(info)

    database_root_path = config["database_root_path"]
    
    #merge util data
    output_str = "Database root path: " + database_root_path
    output_str += "\nNumber of MPI process: %d" % size
    output_str += "\n" + info_str
    output_str += "\nAnalysis: \n" + analysis

        #get currents date and time
    now = datetime.datetime.now()
    formated_time = now.strftime("%Y_%m_%d_%H_%M_%S")

    output_file_path = database_root_path + "/documenthandler/results/" + formated_time

    output_file = open(output_file_path, "w")
    output_file.write(output_str)
    output_file.close()     
    

# Read arguments from command line
def __main__(argv):
    
    try:
        opts, args = getopt.getopt(argv, "c:", ["config_file="])
    except getopt.GetoptError:
        print 'Illegal arguments'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'no_distributed -D <database_path>'
            sys.exit()
        elif opt in ("-c", "--config_file"):
            config_file = open(arg, "r")
            configs = json.load(config_file)
            config_file.close()
    
    for config in configs:
        if rank == 0:
            info, analysis = master(size - 1, config)
            write_output_results(info, analysis, config)
        else:
            worker(config)
    

if __name__ == "__main__":
    __main__(sys.argv[1:])