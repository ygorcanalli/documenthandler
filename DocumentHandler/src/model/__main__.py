from __init__ import *
import sys
import getopt


# Read arguments from command line
def __main__(argv):
    input_file = ''
    output_file = ''
    operation = "dump"
    try:
        opts, args = getopt.getopt(argv, "bdhi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'model <-b|-d> -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'model <-b|-d> -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-b", "--backup"):
            operation = "backup"
        elif opt in ("-d", "--dump"):
            operation = "dump"

    if operation == "backup":
        document_backup(input_file, output_file)
    else:
        document_dump(input_file, output_file)


if __name__ == "__main__":
    __main__(sys.argv[1:])
