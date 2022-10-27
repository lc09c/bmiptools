# Title: 'geometric_tools.py'
# Author: Curcuraci L.
# Date: 28/09/21
#
# Scope: Collect a series of tools useful for geometric transformations. Current tools:
#
#     - Rodrigues vector: useful to compose in vectorial form two rotations expressed in the axis-angle notation, which
#                         the notation used in the Affine class to express rotations.

"""
Collection of a series of tools useful for geometric transformations. Current tools:

     - Rodrigues vector: useful to compose in vectorial form two rotations expressed in the axis-angle notation, which the notation used in the Affine class to express rotations.

"""

#################
#####   LIBRARIES
#################


import numpy as np
import bmiptools.core.math_utils as mut


###############
#####   CLASSES
###############


class RodriguesVector:
    """
    Rodrigues vector to compose the rotations in the angle-axis notation. The composition can be computed by summing two
    RoudriguesVector object, as shown in the example below:

    Example 1:
    Two 90° rotations around the same [0,0,1] axis.

    >>> f = RodriguesVector(90,[0,0,1])
    >>> g = RodriguesVector(90,[0,0,1])
    >>> print(f+g)
    180° · (0.0, 0.0, 1.0)

    Example 2:
    Two 90° rotations around two differnt axes. First aroud the [0,0,1] axis then around the [0,1,0] axis.

    >>> f = RodriguesVector(90,[0,1,0])
    >>> g = RodriguesVector(90,[0,0,1])
    >>> print(f+g)
    120° · (-0.5773502691896257, 0.5773502691896258, 0.5773502691896258)

    Angle and axis of the final composition are attributes of the final RodriguesVector object. For more information see
    https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions and references therein.
    """

    def __init__(self, angle, axis, grad=True):
        """
        Define the Rodrigues vector associated to a rotation of an angle Theta around a certain axis E.

        :param angle: (float) rotation angle, it can be in grad or in radiant;
        :param axis: (array) rotation axis, it should be normalized (i.e. a versor);
        :param grad: (boolean) True if the angle is expressed in grad, False if in radiant.
        """
        self.angle = angle
        if grad == True:

            self._angle = mut.grad_to_rad(self.angle)

        else:

            self._angle = self.angle

        self.axis = np.array(axis) / np.linalg.norm(axis, ord=2)
        self._grad = grad

    def __add__(self, b):

        g = self._get_roudriguez_vector(self)
        f = self._get_roudriguez_vector(b)
        f_comp_g = (g + f - np.cross(f, g)) / (1 - np.dot(g, f))
        mod_f_comp_g = np.linalg.norm(f_comp_g, ord=2)
        if mod_f_comp_g != 0:

            angle_f_comp_g = 2 * np.arctan(mod_f_comp_g)
            axis_f_comp_g = f_comp_g / mod_f_comp_g
            if self._grad == True:
                angle_f_comp_g = mut.rad_to_grad(angle_f_comp_g)

        else:

            angle_f_comp_g = 0
            axis_f_comp_g = self.axis  # convention chosen: when no rotation happens the axis is undetermined

        return RodriguesVector(angle_f_comp_g, axis_f_comp_g, grad=self._grad)

    @staticmethod
    def _get_roudriguez_vector(x):

        return np.tan(x._angle / 2) * x.axis

    def __str__(self):

        angle_uom = 'rad'
        if self._grad == True:

            angle_uom = '°'

        return '{}{} · ({}, {}, {})'.format(self.angle, angle_uom, *self.axis)
