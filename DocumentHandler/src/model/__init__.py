import os
import sys

from model import *
from model.container import *
from model.content import *
from util import *
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


def database_dump(database_name):
    plain_directory_name = os.path.join(database_name, "/plain/")
    pickled_directory_name = os.path.join(database_name, "/pickled/")
    for file_path in list_dir(plain_directory_name, "*.txt"):
        document_dump(os.path.join(plain_directory_name, file_path), os.path.join(pickled_directory_name, file_path.replace(".txt", ".pkl")))
