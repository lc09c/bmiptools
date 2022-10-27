# Title: 'math_utils.py'
# Date: 17/02/21
# Author: Curcuraci L.
#
# Scope: This file contain various mathematical core functions.

"""
Mathematics related utility functions.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import os


#################
#####   FUNCTIONS
#################


# Laziness

def max_and_min(arr,axis=None):
    """
    Return the maximum and the minimum of an array.

    :param arr: numpy array
    :param axis: (optional) axis along which the max and min are taken.
    :return: the maximum and the minimum (in this order)
    """
    return np.max(arr,axis=axis),np.min(arr,axis=axis)

def is_even(x):
    """
    Check if a number is even.

    :param x: (int or float) number to check.
    :return: (boolean) True if the number is even, False otherwise.
    """
    if x%2 == 0:

        return True

    else:

        return False

# UDM Conversion

def grad_to_rad(angle):
    """
    Convert an angle in grad into an angle in rad.

    :param angle: (float) angle in grad
    :return: (float) angle in rad
    """
    return angle/180*np.pi


def rad_to_grad(angle):
    """
    Convert an angle in rad into an angle in grad.

    :param angle: (float) angle in rad
    :return: (float) angle in grad
    """
    return angle/np.pi*180

# Coordinates

def cartesian_to_spherical(x,y,z,grad=True):
    """
    (x,y,z) -> (r,theta,phi)

    :param x: x
    :param y: y
    :param z: z
    :param grad: (boolean) if True theta and phi are converted to grads
    :return: r,theta,phi
    """
    r = np.sqrt(x**2+y**2+z**2)
    theta = np.arccos(z/r)
    phi = np.arctan2(y/x)
    if grad:

        theta = rad_to_grad(theta)
        phi = rad_to_grad(phi)

    return r,theta,phi

def spherical_to_cartesian(r,theta,phi,grad=True):
    """
    (r,theta,phi) -> (x,y,z)

    :param r: r
    :param theta: theta
    :param phi: phi
    :param grad: (boolean) if True theta and phi are converted to radiants.
    :return: x,y,z
    """
    if grad:

        theta = grad_to_rad(theta)
        phi = grad_to_rad(phi)

    x = r*np.sin(theta)*np.cos(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)
    return x,y,z

def cartesian_to_cylindircal(x,y,z,grad=True):
    """
    (x,y,z) -> (r,theta,z)

    :param x: x
    :param y: y
    :param z: z
    :param grad: (boolean) if True theta is converted to grad.
    :return: r,theta,z
    """
    r = np.sqrt(x**2+y**2)
    theta = np.arctan2(y,x)
    if grad:

        theta = rad_to_grad(theta)

    return r,theta,z

def cylindrical_to_cartesian(r,theta,z,grad=True):
    """
    (r,theta,z) -> (x,y,z)

    :param r: r
    :param theta: theta in grad
    :param z: z
    :param grad: (boolean) if True theta is converted to radiants
    :return: x,y,z
    """
    if grad:

        theta = grad_to_rad(theta)

    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return x,y,z

# Linear algebra

def is_diagonal(array,exact = True,epsilon=1e-5):
    """
    Check if an array is a diagonal matrix.

    :param array: arbitrary numpy array.
    :param exact: (boolean) if False approximate diagonal matrix is checked.
    :param epsilon: (float) threshold below witch an element is considered zero for the approximate diagonal
                    checking of a matrix. If exact is True this is ignored.
    :return: boolean
    """
    if len(array.shape) != 2:

        return False

    elif array.shape[0] != array.shape[1]:

        return False

    else:

        if exact:

            return np.count_nonzero(array - np.diag(np.diagonal(array)))==0

        else:

            array[array<epsilon] = 0.0
            return np.count_nonzero(array - np.diag(np.diagonal(array)))==0