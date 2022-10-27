# Title: 'decharge.py
# Author: L. Curcuraci
# Date: 16/02/21
#
# Scope: Plugin to remove/reduce the charging artifact typical of FIB-SEM images.

"""
Plugin to remove/reduce the charging artifact typical of FIB-SEM images.
"""

#################
#####   LIBRARIES
#################


import numpy as np

from skimage.morphology import reconstruction
from scipy.ndimage.morphology import binary_fill_holes,binary_dilation
from skimage.measure import label,regionprops
from skimage.restoration import rolling_ball
from joblib import Parallel,delayed

from bmiptools.transformation.basic.filters import gaussian_filter2d
from bmiptools.core.ip_utils import standardizer
from bmiptools.transformation.base import TransformationBasic
from bmiptools.transformation.restoration._restoration_shared import generate_parameter_space
from bmiptools.gui.gui_basic import GuiPI


###############
#####   CLASSES
###############


class Decharger(TransformationBasic):
    """
    Class used to reduce charging-like artifacts in a stack.
    """

    __version__ = '0.1'
    empty_transformation_dictionary = {'auto_optimize': True,
                                       'optimization_setting': {'dilation_iterations': 10,
                                                                'N_regions_for_opt': 20,
                                                                'gf1_sigma_list': [40,80,120],
                                                                'color_shift_list': [0.05,0.1,0.2],
                                                                'gf2_sigma_list': [40,80,120],
                                                                'RB_radius_list': [2,10,50],
                                                                'gf3_sigma_list': [4,25,50],
                                                                'opt_bounding_box': {'use_bounding_box': False,
                                                                                     'y_limits_bbox': [0,500],
                                                                                     'x_limits_bbox': [0,500] },
                                                                'fit_step': 10},
                                       'decharger_type': 'local_GF2RBGF',
                                       'GF2RBGF_setting': {'gf1_sigma': 80,
                                                           'gf2_sigma': 80,
                                                           'RB_radius': 2,
                                                           'gf3_sigma': 4,
                                                           'local_setting':{'A_threshold': 50,
                                                                            'color_shift': 0.1,
                                                                            'n_px_border': 10}},
                                       'inverse': False}
    _guipi_dictionary = {'auto_optimize': GuiPI(bool),
                         'optimization_setting': {'dilation_iterations': GuiPI(int,min=1),
                                                  'N_regions_for_opt': GuiPI(int,min=1),
                                                  'gf1_sigma_list': GuiPI(list),
                                                  'color_shift_list': GuiPI(list),
                                                  'gf2_sigma_list': GuiPI(list),
                                                  'RB_radius_list': GuiPI(list),
                                                  'gf3_sigma_list': GuiPI(list),
                                                  'opt_bounding_box': {'use_bounding_box': GuiPI(bool),
                                                                       'y_limits_bbox': GuiPI(list),
                                                                       'x_limits_bbox': GuiPI(list) },
                                                  'fit_step': GuiPI(int,min=1)
                                                  },
                         'decharger_type': GuiPI('options',options=['local_GF2RBGF','global_GF2RBGF']),
                         'GF2RBGF_setting': {'gf1_sigma': GuiPI(float,min=0),
                                             'gf2_sigma': GuiPI(float,min=0),
                                             'RB_radius': GuiPI(int,min=1),
                                             'gf3_sigma': GuiPI(float,min=0),
                                             'local_setting':{'A_threshold': GuiPI(int,min=1),
                                                              'color_shift': GuiPI(float,min=0,max=1),
                                                              'n_px_border': GuiPI(int,min=1)}},
                         'inverse': GuiPI(bool)}
    def __init__(self,transformation_dictionary,force_serial=False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'auto_optimize': (bool) if True the plugin  start an optimization routine according to all the specs
            contained in the 'optimization_setting' field.

            'optimization_setting': (dict) Dictionary containing the setting optimization routine. The dictionary has to
            be specified as below:

                {'dilation_iterations': (int) number of dilation done to correction mask in order define the region in
                which charging is not present but the histogram is still comparable with the one obtained from the
                region in which charging is present.

                'N_regions_for_opt': (int) maximum number of regions considered in a correction mask for the loss
                computation.

                'gf1_sigma_list': (list of floats) list of possible values of the 'gf1_sigma' parameter tested during
                the optimization.

                'color_shift_list': (list of floats in between 0 and 1) list of possible values of the 'color_shift'
                parameter tested during the optimization.

                'gf2_sigma_list': (list of floats) list of possible values of the 'gf2_sigma' parameter tested during
                the optimization.

                'RB_radius_list': (list of ints) list of possible values of the 'RB_radius' parameter tested during the
                optimization.

                'gf3_sigma_list': (list of floats) list of possible values of the 'gf3_sigma' parameter tested during
                the optimization.

                'opt_bounding_box': (dict) dictionary containing the setting of the bounding box used during the
                optimization. The bounding box defines the part of the stack (in the YX plane) which is considered by
                the optimization routine. It has to be specified as below:

                    {'use_bounding_box' : (bool) if True the bounding box is used, otherwise the whole YX plane is used.
                    In this last case the two arguments below are ignored.

                    'y_limits_bbox': (list) list specifying the extrema along the Y-direction (i.e. axis 0). This list
                    can contain numpy-like instruction for the definition of the range. The following examples should
                    clarify the usage. Let arr be a numpy array

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

                'fit_step':(int) interval between two slices of the stack that are used during the optimization. If 1
                all the stack is used, for n>1 only the slices having a distance of n on the 0-axis (i.e. the
                z-direction). This parameter therefore determine the number of slices used during the optimization,
                which is equal to (image_size_z)//n.

                }

            'decharger_type': (str) name of the decharging method applied to the images. The available decharger are:

                1. 'local_GF2RBGF' = the decharger first try to estimate the regions in each slice where the charging is
                present, by using a down-hill filter, and then correct the distortion locally. The correction is
                performed by subtracting an estimated increase of the brightness due to the charging in all the regions.
                This kind of correction method, try to correct the less is possible, but it may be slow.

                2. 'global_GF2RBGF' = like the 'local_GF2RBGF' but the correction algorithm is applied to the whole
                image skipping the step in which the regions in which charging is present are estimated. It is typically
                faster than the 'local_GF2RBGF', but it changes more the whole image.

            'GF2RBGF_setting': (dict) Setting of the GF2RBGF method. This field is ignored for the 'local_GF2RBGF' if
            'auto_optimize' is True. It has to be specified as below:

                {'gf1_sigma': (float) sigma of the first gaussian filter which flatten the slice.

                'gf2_sigma': (float,optional) sigma of the second gaussian filter, which should be used if the image is
                not sufficiently flat.

                'RB_radius': (int) radius parameter of the rolling ball algorithm used to estimate the charging related
                increase in brightness.

                'gf3_sigma': (float) sigma of the gaussian filter to smooth the estimated charging related increase in
                brightness, since after the rolling ball algorithm the estimated background is typically to 'regular'.

                'local_setting': (dict) dictionary containing the setting of the charge artifact finder used by the
                'local_GF2RBGF' method. It is ignored if other decharger correction methods are chosen in the
                'decharger_type' field of this dictionary. This dictionary have to be specified as follow:

                    {'A_threshold': (int) threshold on the area (in pixel) used to disregard some the estimated charged
                    region: all the regions having area in pixel below this threshold are not corrected.

                    'color_shift': (float between 0 and 1) shift in the grey-level values used by the down-hill filter
                    to identify the charged regions. Typically this value is low.

                    'n_px_border': (int) number of pixels used to smoothly pass from the regions corrected, to the
                    regions that are not. This is done to avoid a too drastic difference between the corrected and
                    not-corrected regions.

                    }

                },

            'inverse': (bool) If True the decharger is applied to corrected the 'inverse-charging artifact', namely
            when charged regions are shifted towards low-brightness, rather than high-brightness (as it happens for
            normal charging). The default value is False.

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        :param force_serial: (bool) if True serial behavior is forced for this plugin independently on the global
        setting of bmiptools.
        """
        super(Decharger,self).__init__()
        self.available_decharger = ['global_GF2RBGF','local_GF2RBGF']
        self.force_serial = force_serial

        self.auto_optimize = transformation_dictionary['auto_optimize']
        if self.auto_optimize:

            self.dilation_iterations = transformation_dictionary['optimization_setting']['dilation_iterations']
            self.N_regions_for_opt = transformation_dictionary['optimization_setting']['N_regions_for_opt']
            self.gf1_sigma_list = transformation_dictionary['optimization_setting']['gf1_sigma_list']
            self.color_shift_list = transformation_dictionary['optimization_setting']['color_shift_list']
            self.gf2_sigma_list = transformation_dictionary['optimization_setting']['gf2_sigma_list']
            self.RB_radius_list = transformation_dictionary['optimization_setting']['RB_radius_list']
            self.gf3_sigma_list = transformation_dictionary['optimization_setting']['gf3_sigma_list']

            self.use_bounding_box = \
                transformation_dictionary['optimization_setting']['opt_bounding_box']['use_bounding_box']
            if self.use_bounding_box:

                self.y_limits_bbox = \
                    transformation_dictionary['optimization_setting']['opt_bounding_box']['y_limits_bbox']
                self.x_limits_bbox = \
                    transformation_dictionary['optimization_setting']['opt_bounding_box']['x_limits_bbox']

            self.fit_step = transformation_dictionary['optimization_setting']['fit_step']
            self.decharger_type = 'local_GF2RBGF'

        else:

            self.decharger_type = transformation_dictionary['decharger_type']

        if 'GF2RBGF' in self.decharger_type:

            self.gf1_sigma = transformation_dictionary['GF2RBGF_setting']['gf1_sigma']
            self.gf2_sigma = transformation_dictionary['GF2RBGF_setting']['gf2_sigma']
            self.RB_radius = transformation_dictionary['GF2RBGF_setting']['RB_radius']
            self.gf3_sigma = transformation_dictionary['GF2RBGF_setting']['gf3_sigma']
            if 'local' in self.decharger_type:

                self.A_threshold = transformation_dictionary['GF2RBGF_setting']['local_setting']['A_threshold']
                self.color_shift = transformation_dictionary['GF2RBGF_setting']['local_setting']['color_shift']
                self.n_px_border = transformation_dictionary['GF2RBGF_setting']['local_setting']['n_px_border']

        self.inverse = transformation_dictionary['inverse']
        self._setup()

    def _setup(self):

        if self.auto_optimize:

            self.parameter_space,_ = generate_parameter_space({'gf1_sigma': self.gf1_sigma_list,
                                                               'color_shift': self.color_shift_list,
                                                               'gf2_sigma': self.gf2_sigma_list,
                                                               'RB_radius': self.RB_radius_list,
                                                               'gf3_sigma': self.gf3_sigma_list})
            if not self.use_bounding_box:

                self.y_limits_bbox = [None,None]
                self.x_limits_bbox = [None,None]

    @staticmethod
    def _get_loss_optimization_mask_pairs(cmask, dilation_iteration=10, N_charged_regions_for_optimization=20):
        """
        Compute the pairs charged region / uncharged region pairs needed for the computation of the Decharger loss.

        :param cmask: (np.array) mask with all the estimated charged regions
        :param dilation_iteration: (int) umber of dilation done to correction mask in order define the region in which
                                   charging is not present but the histogram is still comparable with the one obtained
                                   from the region in  which charging is present.
        :param N_charged_regions_for_optimization: (int) maximum number of regions considered in a correction mask for
                                                   the loss computation. The region selected are the one with the
                                                   biggest areas.
        :return: (list of np.array) list of couples of masks for the charged region and its surrounding uncharged region.
        """
        labeled_cmask, Nlabels = label(cmask, return_num=True)
        prop_cmask = regionprops(labeled_cmask)
        area_label_pair = [[item.area, item.label] for item in prop_cmask]
        sorted_area_label_pair = sorted(area_label_pair, reverse=True)
        masks_pairs = []
        for _, l in sorted_area_label_pair[:N_charged_regions_for_optimization]:

            sel_cmask = (labeled_cmask == l).astype(np.int8)
            s1 = binary_dilation(sel_cmask, iterations=dilation_iteration).astype(np.int8)
            s2 = binary_dilation(s1, iterations=2 * dilation_iteration).astype(np.int8)
            sel_gmask = s2 - s1
            sel_gmask = ((sel_gmask-binary_dilation(cmask,
                                                    iterations=dilation_iteration).astype(np.int8))>0).astype(np.int8)
            masks_pairs.append((sel_cmask, sel_gmask))

        return masks_pairs

    @staticmethod
    def _li(p, q):
        """
        l1 distance between p and q
        """

        return np.sum(np.abs(p / np.sum(p) - q / np.sum(q)))

    def _compute_loss(self,sl, mask_pairs):
        """
        Compute the loss function for the decharger

        :param sl: (np.array) slice on which the loss is evaluated.
        :param mask_pairs: (list of np.arrays) masks of the charged/uncharged region pairs used to compute the loss.
        :return: (float) the losss value.
        """
        sl_norm = (sl - sl.min()) / (sl.max() - sl.min())*256
        loss = 0
        for m_c, m_b in mask_pairs:

            val_c = sl_norm.flatten()[m_c.flatten() == 1]
            h_c, _ = np.histogram(val_c,bins=256,range=(0,256),density=True)
            val_b = sl_norm.flatten()[m_b.flatten() == 1]
            h_b, _ = np.histogram(val_b,bins=256,range=(0,256),density=True)
            loss += self._li(h_c, h_b)

        return loss / len(mask_pairs)

    def fit(self,x,*args,**kwargs):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        self.fit_enable = False
        self.write('Decharger optimization routine')
        self.write('----------------------------')
        self.write('Optimization method: grid search')
        self.write('Number of parameter combination checked: {}'.format(len(self.parameter_space)))

        x_for_optimization = x.data[::self.fit_step,
                                    self.y_limits_bbox[0]:self.y_limits_bbox[1],
                                    self.x_limits_bbox[0]:self.x_limits_bbox[1]]
        global_loss = 0
        for z in range(len(x_for_optimization)):

            sl = x_for_optimization[z,...]
            z_loss = []
            for n, p in enumerate(self.parameter_space):

                self.progress_bar(n, len(self.parameter_space),15,
                                  text_after=' | parameter combination {}/{}'.format(n + 1, len(self.parameter_space)))

                gf1_sigma = p[0]
                color_shif = p[1]
                gf2_sigma = p[2]
                RB_radius = p[3]
                gf3_sigma = p[4]

                cmask, flat_slice, LFslice = self._find_charging(sl,gf1_sigma,color_shif,self.inverse)
                if np.sum(cmask) != 0:

                    mask_pairs = self._get_loss_optimization_mask_pairs(cmask,dilation_iteration=self.dilation_iterations,
                                                               N_charged_regions_for_optimization=self.N_regions_for_opt)
                    corrected_slice = self._correct_charging(flat_slice,cmask,LFslice,gf2_sigma,RB_radius,gf3_sigma)
                    z_loss.append( self._compute_loss(corrected_slice,mask_pairs) )

                else:

                    z_loss.append( np.inf )

            global_loss += np.array(z_loss)

        global_loss = global_loss/len(x_for_optimization)
        if np.prod(np.isinf(global_loss)):

            self.write('Not able to find the best parameters: default parameters for global algorithm used instead.')
            self.gf1_sigma = self.empty_transformation_dictionary['GF2RBGF_setting']['gf1_sigma']
            self.gf2_sigma = self.empty_transformation_dictionary['GF2RBGF_setting']['gf2_sigma']
            self.RB_radius = self.empty_transformation_dictionary['GF2RBGF_setting']['RB_radius']
            self.gf3_sigma = self.empty_transformation_dictionary['GF2RBGF_setting']['gf3_sigma']
            self.decharger_type = 'global_GF2RBGF'

        else:

            self.write('Best parameters found!')
            best_parameters = self.parameter_space[np.argmin(global_loss)]
            self.gf1_sigma = best_parameters[0]
            self.color_shift = best_parameters[1]
            self.gf2_sigma = best_parameters[2]
            self.RB_radius = best_parameters[3]
            self.gf3_sigma = best_parameters[4]

        self.write('----------------------------')

    def _global_GF2RBGF(self,x):
        """
        Global_GF2RBGF methods for the charging correction/reduction.

        :param x: (np.array) 2d slice to correct
        :return: (np.array) corrected slice
        """
        LFx = gaussian_filter2d(x,self.gf1_sigma)
        flattened_x = x-LFx
        LFflattened_x = gaussian_filter2d(flattened_x,self.gf2_sigma)
        flattened_x2 = flattened_x-LFflattened_x
        if self.inverse:

            bkg_corr = rolling_ball(flattened_x2,radius=self.RB_radius)
            decharged = x-np.minimum(0,gaussian_filter2d(bkg_corr,self.gf3_sigma))

        else:

            bkg_corr = rolling_ball(1-flattened_x2,radius=self.RB_radius)
            decharged = x+np.minimum(0,gaussian_filter2d(bkg_corr,self.gf3_sigma))

        return decharged

    def _find_charging(self,x,gf1_sigma,color_shift,inverse):
        """
        Function used to estimate the regions o the image where charging is present. It is based on a down-hill filter
        followed by a threshold operator.

        :param x: (np.array) slice to correct, in which charging is estimated.
        :param gf1_sigma: (float) sigma of the first gaussian filter.
        :param color_shift: (float in [0,1]) shift used in the downhill filter for the estimation of the charged
                             regions.
        :param inverse: (bool) if True the charged region is estimated from the inverse image.
        :return: (np.array) correction mask, (np.array) flattened image, (np.array) Low-Frequency image used to invert
                 flattening.
        """
        LFx = gaussian_filter2d(x,gf1_sigma)
        flattened_x = x-LFx
        if inverse:

            xt = 1-flattened_x

        else:

            xt = flattened_x

        seed = np.copy(xt-color_shift)
        seed[1:-1,1:-1] = xt.min()
        mask = xt
        filled = reconstruction(seed,mask,method='dilation')
        candidate_mask = (xt-filled)>color_shift
        candidate_mask = binary_fill_holes(candidate_mask)
        labeled_parts = label(candidate_mask)
        props = regionprops(labeled_parts)
        fmask = np.zeros(candidate_mask.shape)
        if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                and not self.force_serial:

            def func_to_par(p,fmask):

                if p.area > self.A_threshold:

                    fmask += (labeled_parts == p.label).astype(np.uint8)

                return fmask

            Parallel(n_jobs=self._n_available_cpu,require='sharedmem')(delayed(func_to_par)(p,fmask) for p in props)

        else:

            for p in props:

                if p.area>self.A_threshold:

                    fmask += (labeled_parts == p.label).astype(np.uint8)

        return fmask,flattened_x,LFx

    def _correct_charging(self,flattened_x,correction_mask,LFx,gf2_sigma,RB_radius,gf3_sigma):
        """
        Function applying the charging correction from the results obtained from the function '_find_charging'.

        :param flattened_x: (np.array) flattened slice.
        :param correction_mask: (np.array) binary mask containing the regions to correct.
        :param LFx: (np.array) low-frequency image used to invert the flattening.
        :param gf2_sigma: (float) sigma of the second gaussian filter.
        :param RB_radius: (int) radius parameter of the rolling ball algorithm used for the background estimation.
        :param gf3_sigma: (float) sigma of the gaussian filter used to estimate the correction mask.
        :return: (np.array) corrected slice.
        """
        # define corrections zone
        dilations = [correction_mask]
        for i in range(self.n_px_border):

            dilations.append(binary_dilation(dilations[-1],iterations=1).astype(np.uint8))

        borders = []
        for i in range(self.n_px_border,0,-1):

            lmbda = (self.n_px_border-i)/(self.n_px_border+1)
            borders.append(lmbda*(dilations[i]-dilations[i-1]).astype(np.float32))

        borders = np.array(borders)
        border_region = dilations[-1]-correction_mask
        increasing_borders = borders.sum(0)
        decreasing_borders = (1-borders.sum(0))*border_region

        # corrector
        if gf2_sigma> 0:

            LFflattened_x = gaussian_filter2d(flattened_x,gf2_sigma)

        else:

            LFflattened_x = 0

        bkg_corr = rolling_ball(flattened_x - LFflattened_x,radius=RB_radius)
        gf_bkg_corr = gaussian_filter2d(bkg_corr,gf3_sigma)
        decharged_x = flattened_x*(1-border_region+decreasing_borders-correction_mask) + \
                      (flattened_x-gf_bkg_corr)*(correction_mask+increasing_borders)

        return decharged_x+LFx

    def _local_GF2RBGF(self,x,return_correction_mask=False):
        """
        Local_GF2RBGF methods for the charging correction/reduction.

        :param x: (np.array) the slice to correct.
        :param return_correction_mask: (bool) if True also the correction mask is returned.
        :return: (np.array) the corrected slice.
        """
        # 0/1 standardize
        M = x.max()
        m = x.min()
        stand_x = standardizer(x,'0/1')

        # identify and correct
        correction_mask,flattened_x,LFx = self._find_charging(stand_x,self.gf1_sigma,self.color_shift,self.inverse)
        decharged_x = \
            self._correct_charging(flattened_x,correction_mask,LFx,self.gf2_sigma,self.RB_radius,self.gf3_sigma)

        # destandardize
        decharged_x = (M-m)*decharged_x+m
        if return_correction_mask:

            return decharged_x,correction_mask

        return decharged_x

    def _select_decharger(self):
        """
        Utility function, select the decharger to use based on the plugin setting.
        """
        if self.decharger_type == 'global_GF2RBGF':

            return self._global_GF2RBGF

        elif self.decharger_type == 'local_GF2RBGF':

            return self._local_GF2RBGF

        else:

            self.write('Error: unrecognized decharger. The available decharger are listed '
                       'below \n{}'.format(self.available_decharger))

    def transform(self,x,inplace=True,*args,**kwargs):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if self.fit_enable and self.auto_optimize:

            self.fit(x)

        decharger = self._select_decharger()
        if x.n_channels > 1:

            x_transformed = []
            for C in range(x.n_channels):

                x_transformed_C = []
                for z in range(x.n_slices):

                    x_transformed_C.append(decharger(x.data[z,:,:,C]))

                x_transformed.append(np.array(x_transformed_C))

            if not inplace:

                return np.array(x_transformed).traspose((1,2,3,0))

            x.from_array(np.array(x_transformed).traspose((1,2,3,0)))

        else:

            x_transformed = []
            for z in range(x.n_slices):

                x_transformed.append(decharger(x.data[z,...]))

            if not inplace:

                return np.array(x_transformed)

            x.from_array(np.array(x_transformed))