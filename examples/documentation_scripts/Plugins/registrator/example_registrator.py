# Title: 'example_registrator.py'
# Author: Curcuraci L.
# Date: 29/06/2022
#
# Scope: Script used to produce the images in the registrator page of the documentation


import os
import sys

sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from copy import copy
from bmiptools.stack import Stack
from bmiptools.transformation.alignment.registrator import Registrator

if __name__ == '__main__':
    # setup
    pdata, rdata = dm.get_paths_from_args()
    path_to_stack, _ = dm.dataIn_manager('stack2', pdata)
    path_to_results, _ = dm.dataOut_manager('registrator', rdata)

    # load stack
    s = Stack()
    s.load_slices_from_folder(path=path_to_stack, S=list(range(5, 15)))

    # crop to a reasonable substack
    s.from_array(s.data[:, 2000:2500, 3000:3500])

    # save result before registration
    s.save_as_gif(saving_path=path_to_results,
                  saving_name='pre_registration',
                  data_type=np.uint8,
                  standard_saving=True,
                  save_metadata=False)

    s2 = copy(s)

    # initialize registrator for Phase corr only
    td = Registrator.empty_transformation_dictionary
    td['opt_bounding_box']['use_bounding_box'] = False  # cropped images are already small
    td['registration_algorithm'] = 'Phase_correlation'
    td['refine_with_optical_flow'] = False
    reg = Registrator(td)

    # apply registration
    reg.transform(s)

    # save result after registration
    s.save_as_gif(saving_path=path_to_results,
                  saving_name='post_registration',
                  data_type=np.uint8,
                  standard_saving=True,
                  save_metadata=False)

    # initialize registrator for Phase Corr + OF registration
    td = Registrator.empty_transformation_dictionary
    td['opt_bounding_box']['use_bounding_box'] = False  # cropped images are already small
    td['registration_algorithm'] = 'Phase_correlation'
    td['refine_with_optical_flow'] = True
    reg = Registrator(td)

    # apply registration
    reg.transform(s2)

    # save result after registration
    s2.save_as_gif(saving_path=path_to_results,
                   saving_name='post_registration_refined',
                   data_type=np.uint8,
                   standard_saving=True,
                   save_metadata=False)