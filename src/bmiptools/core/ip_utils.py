# Title: 'ip_utils.py'
# Date: 27/01/21
# Author: Curcuraci L.
#
# Scope: This file contain various image processing core functions.

"""
Utility functions related to image processing.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import os
import skimage.filters as skfilt


#################
#####   FUNCTIONS
#################


def kill_line(image, ve_line=None, ho_line=None):
    """
    Remove a specific line in a image along the x or y direction (simultaneous killing is possible).
    If no line is provided, the image is left unchanged.

    :param image: numpy array containing the 2d image.
    :param ve_line: (optional) vertical line to remove.
    :param ho_line: (optional) horizontal line to remove.
    :return: numpy array containing the processed image.
    """
    if ve_line is not None:

        image = np.concatenate([image[:, :ve_line - 1], image[:, ve_line + 1:]], axis=1)

    if ho_line is not None:

        image = np.concatenate([image[:ho_line - 1, :], image[ho_line + 1:, :]], axis=0)

    return image

def smoothed_deriv(image,sigma,axis=0):
    """
    Compute the smoothed derivative along a given axis. Smoothing is performed both before and after the derivative
    operation.

    :param image: numpy array containing the image to differentiate.
    :param sigma: standard deviation of the gaussian filter used for smoothing.
    :param axis: axis along witch the derivative is taken (vertical axis as default).
    :return: the smoothed derivative of the image.
    """
    filt_image = skfilt.gaussian(image,sigma,preserve_range=True)
    return np.gradient(filt_image)[axis]

def standardizer(image,type='-1/1',mode='yx'):
    """
    Standardize an image according to a given methods. Currently implemented methods:
-
    * '-1/1': all the values in the image are suitably rescaled between -1 and 1.
    * '0/1': all the values of the image are suitably rescaled between 0 and 1.
    * 'mean/std': the image will have zero mean and standard deviation 1.

    The standardization can be computed with in the 'image plane', or in case of "3d" images (organized according to
    the ZYX convention) the standardization can be done along the z-axis only.

    :param image: (nparray) image to standardize.
    :param type: (str) method name ('-1/1', '0/1' or 'mean/std').
    :param mode: (str) mode name ('yx' or 'z')
    :return: the standardized image.
    """
    if type == '-1/1':

        if mode == 'yx':

            iM = np.max(image,axis=(-2,-1),keepdims=True)
            im = np.min(image,axis=(-2,-1),keepdims=True)

        elif mode == 'z':

            iM = np.max(image)
            im = np.min(image)

        else:

            raise NameError('Image standardization mode can be only \'yx\' or \'z\'.')

        standard_image = 2*(image-im)/(iM-im)-1

    elif type == '0/1':

        if mode == 'yx':

            iM = np.max(image,axis=(-2,-1),keepdims=True)
            im = np.min(image,axis=(-2,-1),keepdims=True)

        elif mode == 'z':

            iM = np.max(image)
            im = np.min(image)

        else:

            raise NameError('Image standardization mode can be only \'yx\' or \'z\'.')

        standard_image = (image-im)/(iM-im)

    elif type == 'mean/std':

        if mode == 'yx':

            mn = np.mean(image,axis=(-2,-1),keepdims=True)
            std = np.std(image,axis=(-2,-1),keepdims=True)

        elif mode == 'z':

            mn = np.mean(image)
            std = np.std(image)

        else:

            raise NameError('Image standardization mode can be only \'yx\' or \'z\'.')

        standard_image = (image-mn)/std

    else:

        raise NotImplementedError('Image standardization not implemented. Standardizations available: \'-1/1\','
                                  '\'0/1\' and, \'mean/std\' . ')

    return standard_image