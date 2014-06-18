import sys
import getopt

import os

from distance import Levenshtein

sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))

from model import *
import model.container
import model.content
from time import time


# Read arguments from command line
def __main__(argv):
    s_file = ''
    t_file = ''

    try:
        opts, args = getopt.getopt(argv, "s:t:o:", ["sfile=", "tfile=", "ofile="])
    except getopt.GetoptError:
        print 'model -s <stfile> -t <tfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'model -s <stfile> -t <tfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-s", "--sfile"):
            s_file = arg
        elif opt in ("-t", "--tfile"):
            t_file = arg
        elif opt in ("-o", "--outputfile"):
            output_file = arg

    # Define the values of comparasion

    s_document = document_from_pkl(s_file)
    t_document = document_from_pkl(t_file)

    output_file = open(output_file, "w")
    header_string = 'Distance(' + s_file + ', ' + t_file + '):\n'
    output_string = ''

    #output_list = []
	
    # Get the paragraphs
    s_paragraphs = s_document.get_paragraphs()
    t_paragraphs = t_document.get_paragraphs()

    start_time = time()

    levenshtein = Levenshtein()

    # Iterata over all paragraphs of each book
    for i in range(0, len(s_paragraphs)):
        for j in range(i+1, len(t_paragraphs)):
            # Get the paragraphs
            s_paragraphsi = s_paragraphs.__getitem__(i)
            t_paragraphsi = t_paragraphs.__getitem__(j)

            s_words = s_paragraphsi.get_words()
            t_words = t_paragraphsi.get_words()
            # Call function
            print len(s_paragraphsi), len(t_paragraphsi) 

            parallel_result = str(levenshtein.parallel_alignment(s_words.to_hash_list(), t_words.to_hash_list()))

            #  results accumulation
            output_string += '[' + str(i) + '][' + str(j) + ']=' + parallel_result + '\n'

	    for word in s_words:
		output_string += str(word) + '\n'

	    output_string += '\n\n'

            for word in t_words:
		output_string += str(word) + '\n'

    end_time = time()
    spent_time = (end_time - start_time)

    time_string = "Spend time: %0.4f s\n" % spent_time
    
    #output_string.join(output_list)
    output_string = header_string + time_string + output_string

    # analysis_string.join(analysis)
    output_file.write(output_string)

    output_file.close()

if __name__ == "__main__":
    __main__(sys.argv[1:])
