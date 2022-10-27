# Title: 'example_destriper.py'
# Author: Curcuraci L.
# Date: 29/06/2022
#
# Scope: Script used to produce the images in the destriper page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.restoration.destriper import Destriper


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,_ = dm.dataIn_manager('stack2',pdata)
    path_to_results,_ = dm.dataOut_manager('destriper',rdata)

    # load stack
    s = Stack()
    s.load_slices_from_folder(path=path_to_stack,S=list(range(20,30)))

    # crop to a reasonable substack
    s.from_array(s.data[:,500:2500,500:3500])

    # save slice 0 before destriping
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_destriper',
            save_metadata=False,
            data_type=np.uint8)
    s2.from_array(s[0,300:1300,2200:3200])
    s2.save(saving_path=path_to_results,
            saving_name='pre_destriper2',
            save_metadata=False,
            data_type=np.uint8)

    # initialize destriper
    td = Destriper.empty_transformation_dictionary
    td['optimization_setting']['decomposition_level']['increase_decomposition_level_during_inference'] = True
    dest = Destriper(td)

    # apply destriper
    dest.transform(s)

    # save slice 0 after destriping
    s2 = Stack()
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
           saving_name='post_destriper',
           save_metadata=False,
           data_type=np.uint8)
    s2.from_array(s[0,300:1300,2200:3200])
    s2.save(saving_path=path_to_results,
            saving_name='post_destriper2',
            save_metadata=False,
            data_type=np.uint8)