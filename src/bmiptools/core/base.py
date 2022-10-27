# Title: base.py
# Date: 27/01/21
# Author: Curcuraci L.
#
# Scope: This file contain basic classes.

"""
Basic class containing general function which can be useful in any object of the library and possibly depending on
the global setting of the library..
"""


#################
#####   LIBRARIES
#################


import os
import joblib
import warnings
from tqdm import tqdm

import bmiptools
import bmiptools.core.utils as ut


#################
#####   FUNCTIONS
#################



#############
##### CLASSES
#############


class CoreBasic:
    """
    Basic class inherited by all the classes of bmiptools.
    """

    def __init__(self):


        self._global_setting_dict = ut.read_global_setting(bmiptools.__global_setting_path__)
        self._basic_setup()

    def _basic_setup(self):

        # verbosity level
        self.verbosity = self._global_setting_dict['verbosity']

        # multiprocessing
        use_multiprocessing = {0:False,
                               1:True}
        self._use_multiprocessing = use_multiprocessing[self._global_setting_dict['use_multiprocessing']]
        multiprocessing_type = {0:'parallelize_pipeline',
                                1:'parallelize_plugin'}
        self._use_multiprocessing_type = multiprocessing_type[self._global_setting_dict['multiprocessing_type']]
        self._cpu_buffer = self._global_setting_dict['cpu_buffer']
        self.configure_multiprocessing()

        # gpu optimization
        self._use_gpu = self._global_setting_dict['use_gpu']

    # verbosity controlled i/o methods
    def write(self,x,**kwargs):
        """
        Print the input based to the chosen verbosity level.

        :param x: input to print.
        """
        if self.verbosity == 1:

            print(x,**kwargs)

    def progress_bar(self,i, i_max, bar_length, text_after='', text_before=''):
        """
        Simple and light verbosity controlled progress bar.

        :param i: (int) current index
        :param i_max: (int) max index
        :param bar_length: (int) max length of the progress bar
        :param text_after: (str) text after the progress bar
        :param text_before: (str) text before the progress bar
        """
        if self.verbosity == 1:

            bar = ''
            if text_before != '':

                bar = text_before + ' | '

            bar = bar + '[' + '#' * int(i / i_max * bar_length) + ' ' * (bar_length - int(i / i_max * bar_length)) + ']'
            if text_after != '':

                bar = bar + ' | ' + text_after

            print(bar, end='\r')

    def vtqdm(self,x):
        """
        Verbosity controlled tqdm counter for for cycle.

        :param x: iterator
        :return: tqdm(iterator)
        """
        if self.verbosity == 1:

            return tqdm(x)

        else:

            return x

    # multiprocessing methods
    def configure_multiprocessing(self):

        self._n_available_cpu = joblib.cpu_count() - self._cpu_buffer
        if self._n_available_cpu <= 1:

            self._use_multiprocessing = False
            warnings.warn('No multiprocessing possible due to an insufficient number of CPUs. Consider to change the'
                          '\'cpu_buffer\' global variable of the library. Execution continues in normal mode.')