# Title: 'destriper.py'
# Date: 04/03/2021
# Author: Curcuraci L.
#
# Scope: Algorithm for the removal of stripe artifacts.
#
# Updates:
#
# - 20/05/21: * the plugin can deal with multichannel images (each channel is treated independently);
#             * the plugin can be optimized and apply the transformation in serial and parallel way.
# - 10/12/21: * implemented optimization routine for the filter hyper-parameter search.
#
# Source:
#
#     [1] "Stripe and ring artifact removal with combined wavelet—Fourier filtering" - Beat Münch, Pavel Trtik,
#         Federica Marone, and Marco Stampanoni - https://doi.org/10.1364/OE.17.008567
#
# Further developments:
#
#     [1] Robust destriping method with unidirectional total variation and framelet regularization - Yi Chang,
#         Houzhang Fang, Luxin Yan, and Hai Liu - https://doi.org/10.1364/OE.21.023307
#
#     [2] Removal of curtaining effects by a variational model with directional forward differences
#         - Jan Henrik Fitschen Jianwei Ma Sebastian Schuff  - https://doi.org/10.1016/j.cviu.2016.12.008

"""
Plugin for the removal of the stripe artifacts, typical of FIB-SEM images.
"""


#################
#####   LIBRARIES
#################


import numpy as np
from scipy import fftpack
import pywt
from joblib import Parallel,delayed
from skimage.exposure import match_histograms

from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI
from bmiptools.transformation.restoration._restoration_shared import SUPPORTED_WAVELET,SUPPORTED_WAVELET_FAMILIES


###############
#####   CLASSES
###############


class Destriper(TransformationBasic):
    """
    Class used to remove vertical line artifacts in a stack.
    """

    __version__ = '0.2'
    empty_transformation_dictionary = {
                                       'auto_optimize': True,
                                       'optimization_setting':{'wavelet':{'use_wavelet': 'all',
                                                                          'wavelet_family': 'db'
                                                                          },
                                                               'sigma':{'sigma_min':0.01,
                                                                        'sigma_max': 50,
                                                                        'sigma_step':1
                                                                        },
                                                               'decomposition_level':{'set_decomposition_level_to_max_compatible': True,
                                                                                      'decomposition_level_min': 2,
                                                                                      'decomposition_level_max': 9,
                                                                                      'increase_decomposition_level_during_inference': False
                                                                                      },
                                                               'opt_bounding_box':{'use_bounding_box': True,
                                                                                   'y_limits_bbox': [-500,None],
                                                                                   'x_limits_bbox': [500,1500]
                                                                                   },
                                                               'fit_step':10
                                                               },
                                      'wavelet_name':'db1',
                                      'decomposition_level':4,
                                      'sigma': 4,
                                      'match_in_out_contrast': True
                                       }
    _guipi_dictionary = {'auto_optimize': GuiPI(bool),
                         'optimization_setting': {'wavelet': {'use_wavelet':
                                                                  GuiPI(options=['all','family']+SUPPORTED_WAVELET),
                                                              'wavelet_family':
                                                                  GuiPI(options=SUPPORTED_WAVELET_FAMILIES)},
                                                  'sigma': {'sigma_min': GuiPI(float),
                                                            'sigma_max': GuiPI(float),
                                                            'sigma_step': GuiPI(float)},
                                                  'decomposition_level': {'set_decomposition_level_to_max_compatible':
                                                                              GuiPI(bool),
                                                                          'decomposition_level_min': GuiPI(int),
                                                                          'decomposition_level_max': GuiPI(int),
                                                                          'increase_decomposition_level_during_inference':
                                                                              GuiPI(bool)},
                                                  'opt_bounding_box': {'use_bounding_box': GuiPI(bool),
                                                                       'y_limits_bbox': GuiPI('math'),
                                                                       'x_limits_bbox': GuiPI('math')},
                                                  'fit_step': GuiPI(int)},
                         'wavelet_name': GuiPI(options=SUPPORTED_WAVELET),
                         'decomposition_level': GuiPI(list),
                         'sigma': GuiPI(float),
                         'match_in_out_contrast': GuiPI(bool)}
    def __init__(self,transformation_dictionary,force_serial=False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'auto_optimize': (bool) if True an optimization routine based on a reasonable self-supervised loss for
            destriping is executed before the application of the transformation to the stack. The parameter space on
            which the search of the best parameter takes place, is created according to what is specified in the
            'optimization_setting' field below.

            'optimization_setting': (dict) Dictionary used to define the parameter space of the filter. It has to be
            specified as follow:

                 {'wavelet': (dict) Dictionary containing all the setting about the research of the wavelet type. It
                 has to be specified as follow:

                    {'use_wavelet': (str) it specify the kind of wavelet(s) used during the parameter search. It can
                    take the following values:

                        * 'all', to check all the discrete wavelets available in the 'pywt' library during the
                          optimization;

                        * 'family', to check just a single wavelet family during the optimization. When this option is
                          used the wavelet family have to be specified in the field 'wavelet_family' below;

                        * a name of a discrete wavelet of the 'pywt' library which is kept fixed during the
                          optimization.

                    'wavelet_family': (str) a name of a discrete wavelet family of the 'pywt' library to search only
                    among the wavelets of this family during the optimization. This field is ignored if 'use_wavelet'
                    is not set equal to 'family'.

                    }

                 'sigma': (dict) Dictionary containing all the setting about the research of the standard deviation of
                 the gaussian filter used at each level of the vertical component of the wavelet decomposition of the
                 image. It has to be specified as follow:

                    {'sigma_min': (float) minimum value of standard deviation of the gaussian filter used during the
                    parameter search.

                    'sigma_max': (float) maximal value of standard deviation of the gaussian filter used during the
                    parameter search.

                    'sigma_step': (float) step value used to define the possible values of standard deviation of the
                    gaussian filter used during the parameter search.

                    }

                 'decomposition_level': (dict) Dictionary containing all the setting about the research of the
                 decomposition level used in the wavelet decomposition of the image. It has to be specified as follow:

                    {'set_decomposition_level_to_max_compatible': (bool) if True only the maximal possible level of
                    the wavelet decomposition, which does not introduce boundary artifacts in the reconstruction, is
                    used during the parameter search.

                    'decomposition_level_min': (float or str) minimum decomposition level of the 2D wavelet transform
                    used during the parameter search. If set equal to 'max' the maximal possible level of the
                    wavelet decomposition, which does not introduce boundary artifacts in the reconstruction, is used.

                    'decomposition_level_max': (float or str) maximal decomposition level of the 2D wavelet transform
                    used during the parameter search. If set equal to 'max' the maximal possible level of the
                    wavelet decomposition, which does not introduce boundary artifacts in the reconstruction, is used.

                    'increase_decomposition_level_during_inference': (bool) if True the decomposition level during
                    the inference is increased by one. This typically further reduces the stripe artifacts in case the
                    optimization does not find the visually best combination of parameters.

                    }

                 opt_bounding_box': (dict) Dictionary containing the setting for the definition of the part of the
                 image(s) which is used in the optimization routine. It has to be specified as follow:

                    {'use_bounding_box': (bool) if True only a part of the image (i.e. yx-slice of the stack) is used
                    for the optimization, otherwise the whole image is used. If True the two arguments below are also
                    read, otherwise they are ignored.

                    'y_limits_bbox': (list) bounds in the y axis. The list have to contain the two extrema of the
                    region of interest along the y-axis. The notation is compatible with the standard numpy slicing
                    notation regarding negative or None indexing e.g

                        1. y_bounds_bbox = [200,300] -> image[200:300,...]

                        2. y_bounds_bbox = [-200,None] -> image[-200:None,...] = image[-200:,...]


                    'x_limits_bbox': (list) bounds in the x axis. The list have to contain the two extrema of the
                    region of interest along the x-axis. The notation is compatible with the standard numpy slicing
                    notation regarding negative or None indexing e.g

                        1. x_bounds_bbox = [200,300] -> image[...,200:300]

                        2. x_bounds_bbox = [-200,None] -> image[...,-200:None] = image[...,-200:]

                    }

                 'fit_step': (int) interval between two slices of the stack that are used during the optimization. If 1
                 all the stack is used, for n>1 only the slices having a distance of n on the 0-axis (i.e. the
                 z-direction). This parameter therefore determine the number of slices used during the optimization,
                 which is equal to (image_size_z)//n.

                 }

            'wavelet_decomposition': (dict) Dictionary containing the setting for the wavelet decomposition. The
            dictionary has to be specified as below:

                {'wavelet_name': (str) wavelet name. To se the available wavelets (and its name check the
                'supported_wavelet' attribute of this class).

                'decomposition_level': (int or str) If an integer number is given, this number is the maximal
                decomposition level used in the wavelet transform. If 'max' is given the highest level which can be
                used in the wavelet decomposition without introduce border artifacts is used.

                }

            'fourier_space_filter': (dict) Dictionary containing the setting for the pre-registration transformations.
            The dictionary has to be specified as below:

                {'sigma': (float) Standard deviation of the gaussian filter used in the fourier space to remove
                vertical artifacts.

                }

            'match_in_out_contrast': (bool) if True, the contrast of each slice of the stack after the wavelet-fourier
            filter is matched with the contrast of the corresponding input slice.

            }


        :param transformation_dictionary: dictionary containing all the transformation options.
        :param force_serial: (bool) if True serial behavior is forced for this plugin independently on the global
                             setting of bmiptools.
        """
        super(Destriper,self).__init__()
        self.force_serial = force_serial

        self.supported_wavelets = SUPPORTED_WAVELET
        self.discrete_wavelet_families_list = SUPPORTED_WAVELET_FAMILIES

        self.auto_optimize = transformation_dictionary['auto_optimize']
        self.match_in_out_contrast = transformation_dictionary['match_in_out_contrast']
        if self.auto_optimize:

            self.use_wavelet = transformation_dictionary['optimization_setting']['wavelet']['use_wavelet']
            if self.use_wavelet == 'family':

                    self.wavelet_family = transformation_dictionary['optimization_setting']['wavelet']['wavelet_family']

            self.sigma_min = transformation_dictionary['optimization_setting']['sigma']['sigma_min']
            self.sigma_max = transformation_dictionary['optimization_setting']['sigma']['sigma_max']
            self.sigma_step = transformation_dictionary['optimization_setting']['sigma']['sigma_step']

            self.set_decomposition_level_to_max_compatible = \
                transformation_dictionary['optimization_setting']['decomposition_level']['set_decomposition_level_to_max_compatible']
            if not self.set_decomposition_level_to_max_compatible:

                self.decomposition_level_min = \
                    transformation_dictionary['optimization_setting']['decomposition_level']['decomposition_level_min']
                self.decomposition_level_max = \
                    transformation_dictionary['optimization_setting']['decomposition_level']['decomposition_level_max']

            self.increase_decomposition_level_during_inference = \
                transformation_dictionary['optimization_setting']['decomposition_level']['increase_decomposition_level_during_inference']

            self.use_bounding_box = transformation_dictionary['optimization_setting']['opt_bounding_box']['use_bounding_box']
            if self.use_bounding_box:

                self.y_limits_bbox = transformation_dictionary['optimization_setting']['opt_bounding_box']['y_limits_bbox']
                self.x_limits_bbox = transformation_dictionary['optimization_setting']['opt_bounding_box']['x_limits_bbox']

            self.fit_step = transformation_dictionary['optimization_setting']['fit_step']

        else:

            self.wavelet_name = transformation_dictionary['wavelet_name']
            self.decomposition_level = transformation_dictionary['decomposition_level']
            self.sigma = transformation_dictionary['sigma']

        self._setup()

    def _setup(self):

        if self.auto_optimize:

            if self.use_wavelet in SUPPORTED_WAVELET:

                self.wavelets_for_optimization = [self.use_wavelet]

            elif self.use_wavelet=='family' and self.wavelet_family in SUPPORTED_WAVELET_FAMILIES:

                self.wavelets_for_optimization = pywt.wavelist(family=self.wavelet_family)

            elif self.use_wavelet == 'all':

                self.wavelets_for_optimization = SUPPORTED_WAVELET

            else:

                raise ValueError('Unrecognized {} wavelet or wavelet family for the optimization. Use \'all\' '
                                 'to use all the wavelets during the optimization, or specify a supported wavelet name '
                                 'to use just the selected wavelet for the optimization, or a supported wavelet family '
                                 'name to use all the wavelet of this family. Supported wavelet names can be found in '
                                 'the list below\n{}\n Supported wavelet family names can be found in the list below '
                                 '\n{}'.format(self.use_wavelet,self.supported_wavelets,
                                               self.discrete_wavelet_families_list))

            if not self.set_decomposition_level_to_max_compatible:

                if self.decomposition_level_min != 'max':

                    self.decomposition_level_min = np.maximum(0,self.decomposition_level_min)

                if self.decomposition_level_max != 'max' and self.decomposition_level_min != 'max':

                    self.decomposition_level_max = np.maximum(self.decomposition_level_min,self.decomposition_level_max)

        else:

            if self.wavelet_name not in pywt.wavelist():

                raise ValueError('Wavelet name \'{}\' not recognized. Use a wavelet name belonging to the following '
                                 'list:\n{}'.format(self.wavelet_name,self.supported_wavelets))

            if self.decomposition_level == 'max':

                self.decomposition_level = None

    @staticmethod
    def _self_supervised_decurtaining_loss(x,filter_funct,params):
        """
        Self-supervised loss used for the parameter search. The loss function used try to match the gradient along the
        vertical direction of the destriped image with the same gradient of the original image. At the same time it
        also try to match the gradient along the horizontal direction of the stripes with the same gradient of the input
        slice, favouring also sparsity along the vertical direction. Mathematically, this means that we try to
        composed the input image I as

                                                I = O + S

        where O is the output image, i.e. O = f(I) where f is our filter, and S is the stripe image, which can be
        defined simply as S = I-f(I). Defining Dy and Dx as the gradient operator along the y- and x-axis, the loss
        function used can be defined as

                                                L = R+P+Q
        with

                                            R = E[ |Dy S| ]
                                            P = E[ |Dx S - Dx I| ]
                                            Q = E[ |Dy O - Dy I| ]

        where E[...] means the expectation value over all the pixels.

        :param x: (ndarray) input slice;
        :param filter_funct: (func) filter function;
        :param params: (dict) dictionary having as key the name of the parameters of the filter used in 'filter_funct'
                       and as value the corresponding parameters values.
        :return: (float) loss value for the given parameters.
        """
        # shape must be even for dwt reconstruction (see https://github.com/PyWavelets/pywt/issues/80)
        if x.shape[0]%2 != 0:

            x = x[:-1,:]

        if x.shape[1]%2 != 0:

            x = x[:,:-1]

        destriped = filter_funct(x,**params)
        stripes = x-destriped
        R = np.mean(np.abs(np.gradient(stripes,axis=0)))
        Q = np.mean(np.abs(np.gradient(stripes,axis=1)-np.gradient(x,axis=1)))
        #P = np.mean(np.abs(np.gradient(destriped,axis=0)-np.gradient(x,axis=0)))
        return 2*R+Q#+P

    def _generate_parameter_space(self,slice_shape):
        """
        Generate the parameter space for the optimization routine (Grid Search).

        :param slice_shape: (tuple) shape of a slice of the stack.
        :return: list of all the parameter combination used during the Grid Search.
        """
        parameter_space = []
        for wname in self.wavelets_for_optimization:

            for sigma in np.arange(self.sigma_min, self.sigma_max, self.sigma_step):

                if self.set_decomposition_level_to_max_compatible:

                    parameter_space.append([wname,sigma,pywt.dwtn_max_level(slice_shape,wname)])

                else:

                    if self.decomposition_level_min == 'max':

                        self.decomposition_level_min = pywt.dwtn_max_level(slice_shape,wname)
                        if self.decomposition_level_max != 'max':

                            self.decomposition_level_max = np.maximum(self.decomposition_level_min,
                                                                      self.decomposition_level_max)

                        else :

                            self.decomposition_level_max = np.maximum(self.decomposition_level_min,
                                                                      pywt.dwtn_max_level(slice_shape,wname))

                    for level in range(self.decomposition_level_min,self.decomposition_level_max,1):

                        parameter_space.append([wname, sigma, level])

        return parameter_space

    def _fit_serial(self,x):
        """
        Serial version of the fitting routine.

        :param x: (ndarray) portion of the stack to be used for the optimization
        :return: (list) the parameter space, (list) the corresponding loss value.
        """
        # Create the parameter space for the grid search
        slice_shape = (x.shape[1], x.shape[2])
        parameter_space = self._generate_parameter_space(slice_shape)
        if len(parameter_space)==0:

            raise ValueError('Empty parameter space: try to reduce the \'decomposition_level_min\' or change the'
                             'range of the \'sigma\' (i.e. parameters \'sigma_min\',\'sigma_max\', and \'sigma_step\')')

        # Grid search optimization
        self.write('Optimization method: grid search')
        self.write('Optimization mode: serial')
        self.write('Total number of parameters combinations: {}'.format(len(parameter_space)))
        Ls = []
        for n,el in self.vtqdm(enumerate(parameter_space)):

            candidate_wavelet_name = el[0]
            candidate_sigma = el[1]
            candidate_level = el[2]
            L = 0
            for slice in x:

                # if x.n_channels > 1:
                #
                #     slice = slice[...,0]    # Temporary for multichannel images: all channels with the same sigma

                params = {'wavelet_name':candidate_wavelet_name,
                          'sigma':candidate_sigma,
                          'level':candidate_level}
                loss_val = self._self_supervised_decurtaining_loss(slice,self._destripe_slice,params)
                L = L+loss_val

            Ls.append(L)
            self.progress_bar(n,len(parameter_space),15,'{}/{}'.format(n,len(parameter_space)))

        return parameter_space,Ls

    def _fit_parallel(self,x):
        """
        Parallel version of the fitting routine.

        :param x: (ndarray) portion of the stack to be used for the optimization
        :return: (list) the parameter space, (list) the corresponding loss value.
        """
        def func_to_par(el):

            candidate_wavelet_name = el[0]
            candidate_sigma = el[1]
            candidate_level = el[2]
            L = 0
            for slice in x:

                # if x.n_channels > 1:
                #
                #     slice = slice[..., 0]  # Temporary for multichannel images: all channels with the same sigma

                params = {'wavelet_name': candidate_wavelet_name,
                          'sigma': candidate_sigma,
                          'level': candidate_level}
                loss_val = self._self_supervised_decurtaining_loss(slice,self._destripe_slice,params)
                L = L+loss_val

            return L

        # Create the parameter space for the grid search
        slice_shape = (x.shape[1], x.shape[2])
        parameter_space = self._generate_parameter_space(slice_shape)
        if len(parameter_space)==0:

            raise ValueError('Empty parameter space: try to reduce the \'decomposition_level_min\' or change the'
                             'range of the \'sigma\' (i.e. parameters \'sigma_min\',\'sigma_max\', and \'sigma_step\')')

        # Grid search optimization
        self.write('Optimization method: grid search')
        self.write('Total number of parameters combinations: {}'.format(len(parameter_space)))
        self.write('Optimization mode: parallel')
        Ls = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(el) for el in self.vtqdm(parameter_space))
        return parameter_space,Ls

    def fit(self,x):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        vol_for_optimization = x.data[::self.fit_step,...]
        if self.use_bounding_box:

            vol_for_optimization = vol_for_optimization[:,self.y_limits_bbox[0]:self.y_limits_bbox[1],
                                                          self.x_limits_bbox[0]:self.x_limits_bbox[1],...]
        if x.n_channels > 1:

            vol_for_optimization = vol_for_optimization[..., 0]  # Temporary for multichannel images: all channels with the same sigma

        self.write('Destriper optimization routine')
        self.write('-------------------------------')
        if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                and not self.force_serial:

            parameter_space,Ls = self._fit_parallel(vol_for_optimization)

        else:

            parameter_space,Ls = self._fit_serial(vol_for_optimization)

        best_parameters = parameter_space[np.argmin(Ls)]
        self.wavelet_name, self.sigma, self.decomposition_level = best_parameters
        if self.set_decomposition_level_to_max_compatible:

            self.decomposition_level = pywt.dwtn_max_level((x.shape[1],x.shape[2]),self.wavelet_name)
            if self.increase_decomposition_level_during_inference:

                self.decomposition_level = self.decomposition_level+1

        self.write('Best filter setting: {}'.format({'wavelet_name': self.wavelet_name,
                                                     'sigma':self.sigma,
                                                     'decomposition_level':self.decomposition_level}))
        self.write('-------------------------------')

    @staticmethod
    def _destripe_slice(x,wavelet_name,sigma,level):
        """
        Core destriper transformation which is applied to a slice of a stack.

        :param x: (ndarray) array containing the image to process.
        :param wavelet_name: (str) name of the wavelet to be used.
        :param sigma: (float) standard deviation of the gaussian filter used to remove vertical lines.
        :param level: (int) decomposition level of the wavelet transform
        :return: (ndarray) the destriped image.
        """
        res = pywt.wavedec2(x,wavelet_name,level=level)
        filtred_res = []
        for coeff in res:

            if type(coeff) is tuple:

                cV = coeff[1]
                fft2_cV = fftpack.fftshift(fftpack.fft2(cV))
                size_y, size_x = fft2_cV.shape

                x_hat = (np.arange(-size_y,size_y,2)+1)/2
                filter_transfer_function = -np.expm1(-x_hat**2/(2*sigma**2))
                filter_transfer_function = np.tile(filter_transfer_function,(size_x,1)).T
                fft2_cV = fft2_cV*filter_transfer_function

                cV = fftpack.ifft2(fftpack.ifftshift(fft2_cV))
                filtred_res.append((coeff[0],np.real(cV),coeff[2]))

            else:

                filtred_res.append(coeff)

        return pywt.waverec2(filtred_res,wavelet_name)

    def _transform_serial(self,x):
        """
        Core method. Serial implementation of the application of the wavelet-fourier filer to a stack.

        :param x: stack object on which the transformation is applied.
        :return: (ndarray) array containing the transformed data.
        """
        if x.n_channels > 1:

            transformed_volume = []
            for C in self.vtqdm(range(x.n_channels)):

                transformed_volume_C = []
                for slice in self.vtqdm(x.data[...,C]):

                    corrected_slice = self._destripe_slice(slice,self.wavelet_name,self.sigma,self.decomposition_level)
                    if self.match_in_out_contrast:

                        corrected_slice = match_histograms(corrected_slice,slice)

                    transformed_volume_C.append(corrected_slice)

                transformed_volume.append(transformed_volume_C)

            return np.array(transformed_volume).transpose((1,2,3,0))

        transformed_volume = []
        for slice in self.vtqdm(x.data):

            corrected_slice = self._destripe_slice(slice,self.wavelet_name,self.sigma,self.decomposition_level)
            if self.match_in_out_contrast:

                corrected_slice = match_histograms(corrected_slice,slice)

            transformed_volume.append(corrected_slice)

        return np.array(transformed_volume)

    def _transform_parallel(self, x):
        """
        Core method. Parallel implementation of the application of the wavelet-fourier filer to a stack.

        :param x: stack object on which the transformation is applied.
        :return: array containing the transformed data.
        """

        def func_to_par(slice):
            """
            function to parallelize
            """
            corrected_slice = self._destripe_slice(slice,self.wavelet_name,self.sigma,self.decomposition_level)
            if self.match_in_out_contrast:

                corrected_slice = match_histograms(corrected_slice,slice)

            return corrected_slice

        if x.n_channels > 1:

            transformed_volume = []
            for C in self.vtqdm(range(x.n_channels)):

                transformed_volume_C = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(slice) for slice in self.vtqdm(x.data[...,C]))
                transformed_volume.append(transformed_volume_C)

            return np.array(transformed_volume).transpose((1,2,3,0))

        transformed_volume = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(slice) for slice in self.vtqdm(x.data))
        return np.array(transformed_volume)

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if self.auto_optimize and self.fit_enable:

            self.fit(x)

        elif not hasattr(self,'sigma'):

            raise ValueError('No parameter \'sigma\' present: specify it in the transformation dictionary.')

        if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                and not self.force_serial:

            if not inplace:

                return self._transform_parallel(x)

            x.from_array(self._transform_parallel(x))

        else:

            if not inplace:

                return self._transform_serial(x)

            x.from_array(self._transform_serial(x))
