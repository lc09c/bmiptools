# Title: 'change_coordinate_system.py
# Author: Curcuraci L.
# Date: 19/02/2021
#
# Scope: Class used to visualize a stack in a different reference frame.

"""
Plugin used  to visualize a stack in a different reference frame.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import scipy.ndimage as spnd

from bmiptools.core import math_utils as mut
from bmiptools.transformation.base import TransformationBasic


###############
#####   CLASSES
###############


class ChangeCoordinateSystem(TransformationBasic):
    """
    This class can be used to change the reference frame in which the stack is visualized. The output behavior of this
    plugin is the same of any transformation plugin: therefore a copy of the stack visualized in the new reference frame
    is returned or overwritten over the input Stack. No transformation dictionary is present for this plugin.
    """

    def __init__(self,reference_frame_origin,xyz_to_XYZ_inv_map,xyz_to_XYZ_specs,use_xyz_ordering=True):
        """
        The new reference frame is specified by using the inverse of the map from the old to the new coordinated and
        from a specification dictionary (called 'xyz_to_XYZ_specs') which has to be the following structure:

            {'new_shape': (tuple) Shape of the stack in the new reference frame.

             'X_bounds': (tuple/list/numpy array) Min and max value of the X coordinate.

             'Y_bounds': (tuple/list/numpy array) Min and max value of the Y coordinate.

             'Z_bounds': (tuple/list/numpy array) Min and max value of the Z coordinate.

             'XYZ_ordering': (None or tuple/list/numpy array of int) Ordering of the coordinates in the new reference
             frame. If None the order is the one implicitly specified in the above fields.

             }


        :param reference_frame_origin: (tuple/list/numpy array) Position of the origin in the new reference frame.
        :param xyz_to_XYZ_inv_map: (python function with 3 inputs) Inverse mapping between the reference frame
                                   'xyz' and the reference frame 'XYZ'.
        :param xyz_to_XYZ_specs: (dict) Dictionary containing the specifications of the new reference frame.
        :param use_xyz_ordering: (bool) if True, the default ordering of the axis in the stack (which is 'zyx') is
                                 converted to the cartesian ordering (i.e. 'xyz').
        """
        self.reference_frame_origin = reference_frame_origin
        self.xyz_to_XYZ_inv_map = xyz_to_XYZ_inv_map
        self.new_shape = xyz_to_XYZ_specs['new_shape']
        self.X_min = xyz_to_XYZ_specs['X_bounds'][0]
        self.X_max = xyz_to_XYZ_specs['X_bounds'][1]
        self.n_X_steps = xyz_to_XYZ_specs['new_shape'][0]
        self.Y_min = xyz_to_XYZ_specs['Y_bounds'][0]
        self.Y_max = xyz_to_XYZ_specs['Y_bounds'][1]
        self.n_Y_steps = xyz_to_XYZ_specs['new_shape'][1]
        self.Z_min = xyz_to_XYZ_specs['Z_bounds'][0]
        self.Z_max = xyz_to_XYZ_specs['Z_bounds'][1]
        self.n_Z_steps = xyz_to_XYZ_specs['new_shape'][2]
        self.XYZ_ordering = None
        if xyz_to_XYZ_specs['XYZ_ordering'] is not None:

            self.XYZ_ordering = xyz_to_XYZ_specs['XYZ_ordering']

        self.use_xyz_ordering = use_xyz_ordering

    def transform(self,x,inplace=True,**kwargs):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
        """

        # get stack content
        volume = x.data

        # adopt the cartesian-like convention if needend
        if self.use_xyz_ordering:

            volume = volume.transpose(2,1,0)

        # create a a grid of points in the new reference frame
        Xs,Ys,Zs = np.meshgrid(np.linspace(self.X_min,self.X_max,self.n_X_steps),
                               np.linspace(self.Y_min,self.Y_max,self.n_Y_steps),
                               np.linspace(self.Z_min,self.Z_max,self.n_Z_steps),indexing='ij')

        # maps the point of the grid back to the original points in the initial reference frame
        xs,ys,zs = self.xyz_to_XYZ_inv_map(Xs,Ys,Zs)

        # Center the reference frame in the image center (z axis is already in the right position)
        xs = xs + self.reference_frame_origin[0]
        ys = ys + self.reference_frame_origin[1]
        zs = zs + self.reference_frame_origin[2]

        # create teh list of all the coordinates in which the image need to be evaluated
        xs, ys, zs = xs.reshape(-1), ys.reshape(-1), zs.reshape(-1)
        coords = np.vstack((xs, ys, zs))

        # compute the volume in the new reference frame
        volume_in_new_coordinates = spnd.map_coordinates(volume, coords,**kwargs)
        volume_in_new_coordinates = np.reshape(volume_in_new_coordinates,self.new_shape)

        # change coordinate ordering if required
        if self.XYZ_ordering is not None:

            volume_in_new_coordinates = volume_in_new_coordinates.transpose(self.XYZ_ordering)

        # eventually return just the transformed volume
        if not inplace:

            return volume_in_new_coordinates

        # otherwise save the volume in the stack
        volume = None # free RAM
        x.data = None # free RAM and empty stack
        x.from_array( volume_in_new_coordinates )