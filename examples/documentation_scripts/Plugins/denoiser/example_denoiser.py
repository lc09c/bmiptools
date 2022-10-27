# Title: 'example_denoiser.py'
# Author: Curcuraci L.
# Date: 31/06/2022
#
# Scope: Script used to produce the images in the denoiser page of the documentation


import os
import sys

sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation import Denoiser

if __name__ == '__main__':
    # setup
    pdata, rdata = dm.get_paths_from_args()
    path_to_stack, _ = dm.dataIn_manager('stack3', pdata)
    path_to_results, _ = dm.dataOut_manager('denoiser', rdata)

    # load stack
    s = Stack()
    s.load_slices_from_folder(path=path_to_stack, S=list(range(10)))

    # crop to the relevant part
    s.from_array(s[:, :, 250:1750])

    # save slice 0 before denoiser
    s2 = Stack()  # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_denoiser',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)
    s2.from_array(s[0, 550:750, 450:650])
    s2.save(saving_path=path_to_results,
            saving_name='pre_denoiser2',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)

    # intialize denoiser
    td = Denoiser.empty_transformation_dictionary
    td['optimization_setting']['opt_bounding_box']['x_limits_bbox'] = [500, 1000]
    den = Denoiser(td)

    # apply denoiser
    den.transform(s)

    # save slice 0 after denoiser
    s2 = Stack()  # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='post_denoiser',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)
    s2.from_array(s[0, 550:750, 450:650])
    s2.save(saving_path=path_to_results,
            saving_name='post_denoiser2',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)