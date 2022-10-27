# Title: 'example_standardizer.py'
# Author: Curcuraci L.
# Date: 29/06/2022
#
# Scope: Script used to produce the images in the standardizer page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.dynamics.standardizer import Standardizer


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,_ = dm.dataIn_manager('stack1',pdata)
    path_to_results,_ = dm.dataOut_manager('standardizer',rdata)

    # load stack
    s = Stack()
    s.load_slices(path=path_to_stack,S = list(range(10,20)))

    # save slice 0 before flattening
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_standardizer',
            save_metadata=False,
            data_type=np.uint8)

    # initialize standardizer
    td0 = Standardizer.empty_transformation_dictionary
    td0['standardization_type'] = '0/1'
    td0['standardization_mode'] = 'slice-by-slice'
    std = Standardizer(td0)

    # apply standardizer
    std.transform(s)

    # save slice 0 before destriping
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='post_standardizer',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)