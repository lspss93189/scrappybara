import pickle

import scrappybara.config as cfg


def file_path(*args):
    """Returns the file's absolute Path object.
    If the file is located in subfolders of the data folder, pass each subfolder as an arg.
    The last arg is the actual filename.
      e.g. if the file is located at "[path_to_data]/sub_folder/file.txt", call file_path('sub_folder', 'file.txt')
    """
    path = cfg.HOME_DIR
    for arg in args:
        path /= arg
    return path


def txt_file_reader(*args):
    """Opens a txt file"""
    return open(file_path(*args), encoding=cfg.ENCODING)


def txt_file_writer(*args):
    """Writes a txt file"""
    return open(file_path(*args), 'w', encoding=cfg.ENCODING)


def load_pkl_file(*args):
    """Loads pkl file & returns python object"""
    with open(file_path(*args), 'rb') as pkl_file:
        return pickle.load(pkl_file)


def save_pkl_file(python_object, *args):
    pickle.dump(python_object, open(file_path(*args), 'wb'))


def load_set_from_txt_file(*args):
    """Opens a txt file & loads each line into a set"""
    with txt_file_reader(*args) as txt_file:
        return {line.strip() for line in txt_file}


def load_dict_from_txt_file(*args):
    """Opens a txt file and loads tab-separated columns into a dictionary"""
    with txt_file_reader(*args) as txt_file:
        return {key: value for key, value in [line.strip().split('\t') for line in txt_file]}
