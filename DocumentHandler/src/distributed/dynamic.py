import sys
import os
import getopt
import datetime
from time import strftime

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
name   = MPI.Get_processor_name()  # Processor identifier
status = MPI.Status()              # MPI status

WORKLOAD = 0
RESULTS = 1
HAS_MORE_JOBS = 2
INFO = 3

CHAR_ALIGNMENT_MODE = "Char"
WORD_ALIGNMENT_MODE = "Word"
PARAGRAPH_BY_WORDS_ALIGNMENT_MODE = "Paragraph by words"

TRESHOLD = 0.04
INITIAL_WORKLOAD_SIZE = 1


def split_workload_defined_size(workload, size):
    splited_workload = []

    len_workload = len(workload)
    workload_split_size = len_workload / size
    remainder_workload = len_workload % size

    for i in range(0, workload_split_size):             
        begin = i * size
        end = begin + size
        splited_workload.append(workload[begin:end])

    if remainder_workload != 0:
        begin = i * size
        end = begin + remainder_workload
        splited_workload.append(workload[begin:end])        

    return splited_workload


def create_non_repeating_list_of_pairs(file_names):
    pairs = []
    for i in range(0, len(file_names)):
        for j in range(i+1, len(file_names)):
	        pairs.append((file_names.__getitem__(i), file_names.__getitem__(j)))
    return pairs


def run_alignment(alignment_mode, s_document, t_document, alignment_function):
    if alignment_mode == CHAR_ALIGNMENT_MODE:
        simil = align_chars(s_document, t_document, alignment_function)
    elif alignment_mode == WORD_ALIGNMENT_MODE:
        simil = align_words(s_document, t_document, alignment_function)
    elif alignment_mode == PARAGRAPH_BY_WORDS_ALIGNMENT_MODE:
        simil = align_paragraph_by_words(s_document, t_document, TRESHOLD, alignment_function)

    return simil


def run_dynamic_workloaded_master(database_name, n_workers):
    start_time = time()

    # List files in database
    file_names = list_dir(database_name + "/pickled/", "*.pkl")

    results = {}
    results_str = ''

    pairs = create_non_repeating_list_of_pairs(file_names)
    splited_workload = split_workload_defined_size(pairs, INITIAL_WORKLOAD_SIZE)

    len_workload = len(splited_workload)

    # Send initial workload to each worker
    for i in range(0, n_workers):
        comm.send(splited_workload.__getitem__(i), dest = i + 1, tag=WORKLOAD)

    #quantity of pairs (jobs) already assigned
    quantity_assigned_jobs = n_workers

    #Receive requests of more jobs and send more jobs
    while quantity_assigned_jobs < len_workload:

        request_more_jobs = comm.Iprobe(source=MPI.ANY_SOURCE, tag=HAS_MORE_JOBS, status=status)
        
        if request_more_jobs == True:
            comm.recv(source=MPI.ANY_SOURCE, tag=HAS_MORE_JOBS, status=status)
            comm.send(True, dest=status.Get_source(), tag=HAS_MORE_JOBS)

            next_job = quantity_assigned_jobs

            comm.send(splited_workload.__getitem__(next_job), dest=status.Get_source(), tag=WORKLOAD)
            quantity_assigned_jobs = quantity_assigned_jobs + 1

    # Sends message that no more jobs
    for i in range(0, n_workers):
        comm.send(False, dest = i + 1, tag=HAS_MORE_JOBS)

    # Recive results and merge the result map
    for i in range(0, n_workers):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=RESULTS)
        results.update(worker_results)

    end_time = time()
    spent_time = (end_time - start_time)

    for s_file_name, t_file_name in results:
        results_str += "[" + s_file_name[:-4] + "]" + "[" + t_file_name[:-4] + "]=" + "%0.4f" % results[(s_file_name, t_file_name)] + "\n"
    
    # Recive info from workers
    info = []
    for i in range(0, n_workers):
        info.extend(comm.recv(source=MPI.ANY_SOURCE, tag=INFO))

    info.append("\n>>Wall time: %0.4f s\n" % spent_time)

    return info, results_str


def run_dynamic_workloaded_worker(database_name, alignment_mode):
    start_time = time()

    documents = {}
    results = {}
    workload = []
   
    #flag indicating whether there are more jobs
    has_more_jobs = True

    while has_more_jobs == True:

        #Receive workload
        has_message = comm.Iprobe(source=0, tag=MPI.ANY_TAG, status=status)
        if has_message == True and status.Get_tag() == WORKLOAD:
            workload.extend(comm.recv(source=0, tag=WORKLOAD))

            # Load documents from pickle avoiding repeated documents            
            for s_file_name, t_file_name in workload:
                if not s_file_name in documents:
                    documents[s_file_name] = model.document_from_pkl(database_name + "/pickled/" + s_file_name)

                if not t_file_name in documents:
                    documents[t_file_name] = model.document_from_pkl(database_name + "/pickled/" + t_file_name)

                #Remove first element
                workload.pop(0)

                # Fill the result map with similaritys
                simil = run_alignment(alignment_mode, documents[s_file_name], documents[t_file_name], sequential_levenshtein)
                results[(s_file_name, t_file_name)] = simil

                #verify if has more jobs
                if len(workload) <= 1:
                    comm.isend(None, dest=0, tag=HAS_MORE_JOBS)
                    response_has_more_jobs = comm.Iprobe(source=0, tag=HAS_MORE_JOBS)
                    if response_has_more_jobs == True:
                        has_more_jobs = comm.recv(source=0, tag=HAS_MORE_JOBS)
                        workload.extend(comm.recv(source=0, tag=WORKLOAD))

        #verify the completetion of jobs
        elif has_message == True and status.Get_tag() == HAS_MORE_JOBS:
            has_more_jobs = comm.recv(source=0, tag=HAS_MORE_JOBS)

    # Send results to master
    comm.send(results, 0, tag=RESULTS)

    end_time = time()
    spent_time = (end_time - start_time)

    info = []
    info.append("---------------------------------------------------------------")
    info.append("Host name: " + name)
    info.append("Alignment mode: " + alignment_mode)
    info.append("Comparasion Technique used: Sequential Levenshtein")
    info.append("Spend time: %0.4f s\n" % spent_time)

    # Send info to master
    comm.send(info, 0, tag=INFO)


def write_output_results(database_name, info, results):
    #convert info from workers and master in string
    info_str = '\n'.join(info)

    #merge util data    
    output_str = "Data base name: " + database_name
    output_str += "\nNumber of MPI process: %d" % size
    output_str += "\n" + info_str
    output_str += "\nResults: \n" + results

    output_file_path = database_name + "/results"

    if not os.path.exists(output_file_path):
        os.mkdir(output_file_path)
    
    #get currents date and time
    now = datetime.datetime.now()
    formated_time = now.strftime("%Y_%m_%d_%H_%M_%S")

    output_file_name = "distributed_" + formated_time
   
    try:
        output_file = open(output_file_path + "/" + output_file_name, "w")
        output_file.write(output_str)
        output_file.close()
    except IOError: 
        print "Error writing results"


# Read arguments from command line
def __main__(argv):

    alignment_mode = PARAGRAPH_BY_WORDS_ALIGNMENT_MODE

    try:
        opts, args = getopt.getopt(argv, "D:w:m:", ["database=","alignment_mode="])
    except getopt.GetoptError:
        print 'no_distributed -D <database_path>'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'no_distributed -D <database_path>'
            sys.exit()
        elif opt in ("-D", "--database"):
            database_name = arg
        elif opt in ("-m", "--alignment_mode"):
            if arg == "word":
                alignment_mode = WORD_ALIGNMENT_MODE
            elif arg == "char":
                alignment_mode == CHAR_ALIGNMENT_MODE
            elif arg == "paragraph_by_words":
                alignment_mode = PARAGRAPH_BY_WORDS_ALIGNMENT_MODE

    if rank == 0:
        info, results = run_dynamic_workloaded_master(database_name, size - 1)
        write_output_results(database_name, info, results)
    else:
        run_dynamic_workloaded_worker(database_name, alignment_mode)


if __name__ == "__main__":
    __main__(sys.argv[1:])
