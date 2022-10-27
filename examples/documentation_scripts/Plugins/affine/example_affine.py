# Title: 'example_affine.py'
# Author: Curcuraci L.
# Date: 05/07/2022
#
# Scope: Script used to produce the images in the affine page of the documentation


import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.geometric.affine import Affine
from bmiptools.transformation.geometric.geometric_tools import RodriguesVector
from bmiptools.transformation.alignment.registrator import Registrator


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,from_folder = dm.dataIn_manager('stack1',pdata)
    path_to_results,_ = dm.dataOut_manager('affine',rdata)

    # load stack
    s = Stack(path=path_to_stack,
              load_metadata=False,
              loading_extension='tiff',
              from_folder=from_folder,
              image_type='others')

    # crop to reduce the memory needs
    s.from_array(s[45:,400:800,400:800])

    # first register the stack
    td0 = Registrator.empty_transformation_dictionary
    td0['opt_bounding_box']['use_bounding_box'] = False      # cropped images are already small
    td0['registration_algorithm'] = 'ECC'
    td0['refine_with_optical_flow'] = False
    reg = Registrator(td0)
    reg.transform(s)

    # save the  animation of 50 slices before affine transformation
    s2 = Stack()
    s2.from_array(s[20:70,...])
    s2.save_as_gif(saving_path=path_to_results,
                   saving_name='pre_affine_3d_anim50slices',
                   data_type=np.uint8,
                   standard_saving=True,
                   save_metadata=False)

    # Define the affine transformation (composite rotation: 10 degree around z-axis, 10 degree around y-axis)
    r1 = RodriguesVector(3,(0,0,1))    # rotation around z-axis
    r2 = RodriguesVector(5,(1,0,0))    # rotation around x-axis
    r = r1+r2                          # composite rotation

    # initialize Affine plugin
    td = Affine.empty_transformation_dictionary
    td['apply'] = 'rotation'
    td['reference_frame_origin'] = 'center'
    td['rotation']['rotation_angle'] = r.angle
    td['rotation']['rotation_axis'] = r.axis
    aff = Affine(td)

    # apply affine plugin
    aff.transform(s)

    # save animation of 50 slices after affine transformation
    s2 = Stack()
    s2.from_array(s[20:70,...])
    s2.save_as_gif(saving_path=path_to_results,
                   saving_name='post_affine_3d_anim50slices',
                   data_type=np.uint8,
                   standard_saving=True,
                   save_metadata=False)