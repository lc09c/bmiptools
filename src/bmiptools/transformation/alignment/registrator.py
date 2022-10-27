# Title: 'registrator.rst.py'
# Date: 21/05/2021
# Author: Curcuraci L.
#
# Scope: Class used to apply registration algorithms to a given stack object.

"""
Plugin used to apply registration algorithms to a given stack object.
"""

#################
#####   LIBRARIES
#################


import numpy as np
import cv2
import os
from joblib import Parallel,delayed
from skimage.registration import optical_flow_tvl1
from skimage.transform import warp

import bmiptools.core.math_utils as mut
from bmiptools.core.ip_utils import standardizer
from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI


###############
#####   CLASSES
###############

# TODO: this plugin is still single channel!!!!!!

class Registrator(TransformationBasic):
    """
    Class used to register a stack.
    """

    __version__ = '0.4'
    empty_transformation_dictionary = {'load_existing_registration': False,
                                       'loading_path': ' ',
                                       'registration_algorithm':'ECC',
                                       'padding_val': 0,
                                       'destandardize': True,
                                       'template_lh_boundary_factor': 1,
                                       'template_rb_boundary_factor': 1,
                                       'ECC_registration_setting': {'n_iterations': 5000,
                                                                    'termination_eps': 1e-10,
                                                                    'motion_model':'Translation',
                                                                    'ecc_threshold': 0.7},
                                       'phase_correlation_registration_setting': {'motion_model': 'Translation',
                                                                                  'phase_corr_threshold': 0.4,
                                                                                  },
                                       'opt_bounding_box': {'use_bounding_box': True,
                                                            'y_limits_bbox': [-500,None],
                                                            'x_limits_bbox': [500,1500]},
                                       'refine_with_optical_flow': False,
                                       'OF_setting':{'optical_flow_attachment': 5,
                                                     'save_mod_OF': False,
                                                     'mod_OF_saving_path': ''},
                                       'save_fitted_registration': False,
                                       'saving_path': ' '
                                       }
    _guipi_dictionary = {'load_existing_registration': GuiPI(bool),
                         'loading_path': GuiPI('path',filemode='r'),
                         'registration_algorithm': GuiPI('options',options=['ECC','Phase_correlation']),
                         'padding_val': GuiPI(float),
                         'destandardize': GuiPI(bool),
                         'template_lh_boundary_factor': GuiPI(float, min=0, visible=False),
                         'template_rb_boundary_factor': GuiPI(float, min=0, visible=False),
                         'ECC_registration_setting':{'n_iterations': GuiPI(int),
                                                     'termination_eps': GuiPI(float,min=1e-15),
                                                     'motion_model': GuiPI('options',
                                                                        options=['Translation','Euclidean','Affine']),
                                                     'ecc_threshold': GuiPI(float,min=0,max=1)},
                         'phase_correlation_registration_setting': {'motion_model': GuiPI('options',options=['Translation']),
                                                                    'phase_corr_threshold': GuiPI(float,min=0,max=1)},
                         'refine_with_optical_flow': GuiPI(bool),
                         'OF_setting': {'optical_flow_attachment': GuiPI(float),
                                        'save_mod_OF': GuiPI(bool),
                                        'mod_OF_saving_path': GuiPI('filepath',visible=False,filemode='d')},
                         'opt_bounding_box': {'use_bounding_box': GuiPI(bool),
                                              'y_limits_bbox': GuiPI('math'),
                                              'x_limits_bbox': GuiPI('math')},
                         'save_fitted_registration': GuiPI(bool),
                         'saving_path': GuiPI('path',filemode='d')
                         }
    def __init__(self,transformation_dictionary,force_serial=False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'load_existing_registration': (bool) if True an existing registration produced by this plugin is loaded.

            'loading_path': (raw str) path to the files containing the existing registration parameters. If the above
            argument is false this field is simply ignored.

            'registration_algorithm': (str) Algorithm used to perform the registration. The possible options are:

            1. 'ECC' = Optimises transformation parameters maximizing the Enhanced Correlation Coefficients (see
               G.D.Evangelidis, E.Z.Psarakis, "Parametric Image Alignment using Enhanced Correlation Coefficient" IEEE
               Trans. on PAMI, vol.30, no.10, 2008).

            2. 'Phase_correlation' = FFT based phase correlation method for rigid registration.

            'padding_val': (float) value used for padding the images in order to reach a certain shape during
            registration.

            'destandardize': (bool) if True at the end of the registration ,the image is destandardized (image
            standardization take place before the optimization of the registration algorithm).

            'ECC_registration_setting': (dict) Dictionary containing the setting for the ECC registration algorithm. The
            dictionary has to be specified as below:

                {'n_iterations': (int) number of iterations used for the maximization of the ECC.

                'termination_eps': (float) number used to determine the convergence of the ECC maximization algorithm:
                if the difference between the ECC values after two iterations is less then 'termination_eps', then the
                maximization stops.

                'motion_model': (str) kind of motion model used for the estimation of the parameters used for the
                registration. The available motion model are

                    1. 'Translation'= assumes that the two images differ only by a rigid translation (recommended);

                    2. 'Euclidean'= assumes that the two images differ by an euclidean transformation
                       ( i.e. rotation + translation);

                    3. 'Affine'= assumes that the two images differ by an affine transformation.

                'template_lh_boundary_factor': (float) left/high boundary factor for the template window definition
                (recommended value: 1)

                'template_rb_boundary_factor': (float) right/bottom boundary factor for the template window definition
                (recommended value: 1)

                'ecc_threshold': (float between 0 and 1) threshold on the ECC value at the end of the maximization
                procedure below which a two step estimation procedure for the estimation of the transformation
                parameters is run. },

            'phase_correlation_registration_setting': dict) Dictionary containing the setting for the registration
            algorithm based on the phase correlation techniques. The dictionary has to be specified as below:

                {'motion_model': (str) kind of motion model used for the estimation of the parameter. Currently, only
                'Translation' is possible.

                'phase_corr_threshold': (float between 0 and 1) threshold on the normalized correlation below which the
                two steps registration optimization is executed.},

            'opt_bounding_box': (dict) dictionary containing the setting of the bounding box used during the
            optimization. The bounding box defines the part of the stack (in the YX plane) which is considered by the
            optimization routine. It has to be specified as below:

                {'use_bounding_box': (bool) if True the bounding box is used, otherwise the whole YX plane is used. In
                this last case the two arguments below are ignored.

                'y_limits_bbox': (list) list specifying the extrema along the Y-direction (i.e. axis 0). This list can
                contain numpy-like instruction for the definition of the range. The following examples should clarify
                the usage. Let arr be a numpy array

                                        [100,300]   => arr[100:300,:]

                                        [-500,None] => arr[-500:,:]

                                        [None,200]  => arr[:200,:]

                'x_limits_bbox': (list) list specifying the extrema along the X-direction (i.e. axis 1). This list can
                contain numpy-like instruction for the definition of the range. The following examples should clarify
                the usage. Let arr be a numpy array

                                        [100,300]   => arr[:,100:300]

                                        [-500,None] => arr[:,-500:]

                                        [None,200]  => arr[:,:200]
                },

            'refine_with_optical_flow': (bool) if True a final refinement with optical flow registration is applied at
            after that the first (rough in principle) registration has been applied on the stack.

            'OF_setting': (dict) Dictionary containing the setting of the optical flow registration. This dictionary has
            to be specified as follow:

                {'optical_flow_attachment': (float) attachment parameter of the optical flow registration algorithm.

                'save_mod_OF': (bool) if True the modulus of the optical flow field is saved.

                'mod_OF_saving_path': (raw str) path where the modulus of the optical flow registration field is saved.
                If the above field is False this field is ignored.

                },

            'save_fitted_registration': (bool) if True the parameters obtained from the ECC or Phase correlation based
            registration are saved. Nothing is saved in any case for the optical flow refinement step.

            'saving_path': (raw str) path where the registration parameters are saved.

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        :param force_serial: (bool) if True serial behavior is forced for this plugin independently on the global
                             setting of bmiptools.
        """
        super(Registrator,self).__init__()
        self.force_serial = force_serial
        self._supported_registration_algorithm = ['ECC','phase_correlation']

        self.load_existing_registration = transformation_dictionary['load_existing_registration']
        if self.load_existing_registration:

            self.loading_path = transformation_dictionary['loading_path']

        self.registration_algorithm = transformation_dictionary['registration_algorithm']
        self.padding_val = transformation_dictionary['padding_val']
        self.destandardize = transformation_dictionary['destandardize']
        self.template_lh_boundary_factor = transformation_dictionary['template_lh_boundary_factor']
        self.template_rb_boundary_factor = transformation_dictionary['template_rb_boundary_factor']
        if transformation_dictionary['registration_algorithm'] == 'ECC':

            self._supported_motion_model = ['Translation','Euclidean','Affine']
            self.n_iterations = transformation_dictionary['ECC_registration_setting']['n_iterations']
            self.termination_eps = transformation_dictionary['ECC_registration_setting']['termination_eps']
            self.motion_model = transformation_dictionary['ECC_registration_setting']['motion_model']
            self.ecc_threshold = transformation_dictionary['ECC_registration_setting']['ecc_threshold']

        elif transformation_dictionary['registration_algorithm'] == 'Phase_correlation':

            self._supported_motion_model = ['Translation']
            self.motion_model = transformation_dictionary['phase_correlation_registration_setting']['motion_model']
            self.phase_corr_threshold = \
                transformation_dictionary['phase_correlation_registration_setting']['phase_corr_threshold']

        else:

            raise ValueError('Unrecognized registration type. Available registration '
                             'algorithms: \n{}'.format(self._supported_registration_type))

        self.use_bounding_box = transformation_dictionary['opt_bounding_box']['use_bounding_box']
        if transformation_dictionary['opt_bounding_box']['use_bounding_box']:

            self.y_limits_bbox = transformation_dictionary['opt_bounding_box']['y_limits_bbox']
            self.x_limits_bbox = transformation_dictionary['opt_bounding_box']['x_limits_bbox']

        self.refine_with_optical_flow = transformation_dictionary['refine_with_optical_flow']
        if self.refine_with_optical_flow:

            self.optical_flow_attachment = transformation_dictionary['OF_setting']['optical_flow_attachment']
            self.save_mod_OF = transformation_dictionary['OF_setting']['save_mod_OF']
            self.mod_OF_saving_path = transformation_dictionary['OF_setting']['mod_OF_saving_path']

        self.save_fitted_registration = transformation_dictionary['save_fitted_registration']
        if self.save_fitted_registration:

            self.saving_path = transformation_dictionary['saving_path']

        self._setup()

    def _setup(self):

        if self.load_existing_registration:

            self.load_registration(self.loading_path)

        else:

            if self.registration_algorithm == 'ECC':

                self.warp_matrix = np.eye(2,3,dtype=np.float32)
                self.termination_criteria = (cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,
                                             self.n_iterations,self.termination_eps)
                if self.motion_model == 'Translation':

                    self.warp_mode = cv2.MOTION_TRANSLATION

                elif self.motion_model == 'Euclidean':

                    self.warp_mode = cv2.MOTION_EUCLIDEAN

                elif self.motion_model == 'Affine':

                    self.warp_mode = cv2.MOTION_AFFINE

                else:

                    raise ValueError('Unrecognized motion model. Chose among the available motion model reported '
                                     'below:\n{}'.format(self._supported_motion_model))

    # core methods
    @staticmethod
    def _destandardize(x,stats,standardization_type):
        """
        Core method. De-standardize a stack (inverse of the standardization).

        :param x: (ndarray) array to de-standardize.
        :param stats: (dict) dictionary containing the stack statistics (as produced by the 'statistics()' method of
                      a stack object).
        :param standardization_type: (str) type of standardization performed (only standardization supported by the
                                      'bmiptools.core.ip_utils.standardize' function).
        """
        if standardization_type == 'mean/std':

            return x*stats['stack_std']+stats['stack_mean']

        elif standardization_type == '-1/1':

            return x*((stats['max_stack']-stats['min_stack'])-1)/2+stats['min_stack']

        elif standardization_type == '0/1':

            return x*(stats['max_stack']-stats['min_stack'])+stats['min_stack']

        else:

            return x

    @staticmethod
    def _match_template(img,ref,lh_boundary_fact,rb_boundary_fact):
        """
        Template matching routine. Given two images, the input and the reference, from the reference the central part is
        cropped and used as template to estimate the parameters for the translation of the input with respect to the
        reference. The estimation is done by looking at the maximum of the absolute value for the cross-correlation of
        the two images (i.e. by using the fourier shift theorem).

        :param img: (nparray) image to be matched.
        :param ref: (nparray) reference image for the matching.
        :param lh_boundary_fact: (float) value used to regulate the left/high size of the template ued for the
                                 estimation of the translation parameters.
        :param rb_boundary_fact: (float) value used to regulate the right/bottom size of the template used for the
                                 estimation of the translation parameters.
        :return: (nparray) array containing the raw aligned image, (float) y coordinate of the maximum of the modulus
                 of the cross-correlation, (float) x coodinate of the maximum of the modulus of the cross-correlation.
        """
        y_template_min = int(2/5*lh_boundary_fact*img.shape[0])
        y_template_max = int(3/5*rb_boundary_fact*img.shape[0])
        x_template_min = int(2/5*lh_boundary_fact*img.shape[1])
        x_template_max = int(3/5*rb_boundary_fact*img.shape[1])

        corrmap = cv2.matchTemplate(img, ref[y_template_min:y_template_max, x_template_min:x_template_max],
                                    method=cv2.TM_CCOEFF_NORMED)

        y_max, x_max = np.where(np.abs(corrmap) == np.max(np.abs(corrmap)))
        y_max = int(y_max-corrmap.shape[0]//2)
        x_max = int(x_max-corrmap.shape[1]//2)

        partial_warp_matrix = np.eye(2,3,dtype=np.float32)
        partial_warp_matrix[0,-1] = x_max
        partial_warp_matrix[1,-1] = y_max
        partial_alignment = cv2.warpAffine(img, partial_warp_matrix,
                                           dsize=img.shape,
                                           flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)

        return partial_alignment,y_max,x_max

    @staticmethod
    def _expand_image(image,dsize0=[0,0],dsize1=[0,0],padding_val=0,inverse_warp=False,**kwargs):
        """
        Expand the size of the image to match a given shape. The original image is placed in the center of the expanded
        image

        :param image: (nparray) array containing the image.
        :param dsize0: (list of int) increase of the shape for the 0th axis, written in the format [Left,Right].
        :param dsize1: (list of int) increase of the shape for the 1th axis, written in the format [Bottom,Top].
        :param padding_val: (float) value used to pad the image in order to reach the desired shape.
        :param inverse_warp: (bool) True if the inverse_warp attribute will be used by the opencv functions.
        :return: (nparray) array containing the expanded image.
        """
        my, My = np.abs(dsize0)
        mx, Mx = np.abs(dsize1)
        canvas_shape = tuple(np.array(image.shape) + np.array([my + My, mx + Mx]))
        canvas = padding_val * np.ones(canvas_shape, **kwargs)
        if inverse_warp:

            if my == 0:

                my = -image.shape[0] - My

            if mx == 0:

                mx = -image.shape[1] - Mx

            canvas[My:-my, Mx:-mx] = image

        else:

            if My == 0:

                My = -image.shape[0] - my

            if Mx == 0:

                Mx = -image.shape[1] - mx

            canvas[my:-My, mx:-Mx] = image

        return canvas

    def save_registration(self,path):
        """
        Save registration parameters (cumulated affine matrix) found during the registration fit.

        :param path: (str) path where the registration parameters are saved.
        """
        try:

            np.save(path,self.cumulated_warp_matrices_list,allow_pickle=True)
            self.write('Registration matrices saved!')

        except:

            self.write('Nothing to save.')

    def load_registration(self,path):
        """
        Load registration parameters (cumulated affine matrix) found during a previous registration fit.

        P.A.: The stack used for estimation of the loaded registration parameters, and the stack on which these
        parameters are applied need to have at least the same number of slice, in order for this operation to make
        sense.

        :param path: (str) path where the registration parameters are saved.
        """
        try:

            self.cumulated_warp_matrices_list = np.load(path,allow_pickle=True)
            self.write('Registration matrices loaded!')

        except:

            self.write('No valid registration file found at \'{}\''.format(path))

    @staticmethod
    def _save_OF(u,v,path):
        """
        Save square modulus of optical flow as png image.

        :param u: (ndarray) flow along the 0 axis.
        :param v: (ndarray) flow along the 1 axis.
        :param path: (str) saving path.
        """
        uv = u ** 2 + v ** 2
        if np.max(uv) == 0:

            den = 1

        else:

            den = np.max(uv) - np.min(uv)

        uv = (uv - np.min(uv)) / den
        uv = (256 * uv).astype(np.uint8)
        cv2.imwrite(path, uv)

    # fit methods
    def _fit_ECC_parallel(self,x):
        """
        Fit the transformation parameters for an ECC based registration algorithm in parallel way.

        :param x: (nparray) array containing the stack.
        """

        def func_to_par(N,x):

            ref = x[N - 1].astype('float32')
            img = x[N].astype('float32')
            try:

                warp_matrix = np.eye(2, 3, dtype=np.float32)
                (cc, warp_matrix) = cv2.findTransformECC(ref,img,warp_matrix,
                                                         motionType=self.warp_mode,
                                                         criteria=self.termination_criteria)

                if cc < self.ecc_threshold:

                    # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                    # translation parameters.
                    partial_alignment, y_max, x_max = self._match_template(img, ref,
                                                                           self.template_lh_boundary_factor,
                                                                           self.template_rb_boundary_factor)
                    warp_matrix2 = np.eye(2, 3, dtype=np.float32)
                    try:

                        (cc2, warp_matrix2) = cv2.findTransformECC(ref,partial_alignment,warp_matrix2,
                                                                   motionType=self.warp_mode,
                                                                   criteria=self.termination_criteria)

                    except:

                        cc2=0
                        pass

                    if cc2 > cc:

                        # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                        # translation parameters.
                        warp_matrix2[0, -1] = warp_matrix2[0, -1]+x_max
                        warp_matrix2[1, -1] = warp_matrix2[1, -1]+y_max
                        warp_matrix = warp_matrix2

            except:

                # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                # translation parameters.
                partial_alignment,y_max,x_max =self._match_template(img,ref,
                                                                       self.template_lh_boundary_factor,
                                                                       self.template_rb_boundary_factor)
                warp_matrix = np.eye(2, 3, dtype=np.float32)
                try:

                    (cc,warp_matrix) = cv2.findTransformECC(ref,partial_alignment,warp_matrix,
                                                             motionType=self.warp_mode,
                                                             criteria=self.termination_criteria)

                except:

                    pass

                # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                # translation parameters.
                warp_matrix[0, -1] = warp_matrix[0, -1]+x_max
                warp_matrix[1, -1] = warp_matrix[1, -1]+y_max

            return warp_matrix

        self.write('-------------------------------------')
        self.write('Estimating warping matrices...')
        self.write('Method: {}'.format(self.registration_algorithm))
        self.write('Slice | Correlation with previous')
        self.warp_matrices_list = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(N,x)
                                                                    for N in self.vtqdm(range(1, len(x))))
        warp_matrices_list = self.warp_matrices_list

        # compute the total transformation matrix for each given slice (i.e. the transformation cumulated for all the
        # previous slices).
        self.cumulated_warp_matrices_list = [np.eye(2, 3, dtype='float32')]
        for wmat in warp_matrices_list:

            new_wmat = np.eye(2, 3, dtype='float32')
            prev_wmat = self.cumulated_warp_matrices_list[-1]
            new_wmat[:, -1] = prev_wmat[:, -1] + wmat[:, -1]
            new_wmat[:, :-1] = np.dot(prev_wmat[:, :-1], wmat[:, :-1])
            self.cumulated_warp_matrices_list.append(new_wmat)

        self.write('Registration parameters estimation terminated!')

    def _fit_ECC_serial(self,x):
        """
        Fit the transformation parameters for an ECC based registration algorithm in serial way.

        :param x: (nparray) array containing the stack.
        """
        self.write('-------------------------------------')
        self.write('Estimating warping matrices...')
        self.write('Method: {}'.format(self.registration_algorithm))
        self.write('Slice | Correlation with previous')
        warp_matrices_list = []
        for N in range(1, len(x)):

            ref = x[N - 1].astype('float32')
            img = x[N].astype('float32')
            try:

                warp_matrix = np.eye(2, 3, dtype=np.float32)
                (cc, warp_matrix) = cv2.findTransformECC(ref, img, warp_matrix,
                                                         motionType=self.warp_mode,
                                                         criteria=self.termination_criteria)

                if cc < self.ecc_threshold:

                    # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                    # translation parameters.
                    partial_alignment, y_max, x_max = self._match_template(img, ref,
                                                                           self.template_lh_boundary_factor,
                                                                           self.template_rb_boundary_factor)
                    warp_matrix2 = np.eye(2, 3, dtype=np.float32)
                    try:

                        (cc2, warp_matrix2) = cv2.findTransformECC(ref, partial_alignment, warp_matrix2,
                                                                   motionType=self.warp_mode,
                                                                   criteria=self.termination_criteria)

                    except:

                        cc2 = 0
                        pass

                    if cc2 > cc:
                        # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                        # translation parameters.
                        warp_matrix2[0, -1] = warp_matrix2[0, -1] + x_max
                        warp_matrix2[1, -1] = warp_matrix2[1, -1] + y_max
                        warp_matrix = warp_matrix2
                        cc = cc2

                self.write('{} | {}'.format(N, cc))

            except:

                self.write('{} |  Simple ECC estimation failed: two-step registration started...'.format(N))

                # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                # translation parameters.
                partial_alignment, y_max, x_max = self._match_template(img, ref,
                                                                       self.template_lh_boundary_factor,
                                                                       self.template_rb_boundary_factor)
                warp_matrix = np.eye(2, 3, dtype=np.float32)
                try:

                    (cc,warp_matrix) = cv2.findTransformECC(ref,partial_alignment,warp_matrix,
                                                            motionType=self.warp_mode,
                                                            criteria=self.termination_criteria)

                except:

                    pass

                # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                # translation parameters.
                warp_matrix[0, -1] = warp_matrix[0, -1] + x_max
                warp_matrix[1, -1] = warp_matrix[1, -1] + y_max
                self.write('{} | {}'.format(N, cc))

            warp_matrices_list.append(warp_matrix)

        # compute the total transformation matrix for each given slice (i.e. the transformation cumulated for all the
        # previous slices).
        self.cumulated_warp_matrices_list = [np.eye(2, 3, dtype='float32')]
        for wmat in warp_matrices_list:

            new_wmat = np.eye(2, 3, dtype='float32')
            prev_wmat = self.cumulated_warp_matrices_list[-1]
            new_wmat[:, -1] = prev_wmat[:, -1] + wmat[:, -1]
            new_wmat[:, :-1] = np.dot(prev_wmat[:, :-1], wmat[:, :-1])
            self.cumulated_warp_matrices_list.append(new_wmat)

        self.write('Registration parameters estimation terminated!')

    def _fit_phase_corr_parallel(self, x):
        """
        Fit the transformation parameters for an phase correlation / FFT based registration algorithm in parallel way.

        :param x: (nparray) array containing the stack.
        """

        def func_to_par(N):

            ref = x[N - 1].astype('float32')
            img = x[N].astype('float32')
            warp_matrix = np.eye(2, 3, dtype=np.float32)
            (shifts, err) = cv2.phaseCorrelate(ref, img)
            if err < self.phase_corr_threshold:

                # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                # translation parameters.
                partial_alignment, y_max, x_max = self._match_template(img, ref,
                                                                       self.template_lh_boundary_factor,
                                                                       self.template_rb_boundary_factor)

                try:

                    self.write('initial shifts: {} | {}'.format(shifts[0], shifts[1]))
                    (shiftst, errt) = cv2.phaseCorrelate(ref, partial_alignment)
                    shiftstot = (shiftst[0] + x_max, shiftst[1] + y_max)
                    self.write('new shifts: {} | {}'.format(shiftstot[0], shiftstot[1]))
                    self.write('{} | {}'.format(N, errt))
                    if errt > err:

                        shifts = shiftstot

                except:

                    pass

            warp_matrix[0, -1] = shifts[0]
            warp_matrix[1, -1] = shifts[1]
            return warp_matrix

        self.write('-------------------------------------')
        self.write('Estimating warping matrices...')
        self.write('Method: {}'.format(self.registration_algorithm))
        self.write('Slice | Correlation with previous')
        warp_matrices_list = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(N)
                                                                    for N in self.vtqdm(range(1, len(x))))

        # compute the total transformation matrix for each given slice (i.e. the transformation cumulated for all the
        # previous slices).
        self.cumulated_warp_matrices_list = [np.eye(2, 3, dtype='float32')]
        for wmat in warp_matrices_list:

            new_wmat = np.eye(2, 3, dtype='float32')
            prev_wmat = self.cumulated_warp_matrices_list[-1]
            new_wmat[:, -1] = prev_wmat[:, -1] + wmat[:, -1]
            new_wmat[:, :-1] = np.dot(prev_wmat[:, :-1], wmat[:, :-1])
            self.cumulated_warp_matrices_list.append(new_wmat)

        self.write('Registration parameters estimation terminated!')

    def _fit_phase_corr_serial(self, x):
        """
        Fit the transformation parameters for an phase correlation / FFT based registration algorithm in serial way.

        :param x: (nparray) array containing the stack.
        """

        warp_matrices_list = []
        self.write('-------------------------------------')
        self.write('Estimating warping matrices...')
        self.write('Method: {}'.format(self.registration_algorithm))
        self.write('Slice | Correlation with previous')
        for N in range(1, len(x)):

            ref = x[N - 1].astype('float32')
            img = x[N].astype('float32')
            try:

                warp_matrix = np.eye(2, 3, dtype=np.float32)
                (shifts, err) = cv2.phaseCorrelate(ref,img)
                self.write('{} | {}'.format(N, err))
                if err < self.phase_corr_threshold:

                    self.write('{} |  Simple phase-correlation estimation failed: two-step registration '
                               'started...'.format(N))

                    # P.A.: numpy use the yx convention, while opencv use the xy convention for the definition of the
                    # translation parameters.
                    partial_alignment, y_max, x_max = self._match_template(img, ref,
                                                                           self.template_lh_boundary_factor,
                                                                           self.template_rb_boundary_factor)

                    try:

                        self.write('initial shifts: {} | {}'.format(shifts[0], shifts[1]))
                        (shiftst, errt) = cv2.phaseCorrelate(ref, partial_alignment)
                        shiftstot = (shiftst[0] + x_max, shiftst[1] + y_max)
                        self.write('new shifts: {} | {}'.format(shiftstot[0], shiftstot[1]))
                        self.write('{} | {}'.format(N, errt))
                        if errt > err:

                            shifts = shiftstot

                        self.write('final 2 steps shifts: {} | {}'.format(shifts[0], shifts[1]))

                    except:

                        self.write('{} | two steps reregistration failed'.format(N))
                        pass

                warp_matrix[0, -1] = shifts[0]
                warp_matrix[1, -1] = shifts[1]

            except:

                self.write('{} | Phase-correlation estimation failed'.format(N))
                pass

            # Here I print the shifs, used for debugging
            # self.write('{} | {}'.format(warp_matrix[0, -1], warp_matrix[1, -1]))
            warp_matrices_list.append(warp_matrix)

        # compute the total transformation matrix for each given slice (i.e. the transformation cumulated for all the
        # previous slices).
        self.cumulated_warp_matrices_list = [np.eye(2, 3, dtype='float32')]
        for wmat in warp_matrices_list:

            new_wmat = np.eye(2, 3, dtype='float32')
            prev_wmat = self.cumulated_warp_matrices_list[-1]
            new_wmat[:, -1] = prev_wmat[:, -1] + wmat[:, -1]
            new_wmat[:, :-1] = np.dot(prev_wmat[:, :-1], wmat[:, :-1])
            self.cumulated_warp_matrices_list.append(new_wmat)

        self.write('Registration parameters estimation terminated!')

    def fit(self,x):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        if not self.load_existing_registration:

            ymin, ymax, xmin, xmax = 4 * [None, ]
            if self.use_bounding_box:

                ymin, ymax = self.y_limits_bbox
                xmin, xmax = self.x_limits_bbox

            if self.registration_algorithm == 'ECC' and self.fit_enable:

                if self._use_multiprocessing and not self.force_serial:

                    self._fit_ECC_parallel(x.data[:,ymin:ymax,xmin:xmax])

                else:

                    self._fit_ECC_serial(x.data[:,ymin:ymax,xmin:xmax])

            if self.registration_algorithm == 'Phase_correlation' and self.fit_enable:

                if self._use_multiprocessing and not self.force_serial:

                    self._fit_phase_corr_parallel(x.data[:,ymin:ymax,xmin:xmax])

                else:

                    self._fit_phase_corr_serial(x.data[:,ymin:ymax,xmin:xmax])

            if self.save_fitted_registration:

                self.save_registration(self.saving_path)

        else:

            self.load_registration(self.loading_path)

    # transform methods
    def _warp_parallel(self,x,dsize_y,dsize_x):
        """
        Apply the registration found to the stack in parallel way.

        :param x: (nparray) array containing the stack.
        :param dsize0: (list of int) increase of the shape for the 0th axis, written in the format [Left,Right].
        :param dsize1: (list of int) increase of the shape for the 1th axis, written in the format [Bottom,Top].
        :return: (nparray) the registered stack
        """

        def func_to_par(i,wmat):

            xi_plus_1 = x[i + 1]
            if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():

                xi_plus_1 = self._destandardize(xi_plus_1,
                                                x.temporary_library_metadata['Standardizer'][
                                                'pre_standardization_statistics'],
                                                x.temporary_library_metadata['Standardizer']['standardization_type'])

            expanded_slice = self._expand_image(xi_plus_1,dsize_y,dsize_x,self.padding_val,
                                                dtype='float32',inverse_warp=True)
            return cv2.warpAffine(expanded_slice,wmat,
                                  dsize=post_reg_shape[::-1],
                                  flags=cv2.INTER_CUBIC+cv2.WARP_INVERSE_MAP)

        x0 = x.data[0]
        if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():

            x0 = self._destandardize(x0,
                                     x.temporary_library_metadata['Standardizer']['pre_standardization_statistics'],
                                     x.temporary_library_metadata['Standardizer']['standardization_type'])

        post_reg_slice0 = self._expand_image(x0,dsize_y,dsize_x,self.padding_val, dtype='float32',inverse_warp=True)
        post_reg_shape = post_reg_slice0.shape
        registered_vol = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(i,wmat)
                                  for i, wmat in self.vtqdm(enumerate(self.cumulated_warp_matrices_list[1:])))
        return np.array([post_reg_slice0]+registered_vol)

    def _warp_serial(self,x,dsize_y,dsize_x):
        """
        Apply the registration found to the stack in serial way.

        :param x: (nparray) array containing the stack.
        :param dsize0: (list of int) increase of the shape for the 0th axis, written in the format [Left,Right].
        :param dsize1: (list of int) increase of the shape for the 1th axis, written in the format [Bottom,Top].
        :return: (nparray) the registered stack
        """

        x0 = x.data[0]
        if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():

            x0 = self._destandardize(x0,
                                     x.temporary_library_metadata['Standardizer']['pre_standardization_statistics'],
                                     x.temporary_library_metadata['Standardizer']['standardization_type'])

        post_reg_slice0 = self._expand_image(x0,dsize_y,dsize_x,self.padding_val,dtype='float32',inverse_warp=True)
        post_reg_shape = post_reg_slice0.shape
        registered_vol = [post_reg_slice0]
        for i, wmat in enumerate(self.cumulated_warp_matrices_list[1:]):

            xi_plus_1 = x[i + 1]
            if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():
                xi_plus_1 = self._destandardize(xi_plus_1,
                                                x.temporary_library_metadata['Standardizer'][
                                                    'pre_standardization_statistics'],
                                                x.temporary_library_metadata['Standardizer']['standardization_type'])

            expanded_slice = self._expand_image(xi_plus_1, dsize_y, dsize_x, self.padding_val,
                                                dtype='float32',inverse_warp=True)
            registered_vol.append(cv2.warpAffine(expanded_slice, wmat,
                                                 dsize=post_reg_shape[::-1],
                                                 flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP))

            return np.array(registered_vol)

    def _warp_parallel_with_OF(self,x,dsize_y,dsize_x):
        """
        Apply the registration found to the stack in parallel way, followed by an optical flow refinement step.

        :param x: (nparray) array containing the stack.
        :param dsize0: (list of int) increase of the shape for the 0th axis, written in the format [Left,Right].
        :param dsize1: (list of int) increase of the shape for the 1th axis, written in the format [Bottom,Top].
        :return: (nparray) the registered stack
        """

        def func_to_par(i,wmat):

            xi_plus_1 = x[i + 1]
            if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():

                xi_plus_1 = self._destandardize(xi_plus_1,
                                                x.temporary_library_metadata['Standardizer'][
                                                'pre_standardization_statistics'],
                                                x.temporary_library_metadata['Standardizer']['standardization_type'])

            expanded_slice = self._expand_image(xi_plus_1,dsize_y,dsize_x,self.padding_val,
                                                dtype='float32',inverse_warp=True)
            return cv2.warpAffine(expanded_slice,wmat,
                                  dsize=post_reg_shape[::-1],
                                  flags=cv2.INTER_CUBIC+cv2.WARP_INVERSE_MAP)

        x0 = x.data[0]
        if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():
            x0 = self._destandardize(x0,
                                     x.temporary_library_metadata['Standardizer']['pre_standardization_statistics'],
                                     x.temporary_library_metadata['Standardizer']['standardization_type'])

        post_reg_slice0 = self._expand_image(x0,dsize_y,dsize_x,self.padding_val, dtype='float32',inverse_warp=True)
        post_reg_shape = post_reg_slice0.shape
        ny,nx = post_reg_shape
        row_coords, col_coords = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
        registered_vol = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(i,wmat)
                                  for i, wmat in self.vtqdm(enumerate(self.cumulated_warp_matrices_list[1:])))
        registered_vol = [post_reg_slice0]+registered_vol
        for i in range(1,len(registered_vol)):

            mask = (registered_vol[i]>self.padding_val)*(registered_vol[i-1]>self.padding_val)
            v, u = optical_flow_tvl1(mask*standardizer(registered_vol[i-1], type='0/1'),
                                     mask*standardizer(registered_vol[i], type='0/1'),
                                     attachment=self.optical_flow_attachment,
                                     prefilter=True)
            registered_vol[i] = warp(registered_vol[i],np.array([row_coords+v,col_coords+u]),mode='edge')
            if self.save_mod_OF:

                self._save_OF(u,v,self.mod_OF_saving_path+os.sep+'OF_square_modulus_slices_{}-{}.png'.format(i,i+1))

        return np.array(registered_vol)

    def _warp_serial_with_OF(self,x,dsize_y,dsize_x):
        """
        Apply the registration found to the stack in serial way, followed by an optical flow refinement step.

        :param x: (nparray) array containing the stack.
        :param dsize0: (list of int) increase of the shape for the 0th axis, written in the format [Left,Right].
        :param dsize1: (list of int) increase of the shape for the 1th axis, written in the format [Bottom,Top].
        :return: (nparray) the registered stack
        """

        x0 = x.data[0]
        if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():

            x0 = self._destandardize(x0,
                                     x.temporary_library_metadata['Standardizer']['pre_standardization_statistics'],
                                     x.temporary_library_metadata['Standardizer']['standardization_type'])

        post_reg_slice0 = self._expand_image(x0, dsize_y, dsize_x, self.padding_val, dtype='float32',inverse_warp=True)
        post_reg_shape = post_reg_slice0.shape
        ny,nx = post_reg_shape
        row_coords, col_coords = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
        registered_vol = [post_reg_slice0]
        for i, wmat in enumerate(self.cumulated_warp_matrices_list[1:]):

            xi_plus_1 = x[i + 1]
            if self.destandardize and 'Standardizer' in x.temporary_library_metadata.keys():

                xi_plus_1 = self._destandardize(xi_plus_1,
                                                x.temporary_library_metadata['Standardizer'][
                                                    'pre_standardization_statistics'],
                                                x.temporary_library_metadata['Standardizer']['standardization_type'])

            expanded_slice = self._expand_image(xi_plus_1, dsize_y, dsize_x, self.padding_val, dtype='float32',
                                                inverse_warp=True)
            preOF_slice = cv2.warpAffine(expanded_slice, wmat,
                                         dsize=post_reg_shape[::-1],
                                         flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP)
            mask = (preOF_slice>self.padding_val)*(registered_vol[-1]>self.padding_val)
            v, u = optical_flow_tvl1(mask*standardizer(registered_vol[-1],type='0/1'),
                                     mask*standardizer(preOF_slice,type='0/1'),
                                     attachment=self.optical_flow_attachment,
                                     prefilter=True)

            if self.save_mod_OF:

                self._save_OF(u,v,self.mod_OF_saving_path+os.sep+'OF_square_modulus_slices_{}-{}.png'.format(i,i+1))

            postOF_slice = warp(preOF_slice, np.array([row_coords+v,col_coords+u]), mode='edge')
            registered_vol.append(postOF_slice)

        return np.array(registered_vol)

    def _transform(self,x):
        """
        Core method. ECC/Pahse correlation based registration algorithm for a stack.

        :param x: (stack) stack to be registered.
        :return: (nparray) array containing the registered stack.
        """
        self.write('-------------------------------------')
        self.write('Registration starting...')

        # compute the shape variations of the final images from the cumulated transformations found
        dsize_y = [np.floor(np.min(np.array(self.cumulated_warp_matrices_list)[:,1,2])).astype(int),
                   np.ceil(np.max(np.array(self.cumulated_warp_matrices_list)[:,1,2])).astype(int)]
        dsize_x = [np.floor(np.min(np.array(self.cumulated_warp_matrices_list)[:,0,2])).astype(int),
                   np.ceil(np.max(np.array(self.cumulated_warp_matrices_list)[:,0,2])).astype(int)]

        # apply registration
        if self._use_multiprocessing and not self.force_serial:

            if self.refine_with_optical_flow:

                registred_vol = self._warp_parallel_with_OF(x,dsize_y,dsize_x)

            else:

                registred_vol = self._warp_parallel(x,dsize_y,dsize_x)

        else:

            if self.refine_with_optical_flow:

                registred_vol = self._warp_serial_with_OF(x,dsize_y,dsize_x)

            else:

                registred_vol = self._warp_serial(x,dsize_y,dsize_x)

        self.write('...registration terminated!')
        self.write('-------------------------------------')
        return registred_vol

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        # fit, if it was not done previously
        if not hasattr(self,'cumulated_warp_matrices_list'):

            self.fit(x)

        # registration
        if self.registration_algorithm in ['ECC','Phase_correlation']:

            registered_vol = self._transform(x)

            # return result
            if not inplace:

                return registered_vol

            x.from_array(registered_vol)