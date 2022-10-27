# Title: 'example_equalizer.py'
# Author: Curcuraci L.
# Date: 29/06/2022
#
# Scope: Script used to produce the images in the equalizer page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.dynamics.equalizer import Equalizer


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,_ = dm.dataIn_manager('stack2',pdata)
    path_to_results,_ = dm.dataOut_manager('equalizer',rdata)

    # load stack
    s = Stack()
    s.load_slices_from_folder(path=path_to_stack,S = list(range(10,20)))

    # crop to a reasonable substack
    s.from_array(s.data[:,500:1500,1500:2500])

    # save slice 0 before equalization
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_equalizer',
            data_type=np.uint8)

    # initialize equalizer
    td = Equalizer.empty_transformation_dictionary
    eq = Equalizer(td)

    # apply equalizer
    eq.transform(s)

    # save slice 0 after equalization
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='post_equalizer',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)