# Title: 'example_cropper.py'
# Author: Curcuraci L.
# Date: 05/07/2022
#
# Scope: Script used to produce the images in the cropper page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.geometric.cropper import Cropper


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,_ = dm.dataIn_manager('stack1',pdata)
    path_to_results,_ = dm.dataOut_manager('cropper',rdata)

    # load stack
    s = Stack()
    s.load_slices(path=path_to_stack,S = list(range(10,20)))

    # save slice 0 before cropping
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_cropper',
            save_metadata=False,
            data_type=np.uint8)

    # initialize cropper
    td = Cropper.empty_transformation_dictionary
    td['y_range'] = [-500,None]
    td['x_range'] = [None,500]
    crop = Cropper(td)

    # apply cropper
    crop.transform(s)

    # save slice 0 after cropping
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='post_cropper',
            save_metadata=False,
            data_type=np.uint8)