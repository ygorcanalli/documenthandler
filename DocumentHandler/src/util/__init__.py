__author__ = 'ygor'

from glob import glob
import os

def list_dir(directory_path, file_pattern):
    files = []

    os.chdir(directory_path)
    for file in glob(file_pattern):
        files.append(file)

    return files