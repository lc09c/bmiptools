# Title: 'example_decharger.py'
# Author: Curcuraci L.
# Date: 30/06/2022
#
# Scope: Script used to produce the images in the decharger page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation import Decharger,Destriper,Flatter


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,from_folder = dm.dataIn_manager('stack5',pdata)
    path_to_results,_ = dm.dataOut_manager('decharger',rdata)

    # load stack
    s = Stack(path=path_to_stack,
              from_folder=from_folder,
              load_metadata=False,
              loading_extension='tiff')

    # Apply destriper first to make the background more homogeneous
    td0 = Destriper.empty_transformation_dictionary
    td0['optimization_setting']['decomposition_level']['increase_decomposition_level_during_inference'] = True
    td0['optimization_setting']['opt_bounding_box']['x_limits_bbox'] = [-500,None]
    dest = Destriper(td0)
    dest.transform(s)

    # save slice 0 before decharging
    s2 = Stack()                                            # create a stack having only the slice to save
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
            saving_name='pre_decharger',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)
    s2.from_array(s[0,1700:2300,800:1300])
    s2.save(saving_path=path_to_results,
            saving_name='pre_decharger2',
            save_metadata=False,
            standard_saving=True,
            data_type=np.uint8)

    # initialize decharger
    td = Decharger.empty_transformation_dictionary
    td['optimization_setting']['opt_bounding_box']['y_limits_bbox'] = [-1000,None]
    td['optimization_setting']['opt_bounding_box']['x_limits_bbox'] = [ None,1000]
    dech = Decharger(td)

    # apply decharger
    dech.transform(s)

    # save slice 0 after decharging
    s2 = Stack()
    s2.from_array(s[0])
    s2.save(saving_path=path_to_results,
           saving_name='post_decharger',
           save_metadata=False,
           standard_saving=True,
           data_type=np.uint8)
    s2.from_array(s[0,1700:2300,800:1300])
    s2.save(saving_path=path_to_results,
           saving_name='post_decharger2',
           save_metadata=False,
           standard_saving=True,
           data_type=np.uint8)

    # copy stack to apply flatter
    s3 = Stack()
    s3.from_array(s[:,:,:])

    # initialize flatter
    td1 = Flatter.empty_transformation_dictionary
    fl = Flatter(td1)

    # apply flatter
    fl.transform(s3)

    # save slice 0 after decharging and flatter
    s4 = Stack()
    s4.from_array(s3[0])
    s4.save(saving_path=path_to_results,
           saving_name='post_decharger_post_flatter',
           save_metadata=False,
           standard_saving=True,
           data_type=np.uint8)
    s4.from_array(s3[0,1700:2300,800:1300])
    s4.save(saving_path=path_to_results,
           saving_name='post_decharger_post_flatter2',
           save_metadata=False,
           standard_saving=True,
           data_type=np.uint8)