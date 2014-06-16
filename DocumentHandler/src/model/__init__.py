from content import *
from container import *
import pickle

def document_dump(input_file_name, output_file_name):
    input_file = open(input_file_name, "r")
    document = Content.create_document(input_file.read())
    input_file.close()

    output_file = open(output_file_name, "wb")
    pickle.dump(document, output_file)
    output_file.close()


def document_backup(input_file_name, output_file_name):
    input_file = open(input_file_name, "rb")
    document = pickle.load(input_file)
    input_file.close()

    output_file = open(output_file_name, "w")
    output_file.write(str(document))
    output_file.close()

def document_from_pkl(input_file_name):
    input_file = open(input_file_name, "rb")
    document = pickle.load(input_file)
    input_file.close()

<<<<<<< HEAD
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
=======
    return document
>>>>>>> be73cb6a5c70356aadf12876d6a9d48793e43353
