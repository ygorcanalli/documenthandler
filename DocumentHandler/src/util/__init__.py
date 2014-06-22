__author__ = 'ygor'

from glob import glob
import os

def list_dir(directory_path, file_pattern):
    files = []

    #get current directory
    current_directory = os.getcwd()

    #change current directory to path
    os.chdir(directory_path)
    for file in glob(file_pattern):
        files.append(file)

    #back to old current directory
    os.chdir(current_directory)

    return files
