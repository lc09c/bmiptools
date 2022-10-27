# Title: 'denoiser.py'
# Date: 25/03/2021
# Author: Curcuraci L.
#
# Scope: Class performing denoising on a stack.
#
# Source:
#
# [1] J. Batson & L. Royer. Noise2Self: Blind Denoising by Self-Supervision, International Conference on Machine
#     Learning, p. 524-533 (2019)
# [2] https://scikit-image.org/docs/stable/auto_examples/filters/plot_j_invariant_tutorial.html
# [3] https://scikit-image.org/docs/dev/api/skimage.restoration.html
# [4] https://github.com/juglab/n2v
# [5] arXiv:1901.11365
#
# Updates:
#
# - 22/12/21: * Filters added (all the one available in skimage);
#             * J-invariant loss optimization for hyperparameters search (despite 'bilateral' does not seem to be
#               compatible with the j-invariance optimization scheme);
#             * n2v block rewritten and compatible with the last n2v version;
#             * J-invariance scheme for architecture research, despite no-comparison between n2v model and other filters
#               seem reliable (and also between the 2d and 3d variant of the same n2v).
#
# - 05/01/22: * GuiPI dictionary added for automatic generation of a graphical interface
#             * Old "Denoiser" class split in 2. The new classes are:
#
#                                - "Denoiser": with non neural network based filtering methods;
#                                - "DenoiserDNN": with neural network based filtering methods.
#
# Improvements:
#
# - Add MB3D method (https://pypi.org/project/bm3d/). What is the best 'psd'?
# - StructN2V possible but no research of the mask is done at them moment during the hyperparameter optimization. Add it?

"""
Plugins performing denoising on a stack. They are:

    - "Denoiser": with non neural network based filtering methods;

    - "DenoiserDNN": with neural network based filtering methods.

"""

#################
#####   LIBRARIES
#################


import numpy as np
import pywt
import os
import glob
from datetime import datetime
import copy
import shutil
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'    # suppress INFO messages from tensorflow

from skimage import img_as_float
from skimage.restoration import denoise_wavelet,estimate_sigma,calibrate_denoiser,denoise_tv_bregman,\
    denoise_nl_means,denoise_bilateral,denoise_tv_chambolle
from joblib import Parallel,delayed
from n2v.models import N2VConfig, N2V
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator

import bmiptools
import bmiptools.core.utils as ut
from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI

####

# "correct" import
# from bmiptools.transformation.restoration._restoration_shared import SUPPORTED_WAVELET,SUPPORTED_WAVELET_FAMILIES,\
#     generate_parameter_space

# "sphinx.ext.autosummary compatible" import (use this during the documentation compilation)
from bmiptools.transformation.restoration._restoration_shared import generate_parameter_space
import pywt
import re

SUPPORTED_WAVELET = pywt.wavelist(kind='discrete')
SUPPORTED_WAVELET_FAMILIES = list(set(map(lambda x:re.sub('[0-9]','',x).replace('.',''),SUPPORTED_WAVELET)))

####


###############
#####   CLASSES
###############


# TODO: DenoiseDNN does not handle multichannel stacks.


class Denoiser(TransformationBasic):
    """
    Class used to apply classical denoising transformations to a stack
    """

    __version__ = '0.2'
    empty_transformation_dictionary = {'auto_optimize': True,
                                       'optimization_setting': {'tested_filters_list': \
                                                                    ['wavelet','tv_chambolle','nl_means'],
                                                                'wavelet': {'level_range': [1,9,1],
                                                                            'wavelet_family': 'db',
                                                                            'mode_range': ['soft','hard'],
                                                                            'method_range': ['BayesShrink','VisuShrink']
                                                                            },
                                                                'tv_chambolle': {'weights_tvch_range':[1e-5,1,100]
                                                                                 },
                                                                'tv_bregman': {'weights_tvbr_range':[1e-5,1,100],
                                                                               'isotropic_range': [False,True]
                                                                               },
                                                                'bilateral': {'sigma_color_range': [0.5,1,5],
                                                                              'sigma_spatial_range': [1,30,2]
                                                                              },
                                                                'nl_means': {'patch_size_range': [5,100,5],
                                                                             'patch_distance_range': [5,100,5],
                                                                             'h_relative_range': [0.1,1.2,15]
                                                                             },
                                                                'opt_bounding_box': {'use_bounding_box': True,
                                                                                     'y_limits_bbox': [-500,None],
                                                                                     'x_limits_bbox': [500,1500]
                                                                                      },
                                                                'fit_step':10
                                                                },
                                       'filter_to_use': 'tv_chambolle',
                                       'filter_params': [['weight', 0.2]],
                                       }
    _guipi_dictionary = {'auto_optimize': GuiPI(bool),
                       'optimization_setting': {'tested_filters_list': GuiPI(list),
                                                'wavelet': {'level_range': GuiPI('range int'),
                                                            'wavelet_family': GuiPI('options',options=['all',]+SUPPORTED_WAVELET_FAMILIES),
                                                            'mode_range': GuiPI(list),
                                                            'method_range': GuiPI(list)},
                                                'tv_chambolle': {'weights_tvch_range': GuiPI('span float')},
                                                'tv_bregman': {'weights_tvbr_range': GuiPI('span float'),
                                                               'isotropic_range': GuiPI(list)},
                                                'bilateral': {'sigma_color_range': GuiPI('span float',min=0.1,max=1.),
                                                              'sigma_spatial_range': GuiPI('range int')},
                                                'nl_means': {'patch_size_range': GuiPI('range int'),
                                                             'patch_distance_range': GuiPI('range int'),
                                                             'h_relative_range': GuiPI('span float')},
                                                'opt_bounding_box': {'use_bounding_box': GuiPI(bool),
                                                                     'y_limits_bbox': GuiPI('math'),
                                                                     'x_limits_bbox': GuiPI('math')},
                                                'fit_step':GuiPI(int)},
                       'filter_to_use': GuiPI(str),
                       'filter_params': GuiPI(list)}
    def __init__(self,transformation_dictionary,force_serial=False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'auto_optimize': (boolean) if True the plugin  start an optimization routine according to all the specs
            contained in the 'optimization_setting' field. The optimization routine try to find the best filter and
            parameter combination in the sense of J-invariance.

            'optimization_setting': (dict) Dictionary containing the setting optimization routine. The dictionary has
            to be specified as below:

                {'tested_filter_list': (list of str) list containing the name of the filters which are tested during the
                optimization routines. The available filters are the name of the other fields of this dictionary.

                'wavelet': (dict) dictionary containing the parameter rage and options used for a wavelet filter during
                the optimization routine. The dictionary has to be specified as below:

                    {'level_range': (list) list defining the range over which the decomposition level parameter of the
                    wavelet filter is searched. It has to be specified as below:

                                            [level min, level max, step size]

                    'wavelet_family': (str) this field can be:

                        * 'all', to do the hyperparameters search among all the discrete wavelet of pywavelet;
                        * a name of a discrete wavelet family available in pywavelet, to do the hyperparameters search
                          only among the wavelet of this family;

                    'mode_range': (list of str) in this list the thresholding mode of the wavelet filter. The available
                    mode are:

                        * 'soft';
                        * 'hard'.

                    'method_range': (list of str) in this list the methods used to define the threshold below which the
                    wavelet coefficients are shrink among which the hyperparameters search is performed. The available
                    methods are:

                        * 'VisuShrink';
                        * 'BayesShrink'.

                    }

                'tv_chambolle': (dict) dictionary containing the parameter rage of the Chambolle total-variational
                denoising filter during the optimization routine. The dictionary has to be specified as below:

                    {'weights_tvch_range': (list) list specifying the weight parameter of the Chambolle
                    total-variational denoiser used during the hyperparameter search. It has to be specified as
                    indicated below:

                                                    [weight min, weight max, number of steps]

                    }

                    'tv_bregman': (dict) dictionary containing the parameter rage of the Bregman total- variational
                    denoising filter. The dictionary has to be specified as below:

                    {'weights_tvbr_range': (list) list specifying the weight parameter of the Bregman total-variational
                    denoiser used during the hyperparameter search. It has to be specified as indicated below:

                                                    [weight min, weight max, number of steps]

                    'isotropic_range': (list of booleans) list specifying the isotropic parameters of the Bregman
                    total-variational denoiser used during the hyperparameter search.

                    }

                    'bilateral': (dict) dictionary containing the parameter rage of the bilateral filter during the
                    optimization routine. The dictionary has to be specified as below:

                        {'sigma_color_range': (list) list specifying the range of the parameter 'sigma_color' of the
                        bilateral filter used during the hyperparameter search. It has to be specified as indicated
                        below:

                                                     [value min, value max, number of steps]

                        'sigma_spatial_range': (list) list specifying the range of the parameter 'sigma_spatial' of the
                        bilateral filter used during the hyperparameter search. It has to be specified as indicated
                        below:

                                                      [value min, value max, step size]
                        }

                    'nl_means': (dict) dictionary containing the parameter rage of the non-local mean filter during the
                    optimization routine. The dictionary has to be specified as below:

                        {'patch_size_range': (list of int) list specifying the range of the parameter 'patch_size' of
                        the non-local mean filter used during the hyperparameter search. It has to be specified as
                        indicated below:

                                                       [value min, value max, step size]

                        'patch_distance_range': (list of int) list specifying the range of the parameter
                        'patch_distance' of the non-local mean filter used during the hyperparameter search. It has to
                        be specified as indicated below:

                                                       [value min, value max, step size]

                        'h_relative_range': (list of int) list specifying the range of the parameter 'h' of the
                        non-local mean filter used during the hyperparameter search. The true parameter 'h' of
                        the filter, is obtained by multiplying the 'h_relative' parameter by the standard deviation of
                        the noise present on the image (which is estimated), namely

                                                    h = h_relative * estimated_sigma_noise

                        It has to be specified as indicated below:

                                                    [value min, value max, number of steps]

                        }

                    'opt_bounding_box': (dict) dictionary containing the setting of the bounding box used during the
                    optimization. The bounding box defines the part of the stack (in the YX plane) which is considered
                    by the optimization routine. It has to be specified as below:

                        {'use_bounding_box': (bool) if True the bounding box is used, otherwise the whole YX plane is
                        used. In this last case the two arguments below are ignored.

                        'y_limits_bbox' <- (list) list specifying the extrema along the Y-direction (i.e. axis 0). This
                        list can contain numpy-like instruction for the definition of the range. The following examples
                        should clarify the usage. Let arr be a numpy array

                                             [100,300]   => arr[100:300,:]

                                             [-500,None] => arr[-500:,:]

                                             [None,200]  => arr[:200,:]

                        'x_limits_bbox': (list) list specifying the extrema along the X-direction (i.e. axis 1). This
                        list can contain numpy-like instruction for the definition of the range. The following examples
                        should clarify the usage. Let arr be a numpy array

                                              [100,300]   => arr[:,100:300]

                                              [-500,None] => arr[:,-500:]

                                              [None,200]  => arr[:,:200]

                        }

                    'fit_step':(int) interval between two slices of the stack that are used during the optimization. If
                    1 all the stack is used, for n>1 only the slices having a distance of n on the 0-axis (i.e. the
                    z-direction). This parameter therefore determine the number of slices used during the optimization,
                    which is equal to (image_size_z)//n.

                    }

            'filter_to_use': (str) Name of the filter chosen. This field is ignore when the auto-optimization is done, since
            in that case the filter found in the optimization routine is used. It can be:

                * 'wavelet';
                * 'tv_chambolle';
                * 'tv_bregman';
                * 'bilateral';
                * 'nl_means'.

            'filter_params': (list of list) list specifying the parameter to be used for the filter selected in the field
            'filter_to_use'. This field is ignored when the auto-optimization is done, and in that case the parameter of
            the best filters found during the optimization routine are used. For manual specification of the parameters of
            the filter available in this plugin, see [3]. It has to be specified as below

                                    [[name_parameter_1, value_parameter_1],

                                    [name_parameter_2, value_parameter_2],

                                    ...],
            }


        :param transformation_dictionary: dictionary containing all the transformation options.
        :param force_serial: (bool) if True serial behavior is forced for this plugin independently on the global
                             setting of bmiptools.
        """
        super(Denoiser,self).__init__()
        self.force_serial = force_serial
        self._available_denoiser = {'wavelet': denoise_wavelet,
                                    'tv_chambolle': denoise_tv_chambolle,
                                    'tv_bregman': denoise_tv_bregman,
                                    'bilateral': denoise_bilateral,
                                    'nl_means': denoise_nl_means}

        self.auto_optimize = transformation_dictionary['auto_optimize']
        if self.auto_optimize:

            self.tested_filters_list = transformation_dictionary['optimization_setting']['tested_filters_list']
            if 'wavelet' in self.tested_filters_list:

                self.level_range = transformation_dictionary['optimization_setting']['wavelet']['level_range']
                self.wavelet_family = transformation_dictionary['optimization_setting']['wavelet']['wavelet_family']
                self.mode_range = transformation_dictionary['optimization_setting']['wavelet']['mode_range']
                self.method_range = transformation_dictionary['optimization_setting']['wavelet']['method_range']

            if 'tv_chambolle' in self.tested_filters_list:

                self.weights_tvch_range = \
                    transformation_dictionary['optimization_setting']['tv_chambolle']['weights_tvch_range']

            if 'tv_bregman' in self.tested_filters_list:

                self.weights_tvbr_range = \
                    transformation_dictionary['optimization_setting']['tv_bregman']['weights_tvbr_range']
                self.isotropic_range = \
                    transformation_dictionary['optimization_setting']['tv_bregman']['isotropic_range']

            if 'bilateral' in self.tested_filters_list:

                self.sigma_color_range = \
                    transformation_dictionary['optimization_setting']['bilateral']['sigma_color_range']
                self.sigma_spatial_range = \
                    transformation_dictionary['optimization_setting']['bilateral']['sigma_spatial_range']

            if 'nl_means' in self.tested_filters_list:

                self.patch_size_range = \
                    transformation_dictionary['optimization_setting']['nl_means']['patch_size_range']
                self.patch_distance_range = \
                    transformation_dictionary['optimization_setting']['nl_means']['patch_distance_range']
                self.h_relative_range = \
                    transformation_dictionary['optimization_setting']['nl_means']['h_relative_range']

            self.use_bounding_box = \
                transformation_dictionary['optimization_setting']['opt_bounding_box']['use_bounding_box']
            if self.use_bounding_box:

                self.y_limits_bbox = \
                    transformation_dictionary['optimization_setting']['opt_bounding_box']['y_limits_bbox']
                self.x_limits_bbox = \
                    transformation_dictionary['optimization_setting']['opt_bounding_box']['x_limits_bbox']

            self.fit_step = transformation_dictionary['optimization_setting']['fit_step']

        self.filter_to_use = transformation_dictionary['filter_to_use']
        self.filter_params = transformation_dictionary['filter_params']

        self._setup()

    def _setup(self):

        if self.auto_optimize:

            # check tested_denoiser_list
            assert len(self.tested_filters_list)>0, 'There must be at least one filter in \'tested_filter_list\''

            for filt in self.tested_filters_list:

                if not filt in self._available_denoiser.keys():

                    raise ValueError('Filter {} not recognized. Use a filter name '
                                     'present in the list below {}'.format(filt,list(self._available_denoiser.keys())))

            # generate wavelet parameter space
            self._Jopt_parameter_dict = {}
            if 'wavelet' in self.tested_filters_list:

                if self.wavelet_family == 'all':

                    wlts = SUPPORTED_WAVELET

                elif self.wavelet_family in SUPPORTED_WAVELET_FAMILIES:

                    wlts = pywt.wavelist(self.wavelet_family)

                else:

                    raise ValueError('Unrecognized \'wavelet_family\' {}. Set this parameter equal to \'all\' if'
                                     'you want to search for the optimal wavelet denoiser over all the discrete'
                                     'wavelets, or to some wavelet family name listed below, to search the optimal'
                                     'wavelet denoiser restricted to a particular wavelet family. Available '
                                     'wavelet families are \n{}'.format(self.wavelet_family,SUPPORTED_WAVELET_FAMILIES))

                self._Jopt_parameter_dict.update({'wavelet': {'wavelet': wlts,
                                                              'wavelet_levels': list(range(*self.level_range)),
                                                              'mode': self.mode_range,
                                                              'method':self.method_range}})

            if 'tv_chambolle' in self.tested_filters_list:

                self._Jopt_parameter_dict.update({'tv_chambolle': {'weight': np.linspace(*self.weights_tvch_range)}})

            if 'tv_bregman' in self.tested_filters_list:

                self._Jopt_parameter_dict.update({'tv_bregman': {'weight': np.linspace(*self.weights_tvbr_range),
                                                                 'isotropic': self.isotropic_range}})

            if 'bilateral' in self.tested_filters_list:

                self._Jopt_parameter_dict.update({'bilateral': {'sigma_color': np.linspace(*self.sigma_color_range),
                                                                'sigma_spatial': np.arange(*self.sigma_spatial_range)}})

            if 'nl_means' in self.tested_filters_list:

                self._Jopt_parameter_dict.update({'nl_means': None})

        else:

            if not self.filter_to_use in list(self._available_denoiser):

                raise ValueError('Filter \'{}\' in \'filter_to_use\' field of the transformation dictionary is not '
                                 'recognized. Available filters for this plugin are listed below '
                                 '\n{}'.format(self.filter_to_use,list(self._available_denoiser)))

            if self.filter_params != None:

                self.filter_params = {item[0]: item[1] for item in self.filter_params}

            if self.filter_params == None or len(self.filter_params) == 0:

                raise ValueError('No parameters specified for the filter {} in \'filter_params\' field of the '
                                 'transformation dictionary. Run automatic optimization if not reasonable filter '
                                 'parameters are known'.format(self.filter_to_use))

    def _nl_means_parameter_space(self,x):
        """
        Generate parameter space for non-local mean denoiser.

        :param x: (ndarray) sample image(s) for noise estimation
        """
        sigma_est = estimate_sigma(x)
        self._Jopt_parameter_dict['nl_means'] = {'patch_size': list(range(*self.patch_size_range)),
                                                 'patch_distance': list(range(*self.patch_distance_range)),
                                                 'h': sigma_est*np.linspace(*self.h_relative_range),
                                                 'sigma':[sigma_est]}

    def _Jinvariance_optimization(self,x,denoise_function,parameter_space):
        """
        Find the best parameter for the filter by using J-invariance assumption. The optimization is done
        with a simple grid-search.

        :param x: (nparray) images (with noise) used to optimize the filter. The following shape is assumed
                  (n_images,y_dim,x_dim) for x made of 'n_images' with dimensions 'y_dim' x 'x_dim'.
        :param denoise_function: (function) function used to denoise the images.
        :param parameter_space: (dict) dictionary containing the parameters range on which the filter is optimized: the
                                key of the dictionary have to be the name of the parameters of the 'denoise_function',
                                while the value of the dictionary are lists of the possible values these parameters may
                                assume.
        :return: best parameters for the 'denoise_function' among the one given in the 'parameter_space'.
        """
        total_loss = 0
        for i in self.vtqdm(range(len(x))):     # Multichannel!!!!!!!!

            _,(params,loss) = calibrate_denoiser(x[i,...],
                                                 denoise_function,
                                                 denoise_parameters=parameter_space,
                                                 extra_output=True)
            total_loss = total_loss+np.array(loss)

        return params[np.argmin(total_loss)],np.argmin(total_loss)/len(x)

    def fit(self,x):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        if self.use_bounding_box:

            ymin,ymax = self.y_limits_bbox
            xmin,xmax = self.x_limits_bbox

        else:

            ymin = xmin = ymax = xmax = None

        self.write('Denoiser optimization routine')
        self.write('----------------------------')
        self.write('Optimization method: grid search.')
        self.opt_params_per_filter = {}
        score_list = []
        for n,filter_name in enumerate(self.tested_filters_list):

            self.progress_bar(n,len(self.tested_filters_list),15,text_after='Current filter tested: {}'.format(filter_name))
            vol_for_optimization = x[::self.fit_step,ymin:ymax,xmin:xmax,...]
            if x.n_channels > 1:  # Temporary solution for multichannel images: only the first channel is considered

                vol_for_optimization = vol_for_optimization[...,0]

            if 'nl_means' in self.tested_filters_list:

                self._nl_means_parameter_space(vol_for_optimization[0,...])

            current_params_space = self._Jopt_parameter_dict[filter_name]
            current_filter = self._available_denoiser[filter_name]
            opt_params,score = \
                self._Jinvariance_optimization(vol_for_optimization,current_filter,current_params_space)



            self.opt_params_per_filter.update({filter_name: {'score': score, 'params': opt_params}})
            score_list.append(score)

        best_filter_idx = np.argmin(score_list)
        self.filter_to_use = list(self.opt_params_per_filter)[best_filter_idx]
        self.filter_params = self.opt_params_per_filter[self.filter_to_use]['params']
        self.write('Optimization terminated!')
        self.write('Best filter: {} \n'
                   'Best filter parameters: {}'.format(self.filter_to_use,self.filter_params))
        self.write('----------------------------')

    def _filter_stack_serial(self,x):
        """
        Apply a filter to denoise a stack.

        :param x: (nparray) stack to denoise.
        :return: (nparray) denoised stack.
        """
        transformed_x = []
        if x.n_channels > 1:

            for i in range(len(x)):

                transformed_x_per_C = []
                for C in range(x.n_channels):

                    tmp = self._available_denoiser[self.filter_to_use](x.data[i,...,C],**self.filter_params)
                    transformed_x_per_C.append(tmp)

                transformed_x.append(transformed_x_per_C)

            return np.array(transformed_x).transpose((1,2,3,0))

        else:

            for i in range(len(x)):

                tmp = self._available_denoiser[self.filter_to_use](x.data[i,...],**self.filter_params)

            transformed_x.append(tmp)
            return np.array(transformed_x)

    def _filter_stack_parallel(self, x):
        """
        Core method. Parallel implementation of the application of the wavelet-fourier filer to a stack.

        :param x: stack object on which the transformation is applied.
        :return: array containing the transformed data.
        """

        def func_to_par(slice):
            """
            function to parallelize
            """
            denoised_slice = self._available_denoiser[self.filter_to_use](slice,**self.filter_params)
            return denoised_slice

        if x.n_channels > 1:

            transformed_volume = []
            for C in range(x.n_channels):

                transformed_volume_C = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(slice) for slice in x.data[...,C])
                transformed_volume.append(transformed_volume_C)

            return np.array(transformed_volume).transpose((1,2,3,0))

        transformed_volume = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(slice) for slice in x.data)
        return np.array(transformed_volume)

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if self.fit_enable and self.auto_optimize:

            self.fit(x)

        if not self.filter_to_use in ['n2v_2d','n2v_3d']:

            if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                    and not self.force_serial:

                if not inplace:

                    return self._filter_stack_parallel(x)

                x.from_array(self._filter_stack_parallel(x))

            else:

                if not inplace:

                    return self._filter_stack_serial(x)

                x.from_array(self._filter_stack_serial(x))

        else:

            if self.filter_to_use == 'n2v_2d':

                if not inplace:

                    return self._filter_n2v_2d_stack(x)

                x.from_array(self._filter_n2v_2d_stack(x))

            else:

                if not inplace:

                    return self._filter_n2v_3d_stack(x)

                x.from_array(self._filter_n2v_3d_stack(x))


class DenoiserDNN(TransformationBasic):
    """
    Class used to apply denoising transformations based on DNN to a stack
    """

    _undillable_path_attributes = 'path_to_trained_n2v_model'
    __version__ = '0.2'
    n2v_default_setting_dictionary = {'unet_kern_size': 3,
                                      'train_steps_per_epoch': 10,
                                      'train_epochs': 40,
                                      'train_loss': 'mse',
                                      'batch_norm': True,
                                      'train_batch_size': 128,
                                      'n2v_perc_pix': 0.198,
                                      'n2v_patch_shape': (64,64),
                                      'n2v_manipulator': 'uniform_withCP',
                                      'n2v_neighborhood_radius': 5}
    # n2v_default_setting_dictionary = {'unet_kern_size': 3,
    #                                   'train_steps_per_epoch': 24,
    #                                   'train_epochs': 30,
    #                                   'train_loss': 'mse',
    #                                   'batch_norm': True,
    #                                   'train_batch_size': 8,
    #                                   'n2v_perc_pix': 2,
    #                                   'n2v_patch_shape': (64,64),
    #                                   'n2v_manipulator': 'uniform_withCP',
    #                                   'n2v_neighborhood_radius': 5}
    empty_transformation_dictionary = {'auto_optimize': True,
                                       'optimization_setting': {'tested_filters_list': ['n2v_2d'],
                                                                'n2v_2d': {'unet_kern_size_2d_list': [3,5,7],
                                                                           'train_batch_size_2d_list': [128],
                                                                           'n2v_patch_shape_2d_list': [64],
                                                                           'train_epochs_2d_list': [30],
                                                                           'train_loss_2d_list': ['mse','mae'],
                                                                           'n2v_manipulator_2d_list': ['uniform_withCP',
                                                                                                    'normal_withoutCP',
                                                                                                    'normal_additive',
                                                                                                    'normal_fitted'],
                                                                           'n2v_neighborhood_radius_2d_list': \
                                                                                                        [5,10,15,20]
                                                                           },
                                                                'n2v_3d': {'unet_kern_size_3d_list': [3,5,7],
                                                                           'train_batch_size_3d_list': [128],
                                                                           'n2v_patch_shape_3d_list': [(32,64,64)],
                                                                           'train_epochs_3d_list': [30],
                                                                           'train_loss_3d_list': ['mse','mae'],
                                                                           'n2v_manipulator_3d_list': ['uniform_withCP',
                                                                                                    'normal_withoutCP',
                                                                                                    'normal_additive',
                                                                                                    'normal_fitted'],
                                                                           'n2v_neighborhood_radius_3d_list': \
                                                                                                        [5,10,15,20]
                                                                           },
                                                                'opt_bounding_box': {'use_bounding_box': True,
                                                                                     'y_limits_bbox': [-500,None],
                                                                                     'x_limits_bbox': [500,1500]
                                                                                      },
                                                                'fit_step': 10
                                                                },
                                       'filter_to_use': 'n2v_2d',
                                       'filter_params': None,
                                       'trained_n2v_setting': {'use_trained_n2v_model': False,
                                                               'path_to_trained_n2v_model': '',
                                                               'save_trained_n2v_model': False,
                                                               'saving_path': ''}
                                       }
    _guipi_dictionary = {'auto_optimize': GuiPI(bool),
                         'optimization_setting': {'tested_filters_list': GuiPI(list),
                                                  'n2v_2d': {'unet_kern_size_2d_list': GuiPI(list),
                                                             'train_batch_size_2d_list': GuiPI(list),
                                                             'n2v_patch_shape_2d_list': GuiPI(list),
                                                             'train_epochs_2d_list': GuiPI(list),
                                                             'train_loss_2d_list': GuiPI(list),
                                                             'n2v_manipulator_2d_list': GuiPI(list),
                                                             'n2v_neighborhood_radius_2d_list': GuiPI(list)},
                                                  'n2v_3d': {'unet_kern_size_3d_list': GuiPI(list),
                                                             'train_batch_size_3d_list': GuiPI(list),
                                                             'n2v_patch_shape_3d_list': GuiPI(list),
                                                             'train_epochs_3d_list': GuiPI(list),
                                                             'train_loss_3d_list': GuiPI(list),
                                                             'n2v_manipulator_3d_list': GuiPI(list),
                                                             'n2v_neighborhood_radius_3d_list': GuiPI(list)},
                                                  'opt_bounding_box': {'use_bounding_box': GuiPI(bool),
                                                                       'y_limits_bbox': GuiPI('math'),
                                                                       'x_limits_bbox': GuiPI('math')},
                                                  'fit_step':GuiPI(int)},
                         'filter_to_use': GuiPI(str),
                         'filter_params': GuiPI(list),
                         'trained_n2v_setting': {'use_trained_n2v_model': GuiPI(bool),
                                                 'path_to_trained_n2v_model': GuiPI('path'),
                                                 'save_trained_n2v_model': GuiPI(bool,visible=False),
                                                 'saving_path': GuiPI('path',visible=False)}}
    def __init__(self,transformation_dictionary,force_serial=False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'auto_optimize': (boolean) if True the plugin  start an optimization routine according to all the specs
            contained in the 'optimization_setting' field. The optimization routine try to find the best filter and
            parameter combination in the sense of J-invariance.

            'optimization_setting': (dict) Dictionary containing the setting optimization routine. The dictionary has
            to be specified as below:

                {'tested_filter_list' : (list of str) list containing the name of the filters which are tested during
                the optimization routines. The available filters are the name of the other fields of this dictionary.

                'n2v_2d': (dict) dictionary containing the parameter rage and options used for a n2v 2d filter during
                the optimization routine. The dictionary has to be specified as below:

                    {'unet_kern_size_2d_list': (list of int) list of all the possible 'kernel_size' parameter used
                    during the hyperparameters optimization routine. This parameter can be equal only to 3,5 or 7.

                    'train_batch_size_2d_list': (list of int) list of all the possible 'batch_size' parameter used
                    during the hyperparameters optimization routine.

                    'n2v_patch_shape_2d_list': (list of int) list of all the possible 'patch_shape' parameter used
                    during the hyperparameters optimization routine.

                    'train_epochs_2d_list': (list of int) list of all the possible 'epochs' parameter used during the
                    hyperparameters optimization routine.

                    'train_loss_2d_list': (list of str) list of all the possible 'train_loss' parameter used during the
                    hyperparameters optimization routine. This parameter can be

                        * 'mse';
                        * 'mae'.

                    'n2v_manipulator_2d_list': (list of str) list of all the possible 'n2v_manipulator' parameter used
                    during the hyperparameters optimization routine. This parameter can be:

                        * 'uniform_withCP';
                        * 'normal_withoutCP';
                        * 'normal_additive';
                        * 'normal_fitted';
                        * 'idenitity' (should not be used).

                    'n2v_neighborhood_radius_2d_list':  (list of int) list of all the possible 'n2v_neighborhood_radius'
                    parameter used during the hyperparameters optimization routine.

                    }

                'n2v_3d': (dict) dictionary containing the parameter rage and options used for a n2v 2d filter during
                the optimization routine. The entries of this field are the same of the dictionary above with the same
                meaning, but '3d' have to be used in the name of the key of the dictionary rather than '2d'.

                'opt_bounding_box': (dict) dictionary containing the setting of the bounding box used during the
                optimization. The bounding box defines the part of the stack (in the YX plane) which is considered by
                the optimization routine. It has to be specified as below:

                    {'use_bounding_box': (bool) if True the bounding box is used, otherwise the whole YX plane is
                    used. In this last case the two arguments below are ignored.

                    'y_limits_bbox': (list) list specifying the extrema along the Y-direction (i.e. axis 0). This
                    list can contain numpy-like instruction for the definition of the range. The following examples
                    should clarify the usage. Let arr be a numpy array

                                       [100,300]   => arr[100:300,:]

                                       [-500,None] => arr[-500:,:]

                                       [None,200]  => arr[:200,:]

                    'x_limits_bbox': (list) list specifying the extrema along the X-direction (i.e. axis 1). This list
                    can contain numpy-like instruction for the definition of the range. The following examples should
                    clarify the usage. Let arr be a numpy array

                                       [100,300]   => arr[:,100:300]

                                       [-500,None] => arr[:,-500:]

                                       [None,200]  => arr[:,:200]

                    }

                'fit_step': (int) interval between two slices of the stack that are used during the optimization. If 1
                all the stack is used, for n>1 only the slices having a distance of n on the 0-axis (i.e. the
                z-direction). This parameter therefore determine the number of slices used during the optimization,
                which is equal to (image_size_z)//n.

                }

            'filter_to_use': (str) Name of the filter chosen. This field is ignore when the auto-optimization is done,
            since in that case the filter found in the optimization routine is used. It can be:

                 * 'n2v_2d';
                 * 'n2v_3d';

            'filter_params': (list of list) list specifying the parameter to be used for the filter selected in the
            field 'filter_to_use'. This field is ignored when the auto-optimization is done, and in that case the
            parameter of the best filters found during the optimization routine are used. For manual specification of
            the parameters of the filter available in this plugin, see https://github.com/juglab/n2v. It has to
            be specified as below

                                        [[name_parameter_1, value_parameter_1],

                                        [name_parameter_2, value_parameter_2],

                                        ...],

            'trained_n2v_setting': Setting relative to the loading/saving of trained n2v models. It has to be
            specified as below:

                {'use_trained_n2v_model': (bool) if True, a trained n2v model is loaded from the path contained in the
                field 'path_to_trained_n2v_model'.

                'path_to_trained_n2v_model': (raw str) path to a trained n2v model. This field is ignored if the
                previous field is False.

                'save_trained_n2v_model': (bool) if True after training, the best n2v model is saved a the path
                contained in the field 'saving_path'.

                'saving_path': (raw str) path where the best n2v model is saved. This field is ignored if the previous
                field is False.

                }

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        :param force_serial: (bool) if True serial behavior is forced for this plugin independently on the global
                             setting of bmiptools.
        """
        super(DenoiserDNN,self).__init__()
        self.force_serial = force_serial
        self._available_denoiser = {'n2v_2d': None,
                                    'n2v_3d': None}

        self.auto_optimize = transformation_dictionary['auto_optimize']
        if self.auto_optimize:

            self.tested_filters_list = transformation_dictionary['optimization_setting']['tested_filters_list']
            if 'n2v_2d' in self.tested_filters_list:

                self.unet_kern_size_2d_list = \
                    transformation_dictionary['optimization_setting']['n2v_2d']['unet_kern_size_2d_list']
                self.train_batch_size_2d_list = \
                    transformation_dictionary['optimization_setting']['n2v_2d']['train_batch_size_2d_list']
                self.n2v_patch_shape_2d_list = \
                    transformation_dictionary['optimization_setting']['n2v_2d']['n2v_patch_shape_2d_list']
                self.train_epochs_2d_list = \
                    transformation_dictionary['optimization_setting']['n2v_2d']['train_epochs_2d_list']
                self.train_loss_2d_list = transformation_dictionary['optimization_setting']['n2v_2d']['train_loss_2d_list']
                self.n2v_manipulator_2d_list = \
                    transformation_dictionary['optimization_setting']['n2v_2d']['n2v_manipulator_2d_list']
                self.n2v_neighborhood_radius_2d_list = \
                    transformation_dictionary['optimization_setting']['n2v_2d']['n2v_neighborhood_radius_2d_list']

            if 'n2v_3d' in self.tested_filters_list:

                self.unet_kern_size_3d_list = \
                    transformation_dictionary['optimization_setting']['n2v_3d']['unet_kern_size_3d_list']
                self.train_batch_size_3d_list = \
                    transformation_dictionary['optimization_setting']['n2v_3d']['train_batch_size_3d_list']
                self.n2v_patch_shape_3d_list = \
                    transformation_dictionary['optimization_setting']['n2v_3d']['n2v_patch_shape_3d_list']
                self.train_epochs_3d_list = \
                    transformation_dictionary['optimization_setting']['n2v_3d']['train_epochs_3d_list']
                self.train_loss_3d_list = transformation_dictionary['optimization_setting']['n2v_3d']['train_loss_3d_list']
                self.n2v_manipulator_3d_list = \
                    transformation_dictionary['optimization_setting']['n2v_3d']['n2v_manipulator_3d_list']
                self.n2v_neighborhood_radius_3d_list = \
                    transformation_dictionary['optimization_setting']['n2v_3d']['n2v_neighborhood_radius_3d_list']

        self.use_bounding_box = \
            transformation_dictionary['optimization_setting']['opt_bounding_box']['use_bounding_box']
        if self.use_bounding_box:

            self.y_limits_bbox = \
                transformation_dictionary['optimization_setting']['opt_bounding_box']['y_limits_bbox']
            self.x_limits_bbox = \
                transformation_dictionary['optimization_setting']['opt_bounding_box']['x_limits_bbox']

        self.fit_step = transformation_dictionary['optimization_setting']['fit_step']
        self.filter_to_use = transformation_dictionary['filter_to_use']
        self.filter_params = transformation_dictionary['filter_params']
        self.use_trained_n2v_model = transformation_dictionary['trained_n2v_setting']['use_trained_n2v_model']
        self.path_to_trained_n2v_model = transformation_dictionary['trained_n2v_setting']['path_to_trained_n2v_model']
        self.save_trained_n2v_model = transformation_dictionary['trained_n2v_setting']['save_trained_n2v_model']
        self.saving_path = transformation_dictionary['trained_n2v_setting']['saving_path']

        self._setup()

    def _setup(self):

        if self.auto_optimize:

            # check tested_denoiser_list
            assert len(self.tested_filters_list)>0, 'There must be at least one filter in \'tested_filter_list\''

            for filt in self.tested_filters_list:

                if not filt in self._available_denoiser.keys():

                    raise ValueError('Filter {} not recognized. Use a filter name '
                                     'present in the list below {}'.format(filt,list(self._available_denoiser.keys())))

            # generate wavelet parameter space
            self._Jopt_parameter_dict = {}
            if 'n2v_2d' in self.tested_filters_list:

                self._n2v_model_name = 'n2v_2d_denoiser__' + datetime.now().strftime("%d%m%Y_%H%M%S")
                self._n2v_basedir = ut.manage_path(bmiptools.__temporary_files_folder_path__ + os.sep + 'n2v_models')
                checked_unet_kern_size_2d_list = list(set([2*(a//2)+1 for a in self.unet_kern_size_2d_list if a in [3,5,7]]))
                if len(checked_unet_kern_size_2d_list) == 0:

                    raise ValueError('Invalid setting for n2v_2d optimization. The CSBDeep library used by n2v currently '
                                     'support only \'unet_kern_size\' equal to 3,5 or 7 for inference. Change your '
                                     'setting accordingly.')

                cheched_n2v_patch_shape_2 = [e for e in self.n2v_patch_shape_2d_list if type(e)==int or \
                                           ((type(e) == list or type(e) == tuple) and len(e)==2)]
                self._Jopt_parameter_dict.update({'n2v_2d': {'unet_kern_size': checked_unet_kern_size_2d_list,
                                                             'train_batch_size': self.train_batch_size_2d_list,
                                                             'n2v_patch_shape': cheched_n2v_patch_shape_2,
                                                             'train_epochs': self.train_epochs_2d_list,
                                                             'train_loss': self.train_loss_2d_list,
                                                             'n2v_manipulator': self.n2v_manipulator_2d_list,
                                                             'n2v_neighborhood_radius': \
                                                                 self.n2v_neighborhood_radius_2d_list}})

                self._n2v_conf_default_dict = self.n2v_default_setting_dictionary

            if 'n2v_3d' in self.tested_filters_list:

                self._n2v_model_name = 'n2v_3d_denoiser__'+datetime.now().strftime("%d%m%Y_%H%M%S")
                self._n2v_basedir = ut.manage_path(bmiptools.__temporary_files_folder_path__ + os.sep + 'n2v_models')
                checked_unet_kern_size_3d_list = list(set([2*(a//2)+1 for a in self.unet_kern_size_3d_list if a in [3,5,7]]))
                if len(checked_unet_kern_size_3d_list) == 0:

                    raise ValueError('Invalid setting for n2v_3d optimization. The CSBDeep library used by n2v currently '
                                     'support only \'unet_kern_size\' equal to 3,5 or 7 for inference. Change your '
                                     'setting accordingly.')

                cheched_n2v_patch_shape_3d = [e for e in self.n2v_patch_shape_3d_list if type(e)==int or \
                                           ((type(e) == list or type(e) == tuple) and len(e)==3)]
                self._Jopt_parameter_dict.update({'n2v_3d': {'unet_kern_size': checked_unet_kern_size_3d_list,
                                                             'train_batch_size': self.train_batch_size_3d_list,
                                                             'n2v_patch_shape': cheched_n2v_patch_shape_3d,
                                                             'train_epochs': self.train_epochs_3d_list,
                                                             'train_loss': self.train_loss_3d_list,
                                                             'n2v_manipulator': self.n2v_manipulator_3d_list,
                                                             'n2v_neighborhood_radius': \
                                                                 self.n2v_neighborhood_radius_3d_list}})

                self._n2v_conf_default_dict = self.n2v_default_setting_dictionary
                self._n2v_conf_default_dict['n2v_patch_shape'] = self._n2v_conf_default_dict['n2v_patch_shape'] + \
                                                                (self._n2v_conf_default_dict['n2v_patch_shape'][0],)

        else:

            if not self.filter_to_use in list(self._available_denoiser):

                raise ValueError('Filter \'{}\' in \'filter_to_use\' field of the transformation dictionary is not '
                                 'recognized. Available filters for this plugin are listed below '
                                 '\n{}'.format(self.filter_to_use,list(self._available_denoiser)))

            if self.filter_params != None:

                self.filter_params = {item[0]: item[1] for item in self.filter_params}

            if self.filter_to_use == 'n2v_2d':

                self._n2v_Ndims = 2
                self._n2v_axes = 'YX'
                if self.use_trained_n2v_model:

                    self._fitted_n2v = True
                    model_name = os.path.basename(os.path.normpath(self.path_to_trained_n2v_model))
                    basedir = os.path.dirname(os.path.normpath(self.path_to_trained_n2v_model))
                    self.APP = [model_name,basedir]
                    self.n2v_model = N2V(config=None,name=model_name,basedir=basedir)

                else:

                    self._fitted_n2v = False
                    self._n2v_basedir = ut.manage_path(bmiptools.__temporary_files_folder_path__+os.sep+'n2v_models')
                    self._n2v_model_name = 'n2v_2d_denoiser__'+datetime.now().strftime("%d%m%Y_%H%M%S")
                    if self.filter_params == None:

                        self.filter_params = self.n2v_default_setting_dictionary

            else:

                self._n2v_Ndims = 3
                self._n2v_axes = 'ZYX'
                if self.use_trained_n2v_model:

                    self._fitted_n2v = True
                    model_name = os.path.basename(os.path.normpath(self.path_to_trained_n2v_model))
                    basedir = os.path.dirname(os.path.normpath(self.path_to_trained_n2v_model))
                    self.n2v_model = N2V(config=None,name=model_name,basedir=basedir)

                else:

                    self._fitted_n2v = False
                    self._n2v_basedir = ut.manage_path(bmiptools.__temporary_files_folder_path__+os.sep+'n2v_models')
                    self._n2v_model_name = 'n2v_3d_denoiser__'+datetime.now().strftime("%d%m%Y_%H%M%S")
                    if self.filter_params == None:

                        self.filter_params = self.n2v_default_setting_dictionary
                        self.filter_params['n2v_patch_shape'] = (64,64,64)

    def _clean_temporary_folder(self,temporary_file_folder_path, path_folder_to_keep):
        """
        Clear the temporary folder keeping only the best model.

        :param temporary_file_folder_path: (raw str) path to the temporary file folder.
        :param path_folder_to_keep: (raw str) path to the folder to keep during the deleting process.
        """
        objects_found = glob.glob(temporary_file_folder_path + os.sep + '**', recursive=True)
        file_to_delete = []
        directory_to_delete = []
        for obj_path in objects_found:

            if not path_folder_to_keep is None and \
                    (os.path.normpath(path_folder_to_keep) in os.path.normpath(obj_path) or \
                    os.path.normpath(obj_path) == os.path.normpath(temporary_file_folder_path)):

                pass

            else:

                if os.path.isdir(obj_path):

                    directory_to_delete.append(obj_path)

                else:

                    file_to_delete.append(obj_path)

        for file_path in file_to_delete:

            try:

                os.unlink(file_path)

            except Exception as e:

                warnings.warn('Failed to delete file {}. Reason: {}'.format(file_path, e))

        dept = [len(path.split(os.sep)) for path in directory_to_delete]
        # dept_ordered_directory_to_delete = \
        #     [list(tpl) for tpl in zip(*sorted(zip(dept, directory_to_delete), reverse=True))][1]
        # for dir_path in dept_ordered_directory_to_delete:
        #
        #     try:
        #
        #         shutil.rmtree(dir_path)
        #
        #     except Exception as e:
        #
        #         warnings.warn('Failed to delete folder {}. Reason: {}'.format(dir_path, e))

        dept_ordered_directory_to_delete = \
            [list(tpl) for tpl in zip(*sorted(zip(dept, directory_to_delete), reverse=True))]
        if len(dept_ordered_directory_to_delete) > 1:

            dept_ordered_directory_to_delete = dept_ordered_directory_to_delete[1]
            for dir_path in dept_ordered_directory_to_delete:

                try:

                    shutil.rmtree(dir_path)

                except Exception as e:

                    warnings.warn('Failed to delete folder {}. Reason: {}'.format(dir_path, e))

    def _Jinvariance_n2v_optimization(self,x,parameter_space,vol_for_Jinv_fit):
        """
        J-invariant optimization routine for the n2v models.

        :param x: (ndarray) data used for the model optimization;
        :param parameter_space: (dict) dictionary containing the parameter space;
        :param vol_for_Jinv_fit: (ndarray) data used for J-invariant loss evaluation.
        """
        datagen = N2V_DataGenerator()
        params_space,params_name = generate_parameter_space(parameter_space)
        self.write('Number of parameter combination tested: {}'.format(len(params_space)))
        n2v_conf_dict = copy.copy(self.n2v_default_setting_dictionary)

        if self._n2v_Ndims == 2:

            slices_train = img_as_float(np.expand_dims(x[1::self.fit_step],axis=-1))
            slices_test = img_as_float(np.expand_dims(x[::4*self.fit_step],axis=-1))

        else:

            slices_train = img_as_float(np.expand_dims(x,axis=(0,-1)))
            slices_test = slices_train

        n2v_models = []
        n2v_training_params = []
        n2v_models_path = []
        loss = []
        for n,param_comb in self.vtqdm(enumerate(params_space)):

            for param_name in params_name:

                n2v_conf_dict[param_name] = param_comb[params_name.index(param_name)]

            if type(n2v_conf_dict['n2v_patch_shape']) is int:

                patch_shape = self._n2v_Ndims*(n2v_conf_dict['n2v_patch_shape'],)

            else:

                patch_shape = n2v_conf_dict['n2v_patch_shape']

            n2v_conf_dict['n2v_patch_shape'] = patch_shape
            patches = datagen.generate_patches(slices_train,shape=patch_shape)
            patches_val = datagen.generate_patches(slices_test,shape=patch_shape)



            config = N2VConfig(slices_train,**n2v_conf_dict)
            model_name = self._n2v_model_name+'_{}d_param_comb_{}'.format(self._n2v_Ndims,n)
            model = N2V(config,model_name,basedir=self._n2v_basedir)
            model.train(patches,patches_val)

            # free RAM from train and test dataset
            patches = patches_val = None

            trained_n2v_denoiser = lambda z: model.predict(z,axes=self._n2v_axes)
            if self._n2v_Ndims == 2:

                total_loss_per_param = 0
                for i in self.vtqdm(range(len(vol_for_Jinv_fit))):          # Multichannel!!!!!!!!!!!!!!!

                    slice = vol_for_Jinv_fit[i,...]
                    _,(_,loss_per_param_per_slice) = calibrate_denoiser(slice,trained_n2v_denoiser,
                                                                        denoise_parameters={},extra_output=True)
                    total_loss_per_param = total_loss_per_param+loss_per_param_per_slice[0]

                loss.append(total_loss_per_param/len(vol_for_Jinv_fit))

            else:

                _,(_,loss_per_param) = calibrate_denoiser(slices_test[0,...,0],trained_n2v_denoiser,
                                                            denoise_parameters={},extra_output=True)
                loss.append(loss_per_param[0]/slices_test.shape[1])

            n2v_models.append(model)
            n2v_models_path.append(self._n2v_basedir+os.sep+model_name)
            n2v_training_params.append(n2v_conf_dict)

        idx_best = np.argmin(loss)
        return n2v_models[idx_best],n2v_models_path[idx_best],n2v_training_params[idx_best],loss[idx_best]

    def fit(self,x):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        if self.use_bounding_box:

            ymin,ymax = self.y_limits_bbox
            xmin,xmax = self.x_limits_bbox

        else:

            ymin = xmin = ymax = xmax = None

        self.write('Denoiser optimization routine')
        self.write('----------------------------')
        self.write('Optimization method: grid search.')
        self.opt_params_per_filter = {}
        score_list = []
        for n,filter_name in enumerate(self.tested_filters_list):

            self.progress_bar(n,len(self.tested_filters_list),15,text_after='Current filter tested: {}'.format(filter_name))
            if filter_name == 'n2v_2d':

                vol_for_optimization = x[:,ymin:ymax,xmin:xmax,...] #<-----
                if x.n_channels > 1:  # Temporary solution for multichannel images: only the first channel is considered

                    vol_for_optimization = vol_for_optimization[...,0]

                current_params_space = self._Jopt_parameter_dict[filter_name]
                self._n2v_Ndims = 2
                self._n2v_axes = 'YX'
                opt_trained_n2v_2d_model,opt_trained_n2v_2d_path,opt_params,score = \
                    self._Jinvariance_n2v_optimization(vol_for_optimization,current_params_space,
                                                       vol_for_optimization[...]) #<-----

            else:

                vol_for_optimization = x[:,ymin:ymax,xmin:xmax, ...]
                if x.n_channels > 1:  # Temporary solution for multichannel images: only the first channel is considered

                    vol_for_optimization = vol_for_optimization[..., 0]

                current_params_space = self._Jopt_parameter_dict[filter_name]
                self._n2v_Ndims = 3
                self._n2v_axes = 'ZYX'
                opt_trained_n2v_3d_model,opt_trained_n2v_3d_path,opt_params,score = \
                    self._Jinvariance_n2v_optimization(vol_for_optimization,current_params_space,
                                                       vol_for_optimization[:,ymin:ymax,xmin:xmax])

            self.opt_params_per_filter.update({filter_name: {'score': score, 'params': opt_params}})
            score_list.append(score)

        best_filter_idx = np.argmin(score_list)
        self.filter_to_use = list(self.opt_params_per_filter)[best_filter_idx]
        self.filter_params = self.opt_params_per_filter[self.filter_to_use]['params']
        if self.filter_to_use == 'n2v_2d':

            self._fitted_n2v = True
            self._n2v_Ndims = 2
            self._n2v_axes = 'YX'
            self.n2v_model = opt_trained_n2v_2d_model
            self.path_to_trained_n2v_model = opt_trained_n2v_2d_path

        else:

            self._fitted_n2v = True
            self._n2v_Ndims = 3
            self._n2v_axes = 'ZYX'
            self.n2v_model = opt_trained_n2v_3d_model
            self.path_to_trained_n2v_model = opt_trained_n2v_3d_path

        self._clean_temporary_folder(self._n2v_basedir,self.path_to_trained_n2v_model)
        self.write('Optimization terminated!')
        self.write('Best filter: {} \n'
                   'Best filter parameters: {}'.format(self.filter_to_use,self.filter_params))
        self.write('----------------------------')

    def _fit_n2v_2d_model(self,x,filter_param):
        """
        Fit the neural network used by a 2d n2v denoiser.

        :param x: (ndarray) data on which the model is fitted.
        :param filter_param: (dict) dictionary model parameters for the initialization of n2v models.
        """
        fit_step = int(len(x)*0.1)
        if fit_step == 0:

            fit_step = 1

        patch_shape = filter_param['n2v_patch_shape']
        slices_train = np.expand_dims(x[1::fit_step],axis=-1)
        slices_test = np.expand_dims(x[::4*fit_step],axis=-1)
        datagen = N2V_DataGenerator()
        patches = datagen.generate_patches(slices_train,shape=patch_shape)
        patches_val = datagen.generate_patches(slices_test,shape=patch_shape)
        config = N2VConfig(slices_train,**filter_param)
        self.n2v_model = N2V(config,self._n2v_model_name,basedir=self._n2v_basedir)
        self.n2v_model.train(patches,patches_val)
        self.path_to_trained_n2v_model = self._n2v_basedir+os.sep+self._n2v_model_name

    def _filter_n2v_2d_stack(self,x):
        """
        Filter the images using a 2d n2v denoiser.

        :param x: (ndarray) images to filter.
        """
        if not self._fitted_n2v:

            self.n2v_model = self._fit_n2v_2d_model(x,self.filter_params)
            self._fitted_n2v = True

        transformed_vol = []
        for slice in x:

            transformed_vol.append(self.n2v_model.predict(img_as_float(slice),axes=self._n2v_axes))

        return np.array(transformed_vol)

    def _fit_n2v_3d_model(self,x,filter_param):
        """
        Fit the neural network used by a 3d n2v denoiser.

        :param x: (ndarray) data on which the model is fitted.
        :param filter_param: (dict) dictionary model parameters for the initialization of n2v models.
        """
        test_fraction = (x.shape[0]//self.fit_step)/x.shape[0]
        z_split = np.maximum(1,int(x.shape[0]*(1-test_fraction)))
        vol_train = img_as_float(np.expand_dims(x[:z_split,...],axis=(0,-1)))
        vol_test = img_as_float(np.expand_dims(x[z_split:,...],axis=(0,-1)))

        patch_shape = filter_param['n2v_patch_shape']
        datagen = N2V_DataGenerator()
        patches = datagen.generate_patches(vol_train,shape=patch_shape)
        patches_val = datagen.generate_patches(vol_test,shape=patch_shape)
        config = N2VConfig(vol_train,**filter_param)
        self.n2v_model = N2V(config,self._n2v_model_name,basedir=self._n2v_basedir)
        self.n2v_model.train(patches,patches_val)
        self.path_to_trained_n2v_model = self._n2v_basedir+os.sep+self._n2v_model_name

    def _filter_n2v_3d_stack(self,x):
        """
        Filter the images using a 3d n2v denoiser.

        :param x: (ndarray) images to filter.
        """
        if not self._fitted_n2v:

            self.n2v_model = self._fit_n2v_3d_model(x,self.filter_params)
            self._fitted_n2v = True

        transformed_vol = self.n2v_model.predict(img_as_float(x.data),axes=self._n2v_axes)
        return np.array(transformed_vol)

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if self.fit_enable and self.auto_optimize:

            self.fit(x)

        if self.save_trained_n2v_model:

            self.save()

        if self.filter_to_use == 'n2v_2d':

            if not inplace:

                return self._filter_n2v_2d_stack(x)

            x.from_array(self._filter_n2v_2d_stack(x))

        else:

            if not inplace:

                return self._filter_n2v_3d_stack(x)

            x.from_array(self._filter_n2v_3d_stack(x))

    def save(self,path = None):
        """
        Save the trained n2v model. In addition to save n2v model in the given folder, it also change the setting
        of the plugin, so that the transformation_dictionary if the plugin is reinitialized with the same
        transformation_dictionary, it will automatically load the model found at the saving path.

        :param path: (raw str) (optional) saving path.
        """
        if path is None:

            path = self.saving_path

        ut.copy_folder_and_its_content(self.path_to_trained_n2v_model,path)

        # ut.delete_folder_and_its_content(self.path_to_trained_n2v_model)  # The model remains also in the temporary
                                                                            # folder.
        self.auto_optimize = False
        self.fit_enable = False
        self.save_trained_n2v_model = False
        self.use_trained_n2v_model = True
        self.path_to_trained_n2v_model = path+os.sep+self.n2v_model.name