import numpy as np


def divide_list(items, nb_lists):
    """Divides list into equal lists"""
    assert nb_lists > 0
    len_list = len(items)
    if nb_lists <= len_list:
        result = []
        ranges = np.linspace(0, len_list, num=nb_lists + 1)
        for i in range(len(ranges) - 1):
            result.append(items[int(ranges[i]):int(ranges[i + 1])])
    else:
        return [[full_list] for full_list in items]
    return result


def make_batches(items, nb_items_per_batch):
    return [items[i:i + nb_items_per_batch] for i in range(0, len(items), nb_items_per_batch)]


def append_to_dict_list(dic, key, item):
    """Appends an item to a list in a dictionary"""
    if key in dic:
        dic[key].append(item)
    else:
        dic[key] = [item]


def add_in_dict_set(dic, key, item):
    """Adds an item to a set in a dictionary"""
    if key in dic:
        dic[key].add(item)
    else:
        dic[key] = {item}


def append_in_dict_dict_list(dic, key1, key2, item):
    """Appends an item to a list in a dictionary of a dictionary"""
    if key1 in dic:
        if key2 in dic[key1]:
            dic[key1][key2].append(item)
        else:
            dic[key1][key2] = [item]
    else:
        dic[key1] = {key2: [item]}


def reverse_dict(dic):
    return {v: k for k, v in dic.items()}
