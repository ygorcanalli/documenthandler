import sys
import os
import getopt
import datetime
from time import strftime

sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))
from util import *

from time import time
from compare.distance import *
from compare.alignment import *
import model


def run_basic_compare(database_name):
    start_time = time()

    # List files in database
    file_names = list_dir(database_name + "/pickled/", "*.pkl")

    pairs = []
    results = {}
    documents = {}
    results = {}
    results_str = ''

    # Create a non-repeating list of document pairs
    for i in range(0, len(file_names)):
        for j in range(i+1, len(file_names)):
	        pairs.append((file_names.__getitem__(i), file_names.__getitem__(j)))

    # Load documents from pickle avoiding repeated documents
    for s_file_name, t_file_name in pairs:
        if not s_file_name in documents:
            documents[s_file_name] = model.document_from_pkl(database_name + "/pickled/" + s_file_name)

        if not t_file_name in documents:
            documents[t_file_name] = model.document_from_pkl(database_name + "/pickled/" + t_file_name)

        # Fill the result map with similaritys
        simil = align_words(documents[s_file_name], documents[t_file_name], sequential_levenshtein)
        results[(s_file_name, t_file_name)] = simil

    end_time = time()
    spent_time = (end_time - start_time)

    for s_file_name, t_file_name in results:
        results_str += "[" + s_file_name[:-4] + "]" + "[" + t_file_name[:-4] + "]=" + "%0.4f" % results[(s_file_name, t_file_name)] + "\n"
    
    # Recive info from workers
    info = []
    info.append("Comparasion Technique used: Sequential Levenshtein")
    info.append("\n>>Wall time: %0.4f s\n" % spent_time)

    return info, results_str

def write_output_results(database_name, info, results):
    #convert info from workers and master in string
    info_str = '\n'.join(info)

    #merge util data    
    output_str = "Data base name: " + database_name
    output_str += "\n" + info_str
    output_str += "\nResults: \n" + results

    output_file_path = database_name + "/results"

    if not os.path.exists(output_file_path):
        os.mkdir(output_file_path)
    
    #get currents date and time
    now = datetime.datetime.now()
    formated_time = now.strftime("%Y_%m_%d_%H_%M_%S")

    output_file_name = "nodistributed_" + formated_time
   
    try:
        output_file = open(output_file_path + "/" + output_file_name, "w")
        output_file.write(output_str)
        output_file.close()
    except IOError: 
        print "Error writing results"


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

    info, results = run_basic_compare(database_name)
    write_output_results(database_name, info, results)


if __name__ == "__main__":
    __main__(sys.argv[1:])
