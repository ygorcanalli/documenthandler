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
NO_MORE_JOBS = 3
INFO = 4

CHAR_ALIGNMENT_MODE = "Char"
WORD_ALIGNMENT_MODE = "Word"
PARAGRAPH_BY_WORDS_ALIGNMENT_MODE = "Paragraph by words"

TRESHOLD = 0.04

# Create a list of pair with size INITIAL_WORKLOAD_SIZE popping from workload
def pop_workload(pairs, size):
    popped_workload = []
    i = 0
    while (len(pairs) > 0 and i < size):
        popped_workload.append(pairs.pop())
        i = i +1
    return popped_workload


def create_list_of_pairs(document_names):
    pairs = []
    for i in range(0, len(document_names)):
        for j in range(i+1, len(document_names)):
            pairs.append((document_names.__getitem__(i), document_names.__getitem__(j)))
    return pairs


def run_alignment(alignment_mode, query, document, alignment_function):
    if alignment_mode == CHAR_ALIGNMENT_MODE:
        simil = align_chars(query, document, alignment_function)
    elif alignment_mode == WORD_ALIGNMENT_MODE:
        simil = align_words(query, document, alignment_function)
    elif alignment_mode == PARAGRAPH_BY_WORDS_ALIGNMENT_MODE:
        simil = align_paragraph_by_words(query, document, TRESHOLD, alignment_function)

    return simil


def run_dynamic_workloaded_master(database_name, n_workers, initial_workload_size, dynamic_workload_size):
    start_time = time()

    # List files in database
    file_names = list_dir(database_name + "/pickled/", "*.pkl")

    results = {}
    results_str = ''
    splited_workload = []

    pairs = create_list_of_pairs(file_names)

    # Send initial workload to each worker
    for i in range(0, n_workers):
        splited_workload = pop_workload(pairs, initial_workload_size)
        if len(splited_workload) > 0:
            comm.send(splited_workload, dest = i + 1, tag=WORKLOAD)

    #Receive requests of more jobs and send then
    while (len(pairs) > 0): 
        comm.recv(source=MPI.ANY_SOURCE, tag=HAS_MORE_JOBS, status=status)
        next_job = pop_workload(pairs, dynamic_workload_size)
        comm.send(next_job, dest=status.Get_source(), tag=WORKLOAD)

    # Sends message that no more jobs
    for i in range(0, n_workers):
        comm.send(None, dest = i + 1, tag=NO_MORE_JOBS)

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
   
    #flag indicating whether there are more jobs in master
    has_more_jobs = True
    
    #flag indicain that thare is a workload asking in coming
    has_workload_asking_in_coming = False
    
    #recive initial workload
    recived_workload = comm.recv(source=0, tag=WORKLOAD)
    workload.extend(recived_workload)
      
    while (len(workload) > 0):
        #retrive the pair from workload
        s_file_name, t_file_name = workload.pop()
        
        #load the pair from disk
        if not s_file_name in documents:
            documents[s_file_name] = model.document_from_pkl(database_name + "/pickled/" + s_file_name)

        if not t_file_name in documents:
            documents[t_file_name] = model.document_from_pkl(database_name + "/pickled/" + t_file_name)
        
        #process the job 
        simil = run_alignment(alignment_mode, documents[s_file_name], documents[t_file_name], sequential_levenshtein)
        results[(s_file_name, t_file_name)] = simil
        
    
        #non blocking message asking for workload 
        if (not has_workload_asking_in_coming) and has_more_jobs:
#            if len(workload) > 0:
            comm.isend(None, dest=0, tag=HAS_MORE_JOBS)
#            else:
#                comm.send(None, dest=0, tag=HAS_MORE_JOBS)
            has_workload_asking_in_coming = True
            
        #verify if there is a answer
        if has_more_jobs:
            if len(workload) > 0:
                has_message = comm.Iprobe(source=0, tag=MPI.ANY_TAG, status=status)

                #verify the type of message
                if has_message == True and status.Get_tag() == WORKLOAD:
                    workload.extend(comm.recv(source=0, tag=WORKLOAD))
                    has_workload_asking_in_coming = False
                elif has_message == True and status.Get_tag() == NO_MORE_JOBS:
                    has_more_jobs = False
            else:
                message = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
                if (status.Get_tag() == WORKLOAD):
                    workload.extend(message)
                    has_workload_asking_in_coming = False
                elif (status.Get_tag() == NO_MORE_JOBS):
                    has_more_jobs = False


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


def write_output_results(documents_database_name, info, analysis):
    #convert info from workers and master in string
    info_str = '\n'.join(info)

    #merge util data    
    output_str = "Data base name: " + documents_database_name
    output_str += "\nNumber of MPI process: %d" % size
    output_str += "\n" + info_str
    output_str += "\nResults: \n" + analysis

    output_file_path = documents_database_name + "/analysis"

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
        print "Error writing analysis"


# Read arguments from command line
def __main__(argv):

    initial_workload_size = 1
    dynamic_workload_size = 1
    alignment_mode = PARAGRAPH_BY_WORDS_ALIGNMENT_MODE

    try:
        opts, args = getopt.getopt(argv, "D:m:i:d:", ["database=","alignment_mode=","initial_workload=","dynamic_workload="])
    except getopt.GetoptError:
        print 'no_distributed -D <database_path> -m <alignment_mode> -i <initial_workload> -d <dynamic_workload>'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'no_distributed -D <database_path> -m <alignment_mode> -i <initial_workload> -d <dynamic_workload>'
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
        elif opt in ("-i", "--initial_workload"):
            initial_workload_size = int(arg)
        elif opt in ("-d", "--dynamic_workload"):
            dynamic_workload_size = int(arg)

    if rank == 0:
        info, results = run_dynamic_workloaded_master(database_name, size - 1, initial_workload_size, dynamic_workload_size)
        write_output_results(database_name, info, results)
    else:
        run_dynamic_workloaded_worker(database_name, alignment_mode)


if __name__ == "__main__":
    __main__(sys.argv[1:])
