# Title: 'example_flatter.py'
# Author: Curcuraci L.
# Date: 29/06/2022
#
# Scope: Script used to produce the images in the flatter page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.dynamics.standardizer import Standardizer
from bmiptools.transformation.restoration.flatter import Flatter


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,_ = dm.dataIn_manager('stack1',pdata)
    path_to_results,_ = dm.dataOut_manager('flatter',rdata)

    # load stack
    s = Stack()
    s.load_slices(path=path_to_stack,S = list(range(10,20)))

    # standardize stack
    td0 = Standardizer.empty_transformation_dictionary
    td0['standardization_type'] = '0/1'
    std = Standardizer(td0)
    std.transform(s)

    # save slice 0 before flattening
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_flatter',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)

    # initialize histogram matcher
    td = Flatter.empty_transformation_dictionary
    fl = Flatter(td)

    # apply histogram matching
    fl.transform(s)

    # save slice 0 before destriping
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='post_flatter',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)