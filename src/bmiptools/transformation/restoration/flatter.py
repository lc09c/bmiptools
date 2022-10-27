# Title: 'flatter.py'
# Date: 23/02/21
# Author: Curcuraci L.
#
# Scope: Class used to apply the flatter transformation on a stack object.
#
# Updates:
#
# - 18/05/21: * the plugin can deal with multichannel images (each channel is treated independently);
#             * the plugin can be optimized and apply the transformation in serial and parallel way.
#
# - 07/02/22: * faster version of gaussian filter used + gpu support for this filter;
#             * no need to change the optimization parameters ('image_range' and 'derivative_range') if the image format
#               changes (uint8 -> I in [0,256], uint16 -> [0,65536], etc...)

"""
Plugin applying the flatter transformation on a stack.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import os
import gc
import warnings
from joblib import Parallel,delayed

import bmiptools
from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI
from bmiptools.transformation.basic.filters import gaussian_filter2d


###############
#####   CLASSES
###############


class Flatter(TransformationBasic):
    """
    Class used to apply the flatter transformation to the stack.
    """

    __version__ = '0.3'
    empty_transformation_dictionary = {'auto_optimize': True,
                                       'optimization_setting':{'sigma_deriv_smoother': 5,
                                                               'sigma_min': 5,
                                                               'sigma_max': 'auto',
                                                               'sigma_step': 5,
                                                               'entropy_setting':{'image_range': (0,1), #(0,256),
                                                                                  'derivative_range': (0,0.039), #(0,10),
                                                                                  'n_bins': 1024},
                                                               'fit_step': 10,
                                                               'regularization_strength': 1,
                                                               'use_early_stopping': True,
                                                               'patience': 5},
                                       'sigma_low_pass': 80}
    _guipi_dictionary = {'auto_optimize': GuiPI(bool),
                         'optimization_setting':{'sigma_deriv_smoother': GuiPI(float,min=0.0),
                                                 'sigma_min': GuiPI(float,min=0.0),
                                                 'sigma_max': GuiPI('math',
                                                                    description= r'A float number of \'auto\' in oder '
                                                                                 r'to automatically determine this '
                                                                                 r'parameter'),
                                                 'sigma_step': GuiPI(float),
                                                 'entropy_setting':{'image_range': GuiPI('math'),
                                                                    'derivative_range': GuiPI('math'),
                                                                    'n_bins': GuiPI(int)},
                                                 'fit_step': GuiPI(int),
                                                 'regularization_strength': GuiPI(float,min=0.0),
                                                 'use_early_stopping': GuiPI(bool),
                                                 'patience': GuiPI(int)},
                         'sigma_low_pass': GuiPI(float,min=0.0)}
    def __init__(self,transformation_dictionary,force_serial=False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'auto_optimize': (bool) If True the optimization procedure used to determine the parameter of the flatter
            transformation is performed before the application of the transformation. The optimization is done on the
            whole stack, finding the best parameter for the whole stack. The optimization setting have to be specified
            in the 'optimization_setting' field of this dictionary (see blow) which is red only if 'auto_optimize' is
            True. If this field is set to False, the value specified in the 'sigma_low_pass' field of this dictionary
            is considered (but ignored if this field is True).

            'optimization_setting': (dict) Dictionary containing the optimization setting. The dictionary has to be
            specified as below:

                {'sigma_deriv_smoother': (float) Standard deviation of the gaussian filter use to suppress the noise
                amplification introduced during discrete differentiation. Its value should be not to high. A recommended
                value can be 5.

                'sigma_min': (float) smallest value of the parameter 'sigma' used during the optimization. This
                value is also used for the loss normalization.

                'sigma_max': (float/str) maximum value of the parameter 'sigma' used during the optimization. It can
                be:

                    * a float, indicating the maximum value of 'sigma' directly;

                    * 'auto', indicating the 'sigma_max' will be automatically inferred from the image shape, imposing
                    the the filter size is not to big with respect to the image.

                'sigma_step': (float) step used for the variation of 'sigma' during the optimization.

                'entropy_setting': Dictionary containing the setting relative to the computation of the entropy. The
                dictionary has to be specified as below:

                    {'image_range': (tuple) tuple containing the minimum and maximum value of an image (i.e. the
                    dynamic range of the image).

                    'derivative_range': <(tuple) tuple containing the minimum and maximum value of the modulus of the
                    derivative of the image (i.e. the dynamic range of the modulus of the image derivative).

                    'n_bins': (int) number of bins used for the computation of the histograms of the image.

                    }

                'fit_step': (int) interval between two slices of the stack that are used during the optimization. If 1
                all the stack is used, for n>1 only the slices having a distance of n on the 0-axis (i.e. the
                z-direction). This parameter therefore determine the number of slices used during the optimization,
                which is equal to (image_size_z)//n.

                'regularization_strength': (float) strength of the regularization used. A value of 1 is recommended.
                Regularization can be switched off by setting this parameter equal to 0.

                'use_early_stopping': (boolean) if True an early-stopping-like policy is used to speed up the
                optimization. The 'patience' parameter below is used in the policy definition when this field is True,
                and ignored when this field is False.

                'patience': (int) number of step waited before the optimization terminates, when no improvements in the
                loss are detected.

                }

            'sigma_low_pass': (float or list of float) parameter of the low pass filter in the flatter transformation
            which is used if no optimization is performed. For stack with multiple channels, a list of floats
            representing the low pass filter parameters for each channel can be given. The length of such a list have
            to be equal to the number of channels of the stack, in order to be used properly.

            }


        :param transformation_dictionary: dictionary containing all the transformation options.
        :param force_serial: (bool) if True serial behavior is forced for this plugin independently on the global
                             setting of bmiptools.
        """
        super(Flatter,self).__init__()
        self.force_serial = force_serial

        self.transformation_dictionary = transformation_dictionary
        self.auto_optimize = transformation_dictionary['auto_optimize']
        if transformation_dictionary['auto_optimize']:

            self.sigma_deriv_smoother = transformation_dictionary['optimization_setting']['sigma_deriv_smoother']
            self.sigma_min = transformation_dictionary['optimization_setting']['sigma_min']
            self.sigma_max = transformation_dictionary['optimization_setting']['sigma_max']
            self.sigma_step = transformation_dictionary['optimization_setting']['sigma_step']
            self.image_range = transformation_dictionary['optimization_setting']['entropy_setting']['image_range']
            self.derivative_range = transformation_dictionary['optimization_setting']['entropy_setting']['derivative_range']
            self.n_bins = transformation_dictionary['optimization_setting']['entropy_setting']['n_bins']
            self.regularization_strength = transformation_dictionary['optimization_setting']['regularization_strength']
            self.use_early_stopping = transformation_dictionary['optimization_setting']['use_early_stopping']
            if transformation_dictionary['optimization_setting']['use_early_stopping']:

                self.patience = transformation_dictionary['optimization_setting']['patience']

            self.fit_step = transformation_dictionary['optimization_setting']['fit_step']

        else:

            self.sigma_low_pass = transformation_dictionary['sigma_low_pass']

    @staticmethod
    def _entropy(p,normalize=True):
        """
        Compute the Shannon entropy given a (possibly unnormalized) probability distribution.

        :param p: (list/ndarray) probability distribution.
        :param normalize: (boolean) if True the distribution is normalized before the computation of the entropy.
        :return: the Shannon entropy associated to that distribution.
        """
        if normalize:

            p = p/np.sum(p)

        with warnings.catch_warnings():

            warnings.simplefilter('ignore')
            H_i = -p*np.log(p)

        H_i[p == 0] = 0     # remove possible NaNs
        return np.sum(H_i)

    def _fit_parallel(self,x,n_channels):
        """
        Core fitting function for the plugin optimization in its parallel version. The aim of the optimization is to
        find the 'sigma' parameter of a gaussian filter by minimizing the following loss:

                                           L[f0,sigma] = L0[f0,sigma] + Lreg[sigma]

        where 'f0' is the image to which the transformation is applied,

        L0 = 1/3*( H_f/H_f_min + H_df_min/H_df + |H_df - H_df0|/|H_df_min - H_df0| ),

        and

        Lreg = alpha*[(sigma-sigma_min)/max(sigma)]^30.

        Above 'f' is the image 'f0' transformed with a certain parameter 'sigma', 'df' is the modulus of the derivative
        of 'f', 'H_f' and 'H_df' are the Shannon entropies of (the histograms of) 'f' and 'df', 'H_df0' is the Shannon
        entropy of the modulus of the derivative of 'f0', while 'H_f_min' and 'H_df_min' are the Shannon entropies of
        'f_min' and 'd_f_min' (i.e. the modulus of the derivative of 'f_min'), where 'f_min' is the image 'f0'
        transformed with the smallest (but positive) value of 'sigma' available.

        The optimization is done via simple line search with possible early stopping policy. Each channel is optimized
        independently.

        :param x: (ndarray) array containing the slice of the stack to be used during the optimization.
        :param n_channels: number of channels in the data used for the optimization.
        :return: value of 'sigma' corresponding to the minimum of the mean loss.
        """

        def loss_components(x):
            """
            Compute the entropy of x and the entropy of the modulus of the 2D derivative of x.
            """
            hist_x = np.histogram(x, bins=self.n_bins, range=self.image_range)[0]
            H_x = self._entropy(hist_x)

            x_smooth = gaussian_filter2d(x, self.sigma_deriv_smoother)
            # x_smooth = skfilt.gaussian(x, self.sigma_deriv_smoother, preserve_range=True)   # smoothed derivative

            dx_x, dy_x = np.gradient(x_smooth)                                              #
            d_x = np.sqrt(dx_x ** 2 + dy_x ** 2)
            hist_d_x = np.histogram(d_x, bins=self.n_bins, range=self.derivative_range)[0]
            H_d_x = self._entropy(hist_d_x)

            return H_x, H_d_x

        sigmas = np.arange(self.sigma_min,self.sigma_max,self.sigma_step)
        self.write('Flatter optimization routine')
        self.write('----------------------------')
        self.write('Optimization method: line search')
        self.write('Search space: [{},{}] with step {}'.format(self.sigma_min,self.sigma_max,self.sigma_step))
        self.write('Early-stopping policy used: {}'.format(self.use_early_stopping))
        if self.use_early_stopping:

            self.write('Patience: {}'.format(self.patience))

        if n_channels>1:

            self.write('Number of channels: {}'.format(n_channels))

        self.write('Parallelized optimization routine')
        self.write('----------------------------')
        optimal_sigma = []
        for C in range(n_channels):

            x_for_optimization = x
            if n_channels > 1:

                self.write('Optimization of channel {}'.format(C+1))
                x_for_optimization = x[...,C]

            Ls = []
            for idx1, slice in enumerate(x_for_optimization):

                self.progress_bar(idx1,len(x_for_optimization),15,'slice {}/{}'.format(idx1+1,len(x_for_optimization)))
                _, H0_dx = loss_components(slice)
                sigma0 = sigmas[0]

                # flat_slice = slice-skfilt.gaussian(slice,sigma0,preserve_range=True)
                flat_slice = slice-gaussian_filter2d(slice,sigma0)

                H_x0, H_dx0 = loss_components(flat_slice-np.min(flat_slice))

                # use of numpy memorymap in order to share memory among different process.
                tmp_file_path = bmiptools.__temporary_files_folder_path__ + os.sep + 'tmp_flatter_plugin.dat'
                mp = np.memmap(tmp_file_path, dtype=float, mode='w+', shape=(len(sigmas)+1,))
                mp[:] = np.finfo(float).max  # set very high default value (the loss should be around 1)
                mp[0] = 1.  # loss equal to 1 for the lowest possible filter value (loss = 1 for a completely wrong value)

                # parallelization over the computation of the possible sigmas.
                def func_to_par(idx2,memory_map):

                    sigma = sigmas[idx2]

                    # flat_slice = slice-skfilt.gaussian(slice,sigma,preserve_range=True)
                    flat_slice = slice -gaussian_filter2d(slice,sigma)

                    H_x, H_dx = loss_components(flat_slice-np.min(flat_slice))
                    l = 1/3*(H_x/H_x0+H_dx0/H_dx0+np.abs(H_dx-H0_dx)/np.abs(H_dx0-H0_dx))               # loss function
                    l = l+1/3*self.regularization_strength*((sigma-self.sigma_min)/np.max(sigmas))**30  # regularization

                    # early stopping (parallel version)
                    current_raw_index = np.where(memory_map == np.finfo(float).max)[0][0] - 1
                    if self.use_early_stopping and (current_raw_index-self.patience)>0 and \
                       (np.where(memory_map[current_raw_index-self.patience:current_raw_index] ==
                        np.min(memory_map[current_raw_index-self.patience:current_raw_index]))[0] == 0).any():

                        self.write('Early-stopping: Loss did\'t decrease for the last {} parameter changes, optimization '
                                   'for slice {} terminated earlier!'.format(self.patience,idx1+1))
                        raise ValueError('')

                    else:

                        memory_map[idx2] = l

                try:

                    Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(idx2,mp)
                                                           for idx2 in range(1,len(sigmas)))

                except ValueError:

                    pass

                L = np.array(mp)
                max_idx = np.min(np.where(L == np.finfo(float).max)[0])
                L = list(L[:max_idx])

                # remove numpy memorymap temporary file
                try:

                    del mp  # close memory map file (does it really work? -  https://github.com/numpy/numpy/issues/13510)
                    gc.collect()
                    os.remove(tmp_file_path)

                except:

                    self.write('Library warning: temporary file \'{}\' used for parallel optimization cannot be erased. '
                               'Do it manually if needed.'.format(tmp_file_path))

                Ls.append(L)

            # optimal sigma: one sigma for all slices
            min_len = np.min([len(ls) for ls in Ls])
            Ls = np.array([ls[:min_len] for ls in Ls])
            optimum = sigmas[np.argmin(Ls.mean(axis=0))]    # one sigma for all slices
            optimal_sigma.append(optimum)

        if n_channels == 1:

            optimal_sigma = optimal_sigma[0]

        self.write('Optimal value(s) for \'sigma_low_pass\': {}'.format(optimal_sigma))
        return optimal_sigma

    def _fit_serial(self,x,n_channels):
        """
        Core fitting function for the plugin optimization in its serial version. The aim of the optimization is to
        find the 'sigma' parameter of a gaussian filter by minimizing the following loss:

                                           L[f0,sigma] = L0[f0,sigma] + Lreg[sigma]

        where 'f0' is the image to which the transformation is applied,

        L0 = 1/3*( H_f/H_f_min + H_df_min/H_df + |H_df - H_df0|/|H_df_min - H_df0| ),

        and

        Lreg = alpha*[(sigma-sigma_min)/max(sigma)]^30.

        Above 'f' is the image 'f0' transformed with a certain parameter 'sigma', 'df' is the modulus of the derivative
        of 'f', 'H_f' and 'H_df' are the Shannon entropies of (the histograms of) 'f' and 'df', 'H_df0' is the Shannon
        entropy of the modulus of the derivative of 'f0', while 'H_f_min' and 'H_df_min' are the Shannon entropies of
        'f_min' and 'd_f_min' (i.e. the modulus of the derivative of 'f_min'), where 'f_min' is the image 'f0'
        transformed with the smallest (but positive) value of 'sigma' available.

        The optimization is done via simple line search with possible early stopping policy. Each channle is optimized
        independently.

        :param x: (ndarray) array containing the slice of the stack to be used during the optimization.
        :param n_channels: number of channels in the data used for the optimization.
        :return: value of 'sigma' corresponding to the minimum of the mean loss.
        """

        def loss_components(x):
            """
            Compute the entropy of x and the entropy of the modulus of the 2D derivative of x.
            """
            hist_x = np.histogram(x, bins=self.n_bins, range=self.image_range)[0]
            H_x = self._entropy(hist_x)

            x_smooth = gaussian_filter2d(x,self.sigma_deriv_smoother)
            # x_smooth = skfilt.gaussian(x, self.sigma_deriv_smoother, preserve_range=True)   # smoothed derivative

            dx_x, dy_x = np.gradient(x_smooth)                                              #
            d_x = np.sqrt(dx_x ** 2 + dy_x ** 2)
            hist_d_x = np.histogram(d_x, bins=self.n_bins, range=self.derivative_range)[0]
            H_d_x = self._entropy(hist_d_x)

            return H_x, H_d_x

        sigmas = np.arange(self.sigma_min,self.sigma_max,self.sigma_step)
        self.write('Flatter optimization routine')
        self.write('----------------------------')
        self.write('Optimization method: line search')
        self.write('Search space: [{},{}] with step {}'.format(self.sigma_min,self.sigma_max,self.sigma_step))
        self.write('Early-stopping policy used: {}'.format(self.use_early_stopping))
        if self.use_early_stopping:

            self.write('Patience: {}'.format(self.patience))

        if n_channels>1:

            self.write('Number of channels: {}'.format(n_channels))

        self.write('----------------------------')
        optimal_sigma = []
        for C in range(n_channels):

            x_for_optimization = x
            if n_channels > 1:

                self.write('Optimization of channel {}'.format(C+1))
                x_for_optimization = x[...,C]

            Ls = []
            for idx1, slice in enumerate(x_for_optimization):

                _, H0_dx = loss_components(slice)
                sigma0 = sigmas[0]

                # flat_slice = slice - skfilt.gaussian(slice, sigma0, preserve_range=True)
                flat_slice = slice - gaussian_filter2d(slice,sigma0)

                H_x0, H_dx0 = loss_components(flat_slice - np.min(flat_slice))
                L = [1]
                for idx2,sigma in enumerate(sigmas[1:]):

                    self.progress_bar(idx2+2,len(sigmas[1:]),15,
                                      'slice {}/{} | sigma {}/{}'.format(idx1+1,len(x),idx2+2,len(sigmas)))

                    # flat_slice = slice - skfilt.gaussian(slice, sigma, preserve_range=True)
                    flat_slice = slice - gaussian_filter2d(slice,sigma)

                    H_x, H_dx = loss_components(flat_slice - np.min(flat_slice))
                    l = 1/3*(H_x/H_x0+H_dx0/H_dx0+np.abs(H_dx-H0_dx)/np.abs(H_dx0-H0_dx))               # loss function
                    l = l+1/3*self.regularization_strength*((sigma-self.sigma_min)/np.max(sigmas))**30  # regularization

                    # early stopping
                    if self.use_early_stopping and\
                       (np.where(L[-self.patience:] == np.min(L[-self.patience::]))[0] == 0).any() and \
                       len(L[-self.patience:]) == self.patience:

                        self.write('Early-stopping: Loss did\'t decrease for the last {} parameter changes, optimization '
                                   'for slice {} terminated earlier!'.format(self.patience,idx1+1))
                        break

                    else:

                        L.append(l)

                Ls.append(np.array(L))

            min_len = np.min([len(ls) for ls in Ls])
            Ls = np.array([ls[:min_len] for ls in Ls])
            optimum = sigmas[np.argmin(Ls.mean(axis=0))]    # one sigma for all slices
            optimal_sigma.append(optimum)

        if n_channels == 1:

            optimal_sigma = optimal_sigma[0]

        self.write('Optimal value(s) for \'sigma_low_pass\': {}'.format(optimal_sigma))
        return optimal_sigma

    def fit(self,x):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        if self.fit_enable and self.auto_optimize:

            if x.data_type in [np.uint8,np.uint16,np.uint32,np.uint64]:

                F = np.iinfo(x.data_type).max+1
                self.image_range = (self.image_range[0]*F,self.image_range[1]*F)
                self.derivative_range = (self.derivative_range[0]*F,self.derivative_range[1]*F)

            vol_for_optimization = x.data[::self.fit_step,...]
            if self.sigma_max == 'auto':

                self.sigma_max = np.minimum(vol_for_optimization.shape[1],vol_for_optimization.shape[2])//4 # kernel truncation is gaussian filter happens after 4 sigma -> so should be divided by 8, no?.

            if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                    and not self.force_serial:

                self.sigma_low_pass = self._fit_parallel(vol_for_optimization,x.n_channels)

            else:

                self.sigma_low_pass = self._fit_serial(vol_for_optimization, x.n_channels)

    def _transform_serial(self,x):
        """
        Core transformation which is essentially an high-pass filter on the image. Serial implementation.

        :param x: (Stack) stack to transform.
        :return: the transformed stack.
        """
        if x.n_channels > 1:

            if type(self.sigma_low_pass) is int or type(self.sigma_low_pass) is float:

                self.sigma_low_pass = x.n_channels * [self.sigma_low_pass]

            elif len(self.sigma_low_pass) != x.n_channels:

                warnings.warn('Channel\'s ambiguity: the input stack has {} channels but \'sigma_low_pass\' has length '
                              '{}. Only the first element of \'sigma_low_pass\' is used: the plugin applies the same '
                              'filter to all channels. To apply different filters to each channels, specify a '
                              '\'sigma_low_pass\' parameter having the number of dimension equal to the number of '
                              'channels of the stack.'.format(x.n_channels,len(self.sigma_low_pass)))
                self.sigma_low_pass = x.n_channels*[self.sigma_low_pass[0]]

            for C in range(x.n_channels):

                # x.data[...,C] = x.data[...,C]-skfilt.gaussian(x.data[...,C],(0,self.sigma_low_pass[C],self.sigma_low_pass[C]),preserve_range=True)
                x.data[...,C] = x.data[...,C]-gaussian_filter2d(x.data[...,C],self.sigma_low_pass[C])

            return x.data+np.expand_dims(x.slices_means,axis=tuple(np.arange(-(len(x.shape)-1),0)))

        else:

            x_transformed = []
            for z in range(x.shape[0]):

                x_transformed.append( x.data[z,...]-gaussian_filter2d(x.data[z,...],self.sigma_low_pass) )

        return np.array(x_transformed)+np.expand_dims(x.slices_means,axis=tuple(np.arange(-(len(x.shape)-1),0)))

    def _transform_parallel(self,x):
        """
        Core transformation which is essentially an high-pass filter on the image. Parallel implementation.

        :param x: (Stack) stack to transform.
        :return: the transformed stack.
        """
        if x.n_channels > 1:

            if type(self.sigma_low_pass) is int or type(self.sigma_low_pass) is float:

                self.sigma_low_pass = x.n_channels * [self.sigma_low_pass]

            elif len(self.sigma_low_pass) != x.n_channels:

                warnings.warn('Channel\'s ambiguity: the input stack has {} channels but \'sigma_low_pass\' has length '
                              '{}. Only the first element of \'sigma_low_pass\' is used: the plugin applies the same '
                              'filter to all channels. To apply different filters to each channels, specify a '
                              '\'sigma_low_pass\' parameter having the number of dimension equal to the number of '
                              'channels of the stack.'.format(x.n_channels,len(self.sigma_low_pass)))
                self.sigma_low_pass = x.n_channels*[self.sigma_low_pass[0]]

            # parallelization on the slices (channel kept constant)
            x_transformed = []
            for C in range(x.n_channels):

                def func_to_par(z):

                    # return x.data[z,:,:,C]-skfilt.gaussian(x.data[z,:,:,C],self.sigma_low_pass[C],preserve_range=True)
                    return x.data[z,:,:,C]-gaussian_filter2d(x.data[z,:,:,C],self.sigma_low_pass[C])

                x_transformed_C = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(z) for z in range(x.n_slices))
                x_transformed.append(np.array(x_transformed_C))

            return x_transformed.traspose((1,2,3,0))+np.expand_dims(x.slices_means,axis=tuple(np.arange(-(len(x.shape)),0)))

        # parallelization on the slices
        def func_to_par(z):

            # return x.data[z,...]-skfilt.gaussian(x.data[z,...],self.sigma_low_pass,preserve_range=True)
            return x.data[z,...]-gaussian_filter2d(x.data[z,...],self.sigma_low_pass)

        x_transformed = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(z) for z in range(x.n_slices))
        return np.array(x_transformed)+np.expand_dims(x.slices_means,axis=tuple(np.arange(-(len(x.shape)-1),0)))

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if self.auto_optimize:

            self.fit(x)

        elif not hasattr(self,'sigma_low_pass'):

            raise ValueError('No parameter \'sigma_low_pass\' present: auto-optimize the transformation or specify it '
                             'in the transformation dictionary.')

        if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                and not self.force_serial:    # parallel transform

            if not inplace:

                return self._transform_parallel(x)

            x.from_array(self._transform_parallel(x))

        else:       # serial transform

            if not inplace:

                return self._transform_serial(x)

            x.from_array(self._transform_serial(x))