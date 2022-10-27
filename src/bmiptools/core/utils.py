# Title: 'tmp_tf_utils.py'
# Date: 27/01/21
# Author: Curcuraci L.
#
# Scope: This file contain various generic core functions.

"""
Generic utility functions
"""


#################
#####   LIBRARIES
#################


import numpy as np
import os
import shutil
import glob
import warnings
import benedict
import json
import operator
from exifread.utils import Ratio
from functools import reduce
from distutils.dir_util import copy_tree


#################
#####   FUNCTIONS
#################


### Generic core


def manage_path(path):
    """
    Check if all the folders specified in a given path exist and if not it creates them. This is done in OS
    independent way.

    P.A.: the string in the path field must be RAW! You can easily do that just adding "r" in
    front of the string of the path, e.g.

             [naive string of the path]       ->       [raw string of the path]

        'home/folder1/folder2/file.extension' -> r'home/folder1/folder2/file.extension'

    If this is not done, escape characters may alter the path of the function.

    :param path: RAW string containing the path possibly with file (put an "r" in front of the string!)
    :return: the normalized path
    """
    path = os.path.normpath(path)
    path_to_check = path
    if path.split(os.sep)[-1].find('.')>-1:

        path_to_check = path[:path.find(os.sep+path.split(os.sep)[-1])]

    os.makedirs(path_to_check,exist_ok=True)
    return path

# def delete_folder_and_its_content(folder):
#     """
#     Delete folder and all its contents (either folders and files).
#
#     :param folder: (raw str) raw string containing the path to the folder to delete with its content.
#     """
#     N_files_to_delete = len(os.listdir(folder))
#     removed_files = []
#     for n,filename in enumerate(os.listdir(folder)):
#
#         file_path = os.path.join(folder,filename)
#         try:
#
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#
#                 os.unlink(file_path)
#
#             elif os.path.isdir(file_path):
#
#                 shutil.rmtree(file_path)
#
#             removed_files.append(n)
#
#         except Exception as e:
#
#             # print('Failed to delete %s. Reason: %s' % (file_path, e))
#             warnings.warn('Failed to delete {}. Reason: {}'.format(file_path, e))
#
#     if N_files_to_delete == len(removed_files):
#
#         shutil.rmtree(folder)

def delete_folder_and_its_content(folder):
    """
    Delete folder and all its contents (either folders and files).

    :param folder: (raw str) raw string containing the path to the folder to delete with its content.
    """

    objects_found = glob.glob(folder,recursive=True)
    file_to_delete = []
    directory_to_delete = []
    for obj_path in objects_found:

        if os.path.isdir(obj_path):

            directory_to_delete.append(obj_path)

        else:

            file_to_delete.append(obj_path)

    for file_path in file_to_delete:

        try:

            os.unlink(file_path)

        except Exception as e:

            warnings.warn('Failed to delete the file {}. Reason: {}'.format(file_path, e))

    dept = [len(path.split(os.sep)) for path in directory_to_delete]
    dept_ordered_directory_to_delete = \
        [list(tpl) for tpl in zip(*sorted(zip(dept,directory_to_delete),reverse=True))][1]
    for dir_path in dept_ordered_directory_to_delete:

        try:

            shutil.rmtree(dir_path)

        except Exception as e:

            warnings.warn('Failed to delete the folder{}. Reason: {}'.format(dir_path, e))

def copy_folder_and_its_content(folder_to_copy_path, copy_destination_path):
    """
    Copy a folder and all its content in a given destination. Only folders can be copied with this function!

    :param folder_to_copy_path: (raw str) path to the folder to copy.
    :param copy_destination_path: (raw str) path of the copy.
    """
    if os.path.isdir(folder_to_copy_path):

        copy_destination_path = manage_path(copy_destination_path + os.sep + os.path.basename(folder_to_copy_path))
        copy_tree(folder_to_copy_path, copy_destination_path,preserve_symlinks=1)

    else:

        warnings.warn('The path {} does not point to a folder. '
                      'Therefore it was not copied.'.format(folder_to_copy_path))

def standard_number(number,n_digits=4):
    """
    Standardize the string containing numbers to avoid subsequent ordering problem

    :param number: (integer) number to standardize.
    :param n_digits: (integer) maximum number of digits used.
    :return: a standardized string containing the number.
    """
    n_zeros_in_front = n_digits - len(str(number))
    res = str(number)
    for _ in range(n_zeros_in_front):

        res = '0' + res

    return res

def set_in_a_nested_dict(adict, key, value):
    """
    Set the value of a given final key in a nested dictionary. Note that for duplicate key names in the nested
    dictionary the value will be changed for all the keys. By final-key we mean the key in a nested dictionary
    whose values are not dictionary.

    :param adict: (dict) nested dictionary.
    :param key: (str) key to change in the nested dictionary.
    :param value: (any except dict) value to set.
    :return: (dict) updated nested dictionary.
    """
    b_adict = benedict.benedict(adict, keypath_separator='.')
    fb_adict = b_adict.flatten(separator='#')
    for keypath in list(fb_adict.keys()):

        if key in keypath:

            fb_adict[keypath] = value

    ufb_adict = fb_adict.unflatten(separator='#')
    new_dict = json.loads(ufb_adict.to_json())
    return new_dict

def list_to_string(l, sep=', '):
    """
    Given a list of numbers/string it produces a string where the list elements are separated by the separator
    specified in 'sep'.

    :param l: input list.
    :param sep: (optional) separator character(s) used between the element of a string.
    """
    string = ''
    for el in l:

        string = string + str(el) + sep

    return string[:-len(sep)]

def write(x,verbosity):
    """
    Verbosity controlled print.

    :param x: (str) string to print.
    :param verbosity: (int) if 1 the content of x is printed, otherwise not.
    """
    if verbosity == 1:

        print(x)

def isfloat(x):
    """
    Check if a (real) number is float or not.

    :param x: (numeric) number to check
    :return: (boolean) True if can only be represented as float, False if it can be also represented exactly as int.
    """
    if x - int(x) == 0:

        return False

    else:

        return True

def read_global_setting(path):
    """
    Read the 'global_setting.txt' file.

    :param path: pat to the 'global_setting.txt' file.
    :return: a dictionary containing the global setting.
    """
    global_setting = {}
    with open(path,'r') as txtfile:

        for line in txtfile:

            tmp = line.split(' = ')
            tmp[1] = tmp[1].replace('\n','')
            if tmp[1].isdecimal():

                tmp[1] = float(tmp[1])
                if not isfloat(tmp[1]):

                    tmp[1] = int(tmp[1])

            global_setting[tmp[0]] = tmp[1]

    return global_setting

def set_option_in_global_setting(setting_name,setting_value,path):
    """
    Set a generic option in the 'global_setting.txt'

    :param setting_name: (str) name of the option to set.
    :param setting_value: (str/float/int) value of the option to set.
    :param path: path to the 'global_setting.txt' file.
    """
    with open(path, 'r') as txtfile:

        buffer = []
        for line in txtfile:

            if line.find(setting_name) >= 0:

                components = line.split(' = ')
                if components[1].find('\n') >= 0:

                    end_char = '\n'

                else:

                    end_char = ''

                if str(setting_value).isdecimal():

                    if not isfloat(setting_value):

                        setting_value = int(setting_value)

                components[1] = str(setting_value)
                line = components[0] + ' = ' + components[1] + end_char

            buffer.append(line)

    with open(path, 'w') as txtfile:

        for line in buffer:

            txtfile.write(line)


def get_branch_of_key_tree(d):
    """
    Returns the list of all the keys in a dictionary (possibly with nested dictionary) reflecting the actual
    key hierarchy, e.g. given

        {'a': val1,'b': {'c': val2,'d': val3},'e': val4}

    then

        [['a'],['b','c'],['b','d'],['e']]

    is returned.

    :param d: dictionary to analyze
    """

    def get_nested_keys(d, keys, prefix):
        """
        based on https://stackoverflow.com/questions/26166910/get-a-list-of-all-keys-in-nested-dictionary
        """
        for k, v in d.items():

            if isinstance(v, dict):

                get_nested_keys(v, keys, f'{prefix}:{k}')

            else:

                keys.append(f'{prefix}:{k}')

    keys_list = []
    get_nested_keys(d, keys_list, '')
    return [el[1:].split(':') for el in keys_list]

def get_by_path(root, items):
    """
    Access a nested object in root by item sequence.

    :param root: nested object (e.g. a dictionary).
    :param items: sequence of item to access the root object (e.g a list).
    """
    return reduce(operator.getitem, items, root)

def set_by_path(root, items, value):
    """
    Set a value in a nested object in root by item sequence.

    :param root: nested object (e.g. a dictionary).
    :param items: sequence of item to access the root object (e.g a list).
    :param value: value set in the specified position.
    """
    get_by_path(root, items[:-1])[items[-1]] = value


#############
##### CLASSES
#############


class NumpyEncoder(json.JSONEncoder):
    """
    Special json encoder for numpy types. Adapted from:

    * https://github.com/mpld3/mpld3/issues/434#issuecomment-340255689
    """
    def default(self, obj):

        if isinstance(obj, np.integer):

            return int(obj)

        elif isinstance(obj, np.floating):

            return float(obj)

        elif isinstance(obj, np.ndarray):

            tmp = []
            for elem in obj:

                if isinstance(elem, np.integer):

                    tmp.append(int(elem))

                elif isinstance(elem, np.floating):

                    tmp.append(float(elem))

                else:

                    tmp.append(elem)

            obj = tmp

        return json.JSONEncoder.default(self, obj)


class ExifreadEncoder(json.JSONEncoder):
    """
    Special json encoder for Exifread metadata.
    """
    def default(self,obj):

        if type(obj) is Ratio:

            return {'num':obj.num,'den':obj.den}