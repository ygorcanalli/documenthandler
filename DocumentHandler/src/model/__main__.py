from __init__ import *
import sys
import getopt


# Read arguments from command line
def __main__(argv):
    input_file = ''
    output_file = ''
    database_name = ''
    operation = "databasedump"
    try:
        opts, args = getopt.getopt(argv, "bdhi:o:D:", ["ifile=", "ofile=", "database="])
    except getopt.GetoptError:
        print('model <-b|-d> -i <inputfile> -o <outputfile> -D <databasename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('model <-b|-d> -i <inputfile> -o <outputfile> -D <databasename>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-b", "--backup"):
            operation = "backup"
        elif opt in ("-d", "--dump"):
            operation = "dump"
        elif opt in ("-D", "--database"):
            operation = "databasedump"
            database_name = arg

    if operation == "backup":
        document_backup(input_file, output_file)
    elif operation == "dump":
        document_dump(input_file, output_file)
    else:
        database_dump(database_name)


if __name__ == "__main__":
    __main__(sys.argv[1:])
