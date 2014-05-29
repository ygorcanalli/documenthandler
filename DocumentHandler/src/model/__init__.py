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

    return document
