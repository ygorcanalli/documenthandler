import sys
import os
import getopt
import datetime
from time import strftime
from pprint import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))

from util import *
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

TRESHOLD = 0.8


def split_workload(workload, n_workers):

    splited_workload = []

    len_workload = len(workload)
    workload_split_size = len_workload / n_workers
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


def create_list_of_pairs(query_database_name, document_database_name):
    # List files in database
    query_names = list_dir(query_database_name + "/pickled/", "*.pkl")
    document_names = list_dir(document_database_name + "/pickled/", "*.pkl")
    
    pairs = []
    for q in query_names:
        for d in document_names:
	        pairs.append( (q, d) )
    return pairs


def run_alignment(alignment_mode, query, document, alignment_function): 
    return None


def master(query_database_name, document_database_name, n_workers, config):
    
    start_time = time()
    splited_workload = []

    wholly_derived_boundary = config["wholly_derived_boundary"]
    partial_derived_boundary = config["partial_derived_boundary"]
    

    pairs = []
    analysis = {}
    analysis_str = ''
    
    wholly_derived = set()
    partial_derived = set()
    non_derived = set()

    pairs = create_list_of_pairs(query_database_name, document_database_name)
    splited_workload = split_workload(pairs, n_workers)

    # Send workload to workers
    for i in range(0, n_workers):
        comm.send(splited_workload.__getitem__(i), dest = i + 1, tag=WORKLOAD)

    # Receive analysis and merge the result map
    for i in range(0, n_workers):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=RESULTS)
        analysis.update(worker_results)

    end_time = time()
    spent_time = (end_time - start_time)

    print spent_time

    for query_file_name, document_file_name in analysis:
        analysis_str +=  query_file_name + "\n" + document_file_name + "\n%0.4f\n" % analysis[(query_file_name, document_file_name)] + "\n"
        
        # Classify results
        if analysis[(query_file_name, document_file_name)] >= wholly_derived_boundary:
            wholly_derived.add(query_file_name)
        elif analysis[(query_file_name, document_file_name)] >= partial_derived_boundary and analysis[(query_file_name, document_file_name)] < wholly_derived_boundary:
            partial_derived.add(query_file_name)
        else:
            non_derived.add(query_file_name)
    
    # remove from non_derived documents that was classifed as derived 
    non_derived.difference_update(partial_derived)
    non_derived.difference_update(wholly_derived)
    
    # remove from partial derived documents that was classifid as wholly derived
    partial_derived.difference_update(wholly_derived)
    
    # Recive info from workers
    info = []
    for i in range(0, n_workers):
        info.extend(comm.recv(source=MPI.ANY_SOURCE, tag=INFO))

    info.append("\nTime: %0.4f s\n" % spent_time)

    return info, analysis_str, "\n".join(wholly_derived), "\n".join(partial_derived), "\n".join(non_derived)


def worker(queries_database_name, documents_database_name, config):

    wholly_derived_boundary = config["wholly_derived_boundary"]
    partial_derived_boundary = config["partial_derived_boundary"]
    compare_mode = getattr(structural_similarity, config["compare_mode"])
    granule_mode = None
    threshold = None
        
    if config.has_key("granule_mode") and config.has_key(threshold):
        granule_mode = getattr(structural_similarity, config["granule_mode"][0])
        threshold = config["threshold"][0]
        
    
    documents = {}
    queries = {}
    results = {}

    start_time = time()

    workload = comm.recv(source=0, tag=WORKLOAD)

    # Load documents from pickle avoiding repeated documents
    for q, d in workload:

        if not q in queries:
            queries[q] = model.document_from_pkl(queries_database_name + "/pickled/" + q)

        if not d in documents:
            documents[d] = model.document_from_pkl(documents_database_name + "/pickled/" + d)


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
    info.append("Wholly derived boundary: " + str(wholly_derived_boundary))
    info.append("Partial derived boundary: " + str(partial_derived_boundary))
    info.append("Compare mode: " + compare_mode.__name__)
    
    if granule_mode != None and threshold != None:
        info.append("Granule mode: " + granule_mode.__name__)
        info.append("Threshold: " + str(threshold))
        
    info.append("Spend time: %0.4f s\n" % spent_time)

    # Send info to master
    comm.send(info, 0, tag=INFO)
    

def write_output_results(queries_database_name, documents_database_name, info, analysis, wholly_derived, partial_derived, non_derived):
    #convert info from workers and master in string
    info_str = '\n'.join(info)

    #merge util data
    output_str = "Queries database name: " + queries_database_name
    output_str = "Documents database name: " + documents_database_name
    output_str += "\nNumber of MPI process: %d" % size
    output_str += "\n" + info_str
    output_str += "\nAnalysis: \n" + analysis

        #get currents date and time
    now = datetime.datetime.now()
    formated_time = now.strftime("%Y_%m_%d_%H_%M_%S")

    output_file_path = queries_database_name + "/results/" + formated_time

    if not os.path.exists(output_file_path):
        os.mkdir(output_file_path)
    
    try:
        output_file = open(output_file_path + "/analysis", "w")
        output_file.write(output_str)
        output_file.close()
        
        output_file = open(output_file_path + "/wholly_derived", "w")
        output_file.write(wholly_derived)
        output_file.close()
        
        output_file = open(output_file_path + "/partial_derived", "w")
        output_file.write(partial_derived)
        output_file.close()
        
        output_file = open(output_file_path + "/non_derived", "w")
        output_file.write(non_derived)
        output_file.close()
    except IOError: 
        print "Error writing analysis"

# Read arguments from command line
def __main__(argv):

    config = {}
    
    try:
        opts, args = getopt.getopt(argv, "Q:D:c:", ["queries_database_name=""documents_database_name=","config_file="])
    except getopt.GetoptError:
        print 'Illegal arguments'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'no_distributed -D <database_path>'
            sys.exit()
        elif opt in ("-Q", "--queries_database_name"):
            queries_database_name = arg
        elif opt in ("-D", "--documents_database_name"):
            documents_database_name = arg
        elif opt in ("-c", "--config_file"):
            config_file = open(arg, "r")
            config = json.load(config_file)
            config_file.close()
    
    if rank == 0:
        info, analysis, wholly_derived, partial_derived, non_derived = master(queries_database_name, documents_database_name, size - 1, config)
        write_output_results(queries_database_name, documents_database_name, info, analysis, wholly_derived, partial_derived, non_derived)
    else:
        worker(queries_database_name, documents_database_name, config)
    

if __name__ == "__main__":
    __main__(sys.argv[1:])
