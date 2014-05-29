import sys
import getopt
from distance import Levenshtein
import model

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

    s_document = model.document_from_pkl(s_file)
    t_document = model.document_from_pkl(t_file)

    output_file = open(output_file, "w")
    output_string = "\n"

    # Get the paragraphs
    s_paragraphs = s_document.get_paragraphs()
    t_paragraphs = t_document.get_paragraphs()

    levenshtein = Levenshtein()

    # Iterata over all paragraphs of each book
    for i in range(0, len(s_paragraphs)):
        for j in range(0, len(t_paragraphs)):
            # Get the paragraphs
            s_paragraphsi = str(s_paragraphs.__getitem__(i))
            t_paragraphsi = str(t_paragraphs.__getitem__(j))

            # Call function
            parallel_result = str(levenshtein.parallel_alignment(s_paragraphsi,t_paragraphsi))

            #  results accumulation
            output_string += 'Distance(' + s_file[:-3] + '[' + str(i) + '], ' + t_file[:-3] + '['  + str(j) + ']) = ' + parallel_result + '\n'


    # analysis_string.join(analysis)
    output_file.write(output_string)

    output_file.close()

if __name__ == "__main__":
    __main__(sys.argv[1:])

print str(__doc__)