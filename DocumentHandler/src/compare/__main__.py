import sys
import getopt

import os

from distance import *
sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))

from model import *
from time import time
from util import *


# Read arguments from command line
def __main__(argv):
    s_file = ''
    t_file = ''
    operation = "compare_database"

    try:
        opts, args = getopt.getopt(argv, "D:s:t:o:", ["database=", "sfile=", "tfile=", "ofile="])
    except getopt.GetoptError:
        print 'model -s <stfile> -t <tfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'model -s <stfile> -t <tfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-s", "--sfile"):
            s_file = arg
            operation = "compare_pair"
        elif opt in ("-t", "--tfile"):
            t_file = arg
            operation = "compare_pair"
        elif opt in ("-D", "--database"):
            database_name = arg
            operation = "compare_database"
        elif opt in ("-o", "--outputfile"):
            output_file = arg


    output_file = open(output_file, "w")
    
    if operation == "compare_database":
        output_string = compare_database(database_name)
    else:
        output_string = compare_pair(s_file, t_file)
    
    output_file.write(output_string)
    output_file.close()

def compare_database(database_name):

    # List files in database
    file_names = list_dir(database_name + "/pickled/", "*.pkl")

    documents = []

    # Read the database
    for file_name in file_names:
       documents.append(document_from_pkl(file_name))

    header_string = 'Distances in database' + database_name + ':\n'
    output_string = ''

    levenshtein = Levenshtein()

    start_time = time()

    for i in range(0, len(documents)):
        for j in range(i+1, len(documents)):
            # Get the words
	    s_words = documents.__getitem__(i).get_words()
	    t_words = documents.__getitem__(j).get_words()

            s_len = len(s_words)
            t_len = len(t_words)

            # Call function
            distance = str(levenshtein.parallel_alignment(s_words.to_hash_list(), t_words.to_hash_list()))

	    simil = similarity(s_len, t_len, distance)

            # results accumulation
            output_string += '[' + file_names.__getitem__(i) + '][' + file_names.__getitem__(j) + ']=' + "%0.4f" % simil + '\n'
    
    end_time = time()
    spent_time = (end_time - start_time)

    time_string = "Spend time: %0.4f s\n" % spent_time

    output_string = header_string + time_string + output_string
    return output_string

def compare_pair(s_file, t_file):

    # Define the values of comparasion
    s_document = document_from_pkl(s_file)
    t_document = document_from_pkl(t_file)

    # Get the paragraphs
    s_paragraphs = s_document.get_paragraphs()
    t_paragraphs = t_document.get_paragraphs()

    header_string = 'Distance(' + s_file + ', ' + t_file + '):\n'
    output_string = ''

    levenshtein = Levenshtein()

    start_time = time()

    for i in range(0, len(s_paragraphs)):
        for j in range(i+1, len(t_paragraphs)):
            # Get the paragraphs
            s_paragraphsi = s_paragraphs.__getitem__(i)
            t_paragraphsi = t_paragraphs.__getitem__(j)

            s_words = s_paragraphsi.get_words()
            t_words = t_paragraphsi.get_words()

            s_len = len(s_words)
            t_len = len(t_words)

            # Call function
            distance = str(levenshtein.parallel_alignment(s_words.to_hash_list(), t_words.to_hash_list()))

            simil = similarity(s_len, t_len, distance)

            #  results accumulation
            output_string += '[' + str(i) + '][' + str(j) + ']=' + "%0.4f" % simil + '\n'

    end_time = time()
    spent_time = (end_time - start_time)

    time_string = "Spend time: %0.4f s\n" % spent_time

    output_string = header_string + time_string + output_string
    return output_string

if __name__ == "__main__":
    __main__(sys.argv[1:])
