# Title: 'data_manager.py'
# Author: Curcuraci L.
# Date: 20/07/2022
#
# Scope: utility function(s) for Data loading and saving in the bmiptools example scripts with the goal to simplify the
#        life to those who wants to reproduce the images and animations used in the documentation.


#################
#####   LIBRARIES
#################


import sys
import os
import glob

from bmiptools.core.utils import manage_path


#################
#####   FUNCTIONS
#################


def dataIn_manager(stack_name,data_path = ''):
    """
    Utils to get path to stack and useful info for the stack loading in the example scripts.

    :param stack_name: (str) name of the stack to use.
    :param data_path: (raw str) Path to the Data folder. When not specified the script assumes the 'Data' folder in the
                      same folder from which the example scripts are launched.
    :return: path to stack and boolean which is False only when the stack is in a multitiff (or a single tiff) file.
    """
    folder = data_path+os.sep+'Data'+os.sep+stack_name
    sub_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
    if len(sub_folders) == 0:

        from_folder = False
        path_to_stack = glob.glob(folder+os.sep+'*.tiff')[0]

    else:

        from_folder = True
        path_to_stack = folder+os.sep+sub_folders[0]

    return path_to_stack, from_folder

def dataOut_manager(results_name,results_path = ''):
    """
    Utils used save the result in a proper manner.

    :param results_name: (str) name of the result folder.
    :param results_path: (raw str) path to the folder where the various files and folders will be produced.
    :return: the path to the final result folder and the result name.
    """
    path = manage_path(results_path+os.sep+'Results'+os.sep+results_name)
    return path, results_name

def get_paths_from_args():
    """
    Read the input arguments of the script and assign the paths for the input Data and the results.

    :return: Data and results paths.
    """
    if len(sys.argv)>2:

        data_path = str(sys.argv[1])
        results_path = str(sys.argv[2])

    elif len(sys.argv)==2:

        data_path = str(sys.argv[1])
        results_path = os.getcwd()

    else:

        data_path = os.getcwd()
        results_path = os.getcwd()

    print('Data path: {}'.format(data_path))
    print('Results path: {}'.format(results_path))
    return data_path, results_path