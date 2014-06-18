import pickle
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))

from model import *
from model.container import *
from model.content import *
from util import *


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
    plain_directory_name = database_name + "/plain/"
    pickled_directory_name = database_name + "/pickled/"
    for file in list_dir(plain_directory_name, "*.txt"):
        document_dump(plain_directory_name + file, pickled_directory_name + file[:-3] + "pkl")