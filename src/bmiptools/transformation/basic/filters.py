# Title: 'filters.py'
# Author: L. Curcuraci
# Date: 03/02/22
#
# Scope: Basic filters used in bmiptools.

"""
Basic filters used in bmiptools.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import cv2
from bmiptools.core.base import CoreBasic

# setting controlled import
cb = CoreBasic()

import scipy.ndimage.filters as spfl
if cb._use_gpu==1:

    try:

        import cupy as cp
        import cupyx.scipy.ndimage.filters as spfl

    except:

        pass


#################
#####   FUNCTIONS
#################


## core

def _compute_ksize(sigma,truncate = 4.0):
    """
    Compute the kernel size for the opencv gaussian filter.

    :param sigma:(float) standard deviation of the gaussian filter.
    :param truncate:(float) truncate the filter at this many standard deviations.
    :return: (int) kernel size.
    """
    # ksize = int(2*((sigma-0.8)/0.3+1))
    # if ksize%2 == 0:
    #
    #     return ksize+1
    ksize = 2*int(truncate*sigma+0.5)+1
    return ksize


## main

def gaussian_filter2d(input,sigma):
    """
    Fast 2-dimensional isotropic Gaussian filter. Implementation based on opencv and cupyx functions: the first is used
    on CPU the later on GPU. Which method is used is automatically selected according to the bmiptools global setting.

    :param input: (ndarray) the input image (2d array).
    :param sigma: (float) standard deviation of the isotropic Gaussian kernel.
    :return: (ndarray) the result of the filtering.
    """
    if cb._use_gpu:

        xcupy = cp.array(input)
        return spfl.gaussian_filter(xcupy,sigma).get()

    else:

        if input.dtype != np.float32:

            input = input.astype(np.float32)

        return cv2.GaussianBlur(input,2*(_compute_ksize(sigma),),sigmaX=sigma,borderType=cv2.BORDER_REFLECT_101)

def gaussian_filterNd(input,sigma,order=0,output=None,mode='reflect',cval=0.0,truncate=4.0):
    """
    Multi-dimensional Gaussian filter. Implementation based on scipy and cupyx functions: the first is used on CPU the
    later on GPU. Which method is used is automatically selected according to the bmiptools global setting.

    :param input: (ndarray) the input array.
    :param sigma: (float or tuple of float) standard deviations for each axis of Gaussian kernel. A single value
                  applies to all axes.
    :param order: (int or tuple of int) an order of 0, the default, corresponds to convolution with a Gaussian
                  kernel. A positive order corresponds to convolution with that derivative of a Gaussian. A single
                  value applies to all axes.
    :param output: (ndarray,dtype or None) the array in which to place the output. Default is is same dtype as the
                   input.
    :param mode: (str) the array borders are handled according to the given mode ('reflect', 'constant', 'nearest',
                 'mirror', 'wrap'). Default is 'reflect'.
    :param cval: (float) value to fill past edges of input if mode is 'constant'. Default is 0.0.
    :param truncate: (float) truncate the filter at this many standard deviations. Default is 4.0.
    :return: (ndarray) the result of the filtering.
    """
    if cb._use_gpu:

        xcupy = cp.array(input)
        return spfl.gaussian_filter(xcupy,sigma,order,output,mode,cval,truncate).get()

    else:

        return spfl.gaussian_filter(input,sigma,order,output,mode,cval,truncate)