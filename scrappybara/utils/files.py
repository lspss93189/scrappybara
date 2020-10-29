import bz2
import os
import pickle

import scrappybara.config as cfg


def path_exists(path):
    """Whether a file/directory exists"""
    return os.path.exists(path)


def files_in_dir(path):
    """Returns a list of filenames found in a directory"""
    return os.listdir(path)


def txt_file_reader(path):
    """Opens a text file"""
    return open(path, encoding=cfg.ENCODING)


def txt_file_writer(path):
    """Writes a text file"""
    return open(path, 'w', encoding=cfg.ENCODING)


def bz2_file_reader(path):
    """Opens compressed file .bz2"""
    return bz2.open(path, 'rt')


def bz2_file_bytes_reader(path):
    """Opens compressed file .bz2 in bytes mode"""
    return bz2.open(path, 'rb')


def load_pkl_file(path):
    """Loads pkl file & returns python object"""
    with open(path, 'rb') as pkl_file:
        return pickle.load(pkl_file)


def save_pkl_file(python_object, path):
    pickle.dump(python_object, open(path, 'wb'))


def load_set_from_txt_file(path):
    """Opens a txt file & loads each line into a set"""
    with txt_file_reader(path) as txt_file:
        return {line.strip() for line in txt_file}


def load_dict_from_txt_file(path):
    """Opens a txt file and loads tab-separated columns into a dictionary"""
    with txt_file_reader(path) as txt_file:
        return {key: value for key, value in [line.strip().split('\t') for line in txt_file]}
