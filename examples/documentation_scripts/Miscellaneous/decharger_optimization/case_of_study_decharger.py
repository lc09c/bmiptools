# Title: 'case_of_study_decharger.py'
# Author: Curcuraci L.
# Date: 06/07/2022
#
# Scope: study decharger loss behavior.


#################
#####   LIBRARIES
#################


import os
import sys

sys.path.append(os.getcwd())

import numpy as np
import matplotlib.pyplot as plt
import pywt
import data_manager as dm

from tqdm import tqdm
from scipy import fftpack

from bmiptools.stack import Stack
from bmiptools.transformation import Standardizer, SUPPORTED_WAVELET
from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2D as b2d


#################
#####   FUNCTIONS
#################


def destripe_slice(x, wavelet_name, sigma, level):
    """
    Core destriper transformation which is applied to a slice of a stack.

    :param x: (ndarray) array containing the image to process.
    :param wavelet_name: (str) name of the wavelet to be used.
    :param sigma: (float) standard deviation of the gaussian filter used to remove vertical lines.
    :param level: (int) decomposition level of the wavelet transform
    :return: (ndarray) the destriped image.
    """

    res = pywt.wavedec2(x, wavelet_name, level=level)
    filtred_res = []
    for coeff in res:

        if type(coeff) is tuple:

            cV = coeff[1]
            fft2_cV = fftpack.fftshift(fftpack.fft2(cV))
            size_y, size_x = fft2_cV.shape

            x_hat = (np.arange(-size_y, size_y, 2) + 1) / 2
            filter_transfer_function = -np.expm1(-x_hat ** 2 / (2 * sigma ** 2))
            filter_transfer_function = np.tile(filter_transfer_function, (size_x, 1)).T
            fft2_cV = fft2_cV * filter_transfer_function

            cV = fftpack.ifft2(fftpack.ifftshift(fft2_cV))
            filtred_res.append((coeff[0], np.real(cV), coeff[2]))

        else:

            filtred_res.append(coeff)

    return pywt.waverec2(filtred_res, wavelet_name)


def self_supervised_decurtaining_loss(x, destriped):
    """
    Self-supervised loss used for the parameter search.

    :param x: (ndarray) input slice;
    :param destriped: (ndarray) destriped slice;
    :return: (float) loss value for the given parameters.
    """
    stripes = x - destriped
    R = np.mean(np.abs(np.gradient(stripes, axis=0)))
    Q = np.mean(np.abs(np.gradient(stripes, axis=1) - np.gradient(x, axis=1)))
    # P = np.mean(np.abs(np.gradient(destriped,axis=0)-np.gradient(x,axis=0)))
    return 2 * R + Q


def generate_destriper_parameter_space(image_shape, sigma_range, wavelet_range):
    """
    Compute all the possible parameters combinations given the individual parameters ranges.

    :param image_shape: (tuple) shape of the image used for the loss computation.
    :param sigma_range: (list[float]) list of values of possible sigma.
    :param wavelet_range: (list[str]) list of possible wavelet names.
    :return: (list[list]) the parameter space.
    """
    param_space = []
    for wname in wavelet_range:

        Lmax = pywt.dwtn_max_level(image_shape, wname)
        for sigma in sigma_range:
            param_space.append([wname, sigma, Lmax])

    return param_space


############
#####   MAIN
############


if __name__ == '__main__':

    ### Data inputs

    slice_to_load = 30
    pdata, _ = dm.get_paths_from_args()
    path_to_stack, _ = dm.dataIn_manager('stack2', pdata)

    ### Parameter inputs

    sigma_range = np.arange(0.01, 50, 1)
    wavelet_range = SUPPORTED_WAVELET

    ### Preliminary operations

    # load stack (a singe slice)
    s = Stack()
    s.load_slices_from_folder(path=path_to_stack, S=[slice_to_load])

    # crop stack to some interesting part
    s.from_array(s[:, 1700:2700, 1500:2500])

    # standardize stack
    stand = Standardizer(Standardizer.empty_transformation_dictionary)
    stand.transform(s)

    # get slice for loss computation
    sl = s[0]
    image_shape = sl.shape

    ### Optimization routine

    # generate parameter space

    pspace = generate_destriper_parameter_space(image_shape, sigma_range, wavelet_range)
    N_param_comb = len(pspace)
    print('Total number of parameters combinations: ', N_param_comb)

    # optimization routine
    L = []
    for p in tqdm(pspace):
        # initialize filter with a set of parameters
        filter = lambda x: destripe_slice(x, *p)

        # apply filter
        dest_sl = filter(sl)

        # compute loss
        L_p = self_supervised_decurtaining_loss(sl, dest_sl)
        L.append(L_p)

    # print results
    best_idx = np.argmin(L)
    print('Best parameters: ', pspace[best_idx])
    print('Loss value: ', L[best_idx])

    ### Show results

    # plot full loss
    plt.figure(figsize=(20, 20))
    plt.title('loss value for parameter combination')
    plt.plot(L)
    plt.ylabel('loss value')
    plt.xlabel('combination number')
    plt.show()

    # plot loss around global minimum
    plt.figure(figsize=(20, 20))
    plt.title('loss value around the global minimum')
    plt.plot(list(range(best_idx - 60, best_idx + 40)), L[best_idx - 60:best_idx + 40], label='loss')
    plt.plot([best_idx], L[best_idx:best_idx + 1], 'x', label='global minimum')
    plt.legend()
    plt.xticks(list(range(best_idx - 60, best_idx + 40)), rotation=90)
    plt.xlabel('parameter combination number')
    plt.ylabel('loss value')
    plt.show()

    # define 3 interesting points
    idx2 = best_idx + 25  # away from global minimum
    idx3 = best_idx + 36  # local maximum
    idx4 = best_idx - 51  # local minumum

    # initialize different filter function
    filter = lambda x: destripe_slice(x, *pspace[best_idx])
    filter2 = lambda x: destripe_slice(x, *pspace[idx2])
    filter3 = lambda x: destripe_slice(x, *pspace[idx3])
    filter4 = lambda x: destripe_slice(x, *pspace[idx4])

    # plot images
    b2d.show_image(sl, title='original')
    b2d.show_image(filter(sl), title='loss {} | best parameter combination'.format(L[best_idx]))
    b2d.show_image(filter2(sl), title='loss {} | away from global minimum'.format(L[idx2]))
    b2d.show_image(filter3(sl), title='loss {} | local maximum'.format(L[idx3]))
    b2d.show_image(filter4(sl), title='loss {} | local minimum'.format(L[idx4]))