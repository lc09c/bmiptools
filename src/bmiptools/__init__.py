"""

"""
############
#####   INFO
############


# Global variables in the library

__version__ = '1.0.1'

__name__ = 'BioMaterials Image Processing Tools - bmiptools'

__author__ = 'Curcuraci Luca'

__affiliation__ = 'MPICI - Max Planck Institute of Colloids and Interfaces'

__scope__ = 'Image processing tools for typical FIB-SEM and micro-CT images acquired at the institute.'

__contributors__ = ['Bertinetti Luca',] # to complete with a 'search_contrib' function to get all the plugin authors.

__manual__ = 'https://bmiptools.readthedocs.io/en/latest/'

def info():

    print('Developed by ', __author__, ' @ ', __affiliation__)
    print('Tool name: ', __name__)
    print('Version: ', __version__)
    print('Tool scope: ',__scope__)
    print('Contributors: \n', __contributors__)
    print('Documentation available @ ',__manual__)

#############
#####   PATHS
#############


import os
import bmiptools.core.utils as ut


# Path of the library
# __lib_path__ = os.getcwd()+os.sep+'bmiptools'
__lib_path__ = os.path.dirname(os.path.abspath(__file__))
# __lib_path__ = os.path.abspath('bmiptools')
# idx_path = [name for name in os.listdir(".") if os.path.isdir(name)].index('bmiptools')
# __lib_path__ = [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name)][idx_path]

# Path to the file folder of bmiptools, where internal files of the library are saved
__bmiptools_files_folder_path__ = __lib_path__+os.sep+os.path.normpath(r'setting/files')

# Path to the 'global_setting.txt' file, where the global setting variables of the library are specified.
# __global_setting_path__ = r'bmiptools/setting/files/global_setting.txt'
__global_setting_path__ = __bmiptools_files_folder_path__+os.sep+r'global_setting.txt'

# Path to the temporary files folder
# __temporary_files_folder_path__ = ut.manage_path(r'setting/temporary_files')
__temporary_files_folder_path__ = ut.manage_path( __lib_path__+os.sep+os.path.normpath(r'setting/temporary_files'))


#################
#####   CONFIGURE
#################


from bmiptools.setting.configure import *


##############################
#####   GLOBAL SETTING METHODS
##############################
#
#
# def set_verbosity(verbosity_level,path=__global_setting_path__):
#     """
#     Set verbosity level in 'global_setting.txt'.
#
#     :param verbosity_level: (int) 0 for no messages printed or 1 printing allowed.
#     :param path: path to the 'global_setting.txt' file.
#     """
#     ut.set_option_in_global_setting('verbosity',verbosity_level,path=path)
#
#
# def set_cpu_buffer(n_cpu_buffer, path=__global_setting_path__):
#     """
#     Set number of cpu buffer 'global_setting.txt'.
#
#     :param n_cpu_buffer: (int) number of cpu that are not used during multiprocessing.
#     :param path: path to the 'global_setting.txt' file.
#     """
#     ut.set_option_in_global_setting('cpu_buffer',n_cpu_buffer, path=path)
#
# def set_use_multiprocessing(multiprocessing, path=__global_setting_path__):
#     """
#     Set multiprocessing flag in 'global_setting.txt'.
#
#     :param multiprocessing: (int) 0 to not use multiprocessing, 1 to use multiprocessing.
#     :param path: path to the 'global_setting.txt' file.
#     """
#     ut.set_option_in_global_setting('use_multiprocessing',multiprocessing, path=path)
#
# def set_multiprocessing_type(multiprocessing_type, path=__global_setting_path__):
#     """
#     Set multiprocessing type in 'global_setting.txt'.
#
#     :param multiprocessing_type: (int) set it 0 to use multiprocessing for pipeline parallelization, set it 1 to use
#                                   multiprocessing for internal parallelization in the plugin.
#     :param path: path to the 'global_setting.txt' file.
#     """
#     ut.set_option_in_global_setting('multiprocessing_type',multiprocessing_type, path=path)
#
# def set_use_gpu(gpu, path=__global_setting_path__):
#     """
#     Set multiprocessing flag in 'global_setting.txt'.
#
#     :param gpu: (int) 0 to not use gpu parallelization, 1 to use gpu parallelization.
#     :param path: path to the 'global_setting.txt' file.
#     """
#     ut.set_option_in_global_setting('use_gpu',gpu, path=path)
