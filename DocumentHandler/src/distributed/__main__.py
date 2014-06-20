import sys
import os
import getopt

sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))
from util import *

from mpi4py import MPI
from time import time
from compare.distance import *
from compare.alignment import *
import model

# MPI initializations
comm   = MPI.COMM_WORLD            # MPI communicator
size   = comm.Get_size()           # Total number of processes
rank   = comm.Get_rank()           # Process rank
#name   = MPI.Get_processor_name()  # Processor identifier

WORKLOAD = 0
RESULTS = 1


def split_workload(workload, n_workers):
    len_workload = len(workload)
    workload_split_size = len_workload / n_workers
    remainder_workload = len_workload % n_workers
    splited_workload = []

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


def run_master(database_name, n_workers):
    
    start_time = time()
    splited_workload = []

    # List files in database
    file_names = list_dir(database_name + "/pickled/", "*.pkl")

    pairs = []
    results = {}

    # Create a non-repeating list of document pairs
    for i in range(0, len(file_names)):
        for j in range(i+1, len(file_names)):
	        pairs.append((file_names.__getitem__(i), file_names.__getitem__(j)))

    splited_workload = split_workload(pairs, n_workers)

    # Send workload to workers
    for i in range(0, n_workers):
        comm.send(splited_workload.__getitem__(i), dest = i + 1, tag=WORKLOAD)

    # Recive results and merge the result map
    for i in range(0, n_workers):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=RESULTS)
        results.update(worker_results)

    for s_file_name, t_file_name in results:
        print "[" + s_file_name[:-4] + "]" + "[" + t_file_name[:-4] + "]=" + "%0.4f" % results[(s_file_name, t_file_name)]

    end_time = time()
    spent_time = (end_time - start_time)

    print "\nSpend time: %0.4f s\n" % spent_time


def run_worker(database_name):
    documents = {}
    results = {}

    workload = comm.recv(source=0, tag=WORKLOAD)

    # Load documents from pickle avoiding repeated documents
    for s_file_name, t_file_name in workload:
        s_document = model.document_from_pkl(database_name + "/pickled/" + s_file_name)
        t_document = model.document_from_pkl(database_name + "/pickled/" + t_file_name)

        if not s_file_name in documents:
            documents[s_file_name] = model.document_from_pkl(database_name + "/pickled/" + s_file_name)

        if not t_file_name in documents:
            documents[t_file_name] = model.document_from_pkl(database_name + "/pickled/" + t_file_name)

    # Fill the result map with similaritys
    for s_file_name, t_file_name in workload:
        simil = align_words(documents[s_file_name], documents[t_file_name], sequential_levenshtein)
        results[(s_file_name, t_file_name)] = simil

    # Send result to master
    comm.send(results, 0, tag=RESULTS)


# Read arguments from command line
def __main__(argv):

    try:
        opts, args = getopt.getopt(argv, "D:o:w:", ["database=", "ofile="])
    except getopt.GetoptError:
        print 'model -D <database_path> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'model -D <database_path> -o <outputfile>'
            sys.exit()
        elif opt in ("-D", "--database"):
            database_name = arg
        elif opt in ("-o", "--outputfile"):
            output_file = arg 

    if rank == 0:
        run_master(database_name, size - 1)
    else:
        run_worker(database_name)


if __name__ == "__main__":
    __main__(sys.argv[1:])
