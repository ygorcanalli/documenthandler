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

CHAR_ALIGNMENT_MODE = "Char"
WORD_ALIGNMENT_MODE = "Word"
PARAGRAPH_BY_WORDS_ALIGNMENT_MODE = "Paragraph by words"
TRESHOLD = 0.04


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


def run_basic_compare(database_name, alignment_mode, alignment_function):
    start_time = time()

    # List files in database
    file_names = list_dir(database_name + "/pickled/", "*.pkl")

    pairs = []
    results = {}
    documents = {}
    results = {}
    results_str = ''

    total_read_time = 0
    total_alignment_time = 0

    pairs = create_non_repeating_list_of_pairs(file_names)

    # Load documents from pickle avoiding repeated documents
    for s_file_name, t_file_name in pairs:

        if not s_file_name in documents:
            documents[s_file_name] = model.document_from_pkl(database_name + "/pickled/" + s_file_name)

        if not t_file_name in documents:
            documents[t_file_name] = model.document_from_pkl(database_name + "/pickled/" + t_file_name)

        start_alignment_time = time()

        # Fill the result map with similaritys
        simil = run_alignment(alignment_mode, documents[s_file_name], documents[t_file_name], alignment_function)

        results[(s_file_name, t_file_name)] = simil

    end_time = time()
    spent_time = (end_time - start_time)

    print spent_time

    for s_file_name, t_file_name in results:
        results_str += "[" + s_file_name[:-4] + "]" + "[" + t_file_name[:-4] + "]=" + "%0.4f" % results[(s_file_name, t_file_name)] + "\n"
    
    # Recive info from workers
    info = []
    info.append("Alignment mode: " + alignment_mode)
    info.append("Comparasion Technique used: " + alignment_function.__name__)
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

    alignment_mode = PARAGRAPH_BY_WORDS_ALIGNMENT_MODE
    alignment_function = sequential_levenshtein

    try:
        opts, args = getopt.getopt(argv, "D:m:f:", ["database=","alignment_mode=", "alignment_function="])
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
                alignment_mode = CHAR_ALIGNMENT_MODE
            elif arg == "paragraph_by_words":
                alignment_mode = PARAGRAPH_BY_WORDS_ALIGNMENT_MODE
        elif opt in ("-f", "--alignment_function"):
            if arg == "sequential_levenshtein":
                alignment_function = sequential_levenshtein
            elif arg == "parallel_levenshtein":
                alignment_function = parallel_levenshtein

    info, results = run_basic_compare(database_name, alignment_mode, alignment_function)
    write_output_results(database_name, info, results)


if __name__ == "__main__":
    __main__(sys.argv[1:])