=====================================
Case of study: decharger optimization
=====================================


Here the optimization routine for the *local GF2RBGF algorithm* of the decharger plugin is briefly discussed with a
practical example. In the :ref:`Implementation details <decharger_implementation_details>` section of the Decharger
plugin was discussed how the local GF2RBGF algorithm works, and how it can be optimized.

.. note::

    The following imports are needed to run the code snapshots below.

    .. code-block::


        import numpy as np
        import psutil as psu

        from joblib import Parallel,delayed
        from scipy.ndimage.morphology import binary_dilation,binary_fill_holes
        from skimage.morphology import reconstruction
        from skimage.restoration import rolling_ball
        from skimage.measure import label,regionprops

        from bmiptools.transformation.basic.filters import gaussian_filter2d
        from bmiptools.transformation.restoration._restoration_shared import generate_parameter_space


As explained in the  :ref:`Implementation details <decharger_implementation_details>` section of the Decharger
plugin, the local GF2RBGF consist essentially in two steps: first identification of the regions containing the charging
artifact, then correct the image in this region by subtracting an estimated charging contribution. The function
below implement the first step, produce correction mask :math:`M(j,i)` plus other data useful for the next correction
step.


.. code-block::


    def find_charging(x, gf1_sigma, color_shift, inverse,A_threshold=50,n_available_cpu=psu.cpu_count()):
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
        LFx = gaussian_filter2d(x, gf1_sigma)
        flattened_x = x - LFx
        if inverse:

            xt = 1 - flattened_x

        else:

            xt = flattened_x

        seed = np.copy(xt - color_shift)
        seed[1:-1, 1:-1] = xt.min()
        mask = xt
        filled = reconstruction(seed, mask, method='dilation')
        candidate_mask = (xt - filled) > color_shift
        candidate_mask = binary_fill_holes(candidate_mask)
        labeled_parts = label(candidate_mask)
        props = regionprops(labeled_parts)
        fmask = np.zeros(candidate_mask.shape)

        def func_to_par(p, fmask):

            if p.area > A_threshold:

                fmask += (labeled_parts == p.label).astype(np.uint8)

            return fmask

        Parallel(n_jobs=n_available_cpu, require='sharedmem')(delayed(func_to_par)(p, fmask) for p in props)
        return fmask, flattened_x, LFx


The final decharged image for the local GF2RBGF :math:`I_{decharged}(j,i)` is produced by the function below.


.. code-block::


    def correct_charging(flattened_x,correction_mask,LFx,gf2_sigma,RB_radius,gf3_sigma,n_px_border=10):
        """
        Function applying the charging correction from the results obtained from the function '_find_charging'.

        :param flattened_x: (np.array) flattened slice.
        :param correction_mask: (np.array) binary mask containing the regions to correct.
        :param LFx: (np.array) low-frequency image used to invert the flattening.
        :param gf2_sigma: (float) sigma of the second gaussian filter.
        :param RB_radius: (int) radius parameter of the rolling ball algorithm used for the background estimation.
        :param gf3_sigma: (float) sigma of the gaussian filter used to estimate the correction mask.
        :param n_px_border: (int) number of pixel at the border used to fade the correction away in the input slice.
        :return: (np.array) corrected slice.
        """
        # define corrections zone
        dilations = [correction_mask]
        for i in range(n_px_border):

            dilations.append(binary_dilation(dilations[-1],iterations=1).astype(np.uint8))

        borders = []
        for i in range(n_px_border,0,-1):

            lmbda = (n_px_border-i)/(n_px_border+1)
            borders.append(lmbda*(dilations[i]-dilations[i-1]).astype(np.float32))

        borders = np.array(borders)
        border_region = dilations[-1]-correction_mask
        increasing_borders = borders.sum(0)
        decreasing_borders = (1-borders.sum(0))*border_region

        # corrector
        if gf2_sigma > 0:

            LFflattened_x = gaussian_filter2d(flattened_x,gf2_sigma)

        else:

            LFflattened_x = 0

        bkg_corr = rolling_ball(flattened_x - LFflattened_x,radius=RB_radius)
        gf_bkg_corr = gaussian_filter2d(bkg_corr,gf3_sigma)
        decharged_x = flattened_x*(1-border_region+decreasing_borders-correction_mask) + \
                      (flattened_x-gf_bkg_corr)*(correction_mask+increasing_borders)

        return decharged_x+LFx


The full local GF2RBGF algorithm consist practically in the application in sequence of the two functions presented
above. A standardization/destandardization step is added to make the algorithm more robust to variations in the
dynamics of the input image.


.. code-block::


    def local_GF2RBGF(x,param):
        """
        Local_GF2RBGF methods for the charging correction/reduction.

        :param x: (np.array) the slice to correct.
        :param param: (tuple) tuple containing all the algorithm parameter.
        :return: (np.array) decharged slice.
        """

        #get parameters
        gf1_sigma, color_shift, gf2_sigma, RB_radius, gf3_sigma, inverse = param

        # 0/1 standardize
        M = x.max()
        m = x.min()
        stand_x = standardizer(x,'0/1')

        # identify and correct
        correction_mask,flattened_x,LFx = find_charging(stand_x,gf1_sigma,color_shift,inverse)
        decharged_x = correct_charging(flattened_x,correction_mask,LFx,gf2_sigma,RB_radius,gf3_sigma)

        # destandardize
        decharged_x = (M-m)*decharged_x+m

        return decharged_x

The three functions described here, are very close to the corresponding one are present in the :py:class:`Decharger
<bmiptools.transformation.restoration.decharger.Decharger>` class.


The optimization routine
========================


The parameter space used for the optimization routine is defined as follow


* the :math:`\sigma_{GF1}` and :math:`\sigma_{GF2}` parameter are tested for 3 possible values: 40, 80, and 120;

* the values of :math:`c_{shift}` tested are 0.05, 0.1, and 0.2;

* the rolling ball radius :math:`r` is tested for a value of 2, 10, and 50;

* the :math:`\sigma_{GF3}` parameter is tested for 3 possible values: 4, 25, and 50.


In total the number of possible combinations tested are 243. To generate the parameter space from these setting one can
use the function :py:func:`generate_parameter_space <bmiptools.transformation.restoration._restoration_shared.generate_parameter_space>`.


.. code-block::


    from bmiptools.transformation.restoration._restoration_shared import generate_parameter_space

    # define parameter space boundaries
    gf1_sigma_range = [40,80,120]
    color_shift_range = [0.05,0.1,0.2]
    gf2_sigma_range = [40,80,120]
    RB_radius_range = [2,10,50]
    gf3_sigma_range = [4,25,50]

    # generate parameter space
    parameter_space,_ = generate_parameter_space({'gf1_sigma': gf1_sigma_range,
                                                  'color_shift': color_shift_range,
                                                  'gf2_sigma': gf2_sigma_range,
                                                  'RB_radius': RB_radius_range,
                                                  'gf3_sigma': gf3_sigma_range,
                                                  'inverse': [True]})
    print('Total number of parameters combination: ',len(parameter_space))

.. note::

   The example used here is a case of inverse charging: the shift in brightness is towards lower brightness level
   rather than the opposite, as in the usual charging. That is way the parameter space contains also the ``inverse``
   parameter which is always ``True``.


According to the optimization procedure presented in the :ref:`Implementation details
<decharger_implementation_details>` section of this plugin, pairs of charged-decharged regions :math:`(Q,Q^s)` used in
to compute the loss, can be obtained using the function below.


.. code-block::


    def get_loss_optimization_mask_pairs(cmask, dilation_iteration=10, N_charged_regions_for_optimization=20):
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


Given the pairs :math:`(Q,Q^s)`, the loss
:math:`\mathcal{L}[c_{shift},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}](I,Q,Q^s)` is computed with the function below.


.. code-block::


    def l1(p, q):
        """
        l1 distance between normalized p and q.
        """

        return np.sum(np.abs(p / np.sum(p) - q / np.sum(q)))

    def compute_loss(sl, mask_pairs):
        """
        Compute the loss function for the decharger.

        :param sl: (np.array) slice on which the loss is evaluated.
        :param mask_pairs: (list of np.arrays) masks of the charged/uncharged region pairs used to compute the loss.
        :return: (float) the loss value.
        """
        sl_norm = (sl - sl.min()) / (sl.max() - sl.min()) * 256
        loss = 0
        for m_c, m_b in mask_pairs:

            val_c = sl_norm.flatten()[m_c.flatten() == 1]
            h_c, _ = np.histogram(val_c, bins=256, range=(0, 256), density=True)
            val_b = sl_norm.flatten()[m_b.flatten() == 1]
            h_b, _ = np.histogram(val_b, bins=256, range=(0, 256), density=True)
            loss += l1(h_c, h_b)

        return loss / len(mask_pairs)


Assuming to apply the optimization routine on the slice ``sl`` of some stack. The code below should be used to compute
the loss function for each parameter combination.


.. code-block::

    sl = ...     # slice used for the decharger optimization routine

    # compute the loss
    loss = []
    for p in parameter_space:

        # get parameter combination
        gf1_sigma, color_shift, gf2_sigma, RB_radius, gf3_sigma,inverse = p

        # estimate correction mask
        cmask, flat_slice, LFslice = find_charging(sl, gf1_sigma, color_shift, inverse)

        # correct slice and compute the loss value
        if np.sum(cmask) != 0:

            mask_pairs = get_loss_optimization_mask_pairs(cmask)
            corrected_slice = correct_charging(flat_slice, cmask, LFslice, gf2_sigma, RB_radius, gf3_sigma)
            l = compute_loss(corrected_slice, mask_pairs)
            loss.append(l)

        else:

            loss.append(np.inf)


Clearly, the best parameters are the one corresponding to the lowest value of the loss.


.. code-block::

    # print best parameters
    best_idx = np.argmin(loss)
    print('Best parameter combinations: ',parameter_space[best_idx])
    print('Loss = {}'.format(loss[best_idx]))


The optimization routine described here, contains all the essential steps which are present in the :py:class:`Decharger
<bmiptools.transformation.restoration.decharger.Decharger>` class.


Results
=======


Consider the image below as input for the algorithm. The inverse charging artifacts are clearly visible in the upper
half of the image.


.. image:: ../_images/Miscellaneous/decharger_optimization/original.png
   :class: align-center
   :width: 700px
   :height: 700px
   :scale: 42

The loss value for all the 243 combinations is showed in the graph below.


.. image:: ../_images/Miscellaneous/decharger_optimization/loss_values.png
   :class: align-center
   :width: 1923px
   :height: 1015px
   :scale: 40


Being not completely clear how the loss function look like, it can be useful to zoom around the global minimum of the
loss, as showed in the graph below.


.. image:: ../_images/Miscellaneous/decharger_optimization/loss_values_zoom.png
   :class: align-center
   :width: 1923px
   :height: 1015px
   :scale: 40


The best parameter combination corresponds to the loss value
:math:`\mathcal{L}[c_{shift},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}] = 0.5344`, which gives the visual result
below.


.. |fig-1| image:: ../_images/Miscellaneous/decharger_optimization/original.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig0| image:: ../_images/Miscellaneous/decharger_optimization/global_minimum.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig-1| |fig0|


Clearly, different values of the loss correspond to different level of decharging. The animation below show how the
filter quality changes in different points of the loss, confirming empirically that the loss function used is able
to capture the idea of image wit less level of (inverse, in this case) charging .


.. image:: ../_images/Miscellaneous/decharger_optimization/animation.gif
   :class: align-center
   :width: 706px
   :height: 841px
   :scale: 80


To give a closer look at the different visual results, the different images showed above compared with the one
obtained with the best parameter combination are available below.


**Global minimum vs Local minimum**

On the right, one can see the result produced with the parameter combination corresponding to a local minimum of
the loss (:math:`\mathcal{L}[c_{shift},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}] = 0.6950`).


.. |fig1| image:: ../_images/Miscellaneous/decharger_optimization/global_minimum.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig2| image:: ../_images/Miscellaneous/decharger_optimization/local_minimum.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig1| |fig2|


There is not much difference between the one corresponding to the global and local minimum.


**Global minimum vs Away from minimum**

On the right, one can see the result produced with the parameter combination corresponding to a value in between a
local maximum and the global minimum of the loss
(:math:`\mathcal{L}[c_{shift},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}] = 1.4365`).


.. |fig5| image:: ../_images/Miscellaneous/decharger_optimization/global_minimum.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig6| image:: ../_images/Miscellaneous/decharger_optimization/away_global_minimum.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig5| |fig6|


**Global minimum vs Local maximum**

On the right, one can see the result produced with the parameter combination corresponding to a local maximum of
the loss (:math:`\mathcal{L}[c_{shift},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}] = 1.9672`)


.. |fig3| image:: ../_images/Miscellaneous/decharger_optimization/global_minimum.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig4| image:: ../_images/Miscellaneous/decharger_optimization/local_maximum.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig3| |fig4|


Being completely far away from the global minimum, the charging artifact is practically left unchanged.



.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Miscellaneous/decharger_optimization>`_. To reproduce the images showed
   above one may consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/
   tree/master/examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can
   find all the necessary input data.


