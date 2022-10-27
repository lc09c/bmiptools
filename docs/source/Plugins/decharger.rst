=========
Decharger
=========


.. admonition:: Dechargere in a nutshell.
   :class: note

   1. Plugin to reduce the charging artefacts in a stack;
   2. This plugin is multichannel;
   3. When ``local_GF2RBGF`` is used as decharging method, this plugin can be optimized on the stack.
   4. Python API reference: :py:class:`bmiptools.transformation.restoration.decharger.Decharger`.



This plugin can be used to reduce the charging artifact, typical of Cryo FIB-SEM images. Two methods are
available to reduce the charging artifact:

* *local GF2RBGF*: where the decharger first try to estimate the regions in each slice where the charging is
  present, by using a down-hill filter, and then correct the distortion locally. The correction is performed by
  subtracting an estimated increase of the brightness due to the charging in all the regions. This kind of correction
  method, try to correct the less is possible, but it may be slow.

* *global GF2RBGF*: which is like the local GF2RBGF but the correction algorithm is applied to the whole image
  skipping the step in which the regions in which charging is present are estimated. It is typically faster than the
  local one, but it changes more the whole image.

The charging can be both the "normal" one, where the brightness is increased locally, or the "inverse" one, where the
brightness is instead decreased.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.restoration.decharger.Decharger`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.

.. code-block::

   {'auto_optimize': True,
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



The optimization-related plugin-specific parameters contained in the ``optimization_setting`` field of this dictionary
are:


* ``dilation_iteration``: is the number of dilation done to correction mask in order define the region in which charging
  is not present but the histogram is still comparable with the one obtained from the region in which charging is
  present.

* ``N_regions_for_opt``:  is the maximum number of regions considered in a correction mask for the loss computation.

* ``gf1_sigma_list``: is the list containing the of possible values of the 'gf1_sigma' parameter tested during the
  optimization.

* ``color_shift_list``: is the list of possible values of the 'color_shift' parameter tested during the optimization.

* ``gf2_sigma_list``: is the list of possible values of the 'gf2_sigma' parameter tested during the optimization.

* ``RB_radius_list``: is the list of possible values of the 'RB_radius' parameter tested during the optimization.

* ``gf3_sigma_list``: is the list of possible values of the 'gf3_sigma' parameter tested during the optimization.


The plugin-specific parameters contained in this dictionary are:

* ``decharger_type``: contain name of the decharging method applied to the images. The available decharger are:

  * ``local_GF2RBGF``,
  * ``global_GF2RBGF``.

* ``GF2RBGF_setting``: is a dictionary containing the setting of the GF2RBGF method. This field is ignored when
  ``decharger_type = 'local_GF2RBGF'`` and ``auto_optimize = True``. It contains the keys below:

  * ``gf1_sigma``, which is the standard deviation of the first gaussian filter which flatten the slice.

  * ``gf2_sigma``: which is the standard deviation of the second gaussian filter, which should be used if the image is
    not sufficiently flat.

  * ``RB_radius``, which is the radius parameter of the rolling ball algorithm used to estimate the charging related
    increase in brightness.

  * ``gf3_sigma`` which is the standard deviation of the gaussian filter to smooth the estimated charging related
    increase in brightness, since after the rolling ball algorithm the estimated background is typically to 'regular'.

  * ``local_setting``, containing a dictionary with the decharger setting used by the ``'local_GF2RBGF'`` method. It is
    ignored if the global decharger type is specified in the ``decharger_type`` field. This dictionary has the following
    fields:

    * ``A_threshold``, which is a threshold on the area (expressed in pixel), used to disregard all the estimated
      charged regions that are too small. All the regions having area in pixel below this threshold are not corrected.

    * ``color_shift``, which is  number between 0 and 1 indicating the shift in the grey-level values used by the
      down-hill filter to identify the charged regions. Typically this value is small.

    * ``n_px_border``, which is the number of pixels used to smoothly pass from the regions corrected, to the regions
      that are not. This is done to avoid a too drastic difference between the corrected and not-corrected regions.

* ``inverse``:  when ``True`` the decharger is applied to corrected the 'inverse-charging artifact', namely
  when charged regions are shifted towards low-brightness, rather than high-brightness (as it happens for normal
  charging). The default value is ``False``.


When ``auto-optimize = True`` the plugin-specific parameters above are ignored, since the one selected by the
optimization procedure are used. Finally, the meaning of the remaining parameters can be found in
:ref:`General information#Transfomation dictionary <transformation_dictionary>`.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Decharger <bmiptools.transformation.restoration.decharger.Decharger>`.


Use case
========


The typical use of this plugin are:


1. Reduce the amount of charging artifacts in the input stack.

.. tip::

  The following things turn out to be useful, from a practical point of view.

  1. Even when the ``local_GF2RBGF`` decharger is used, the ``A_threshold`` parameter does not have an optimization
     procedure. By the way, by keeping it constant to a reasonable value (``A_threshold = 50``, for instance) gives good
     results for different input stacks.

  .. _decharger_position_in_pipeline:

  2. The decharger plugin should be applied to images having sufficiently smooth background. The background should not
     necessarily need to be flat, but a smooth variation of it is assumed in the plugin. To have a rough idea of what
     can be considered smooth variation, the following criteria can be applied. Consider the typical dimension of the
     chargerd regions in an image, if another artifacts have comparable dimension, the background cannot be considered
     smooth for the application of the decharger. As such, in images with striping artifacts, it is recommended to
     remove this artifact (e.g. by applying the :doc:`destriper` plugin) *before* the application of this plugin. On the
     other hand, the image noise should not disturb the application of a plugin, since it typically involves at most few
     pixels (if noise is pixelwise correlated) and decharger is insensitive to such a small variations. Therefore there
     is no need to apply a denoiser before the application of this plugin (but of course it can be done if needed).


Application example
===================


As example consider the slice of a stack of a biological sample obtained via FIB-SEM, where the charging artifact is
present. According to the :ref:`tip 2 <decharger_position_in_pipeline>`, the :doc:`destriper` plugin was applied before
to apply the decharger. Below the starting point for the application of the decharger.


.. image:: ../_images/Plugins/decharger/pre_decharger.png
   :class: align-center
   :width: 3072px
   :height: 2304px
   :scale: 20


A zoomed part of the center-bottom/center-left part of the slice can be found below. One can clearly see some complex
structures surrounded by a brightness halo, which is due to the charging artifact.


.. image:: ../_images/Plugins/decharger/pre_decharger2.png
   :class: align-center
   :width: 500px
   :height: 600px
   :scale: 60



Applying the decharger plugin with default setting (which uses the ``local_GF2RBGF`` algorithm, which can be optimized),
except for the use of the bounding box, the result obtained is showed below.


.. image:: ../_images/Plugins/decharger/post_decharger.png
   :class: align-center
   :width: 3072px
   :height: 2304px
   :scale: 20


Zooming-in in the same place, one can see that the structure now are well visible and charging is reduced.


.. image:: ../_images/Plugins/decharger/post_decharger2.png
   :class: align-center
   :width: 500px
   :height: 600px
   :scale: 60


.

.. attention::

   As one can see there is till some brighter regions in the final image. These local brightness variations probably
   have the same physical origin of the artifact here called charging. By the way, to reduce them, Decharger alone is
   not sufficient: one need to use also the :doc:`flatter` plugin. Applying the Flatten with its standard setting on the
   images above (i.e. after the Decharger) one obtain the following.


   .. image:: ../_images/Plugins/decharger/post_decharger_post_flatter.png
      :class: align-center
      :width: 3072px
      :height: 2304px
      :scale: 20


   The zoomed part now looks as below.


    .. image:: ../_images/Plugins/decharger/post_decharger_post_flatter2.png
       :class: align-center
       :width: 500px
       :height: 600px
       :scale: 60


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/decharger>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


.. _decharger_implementation_details:

Implementation details
======================


This plugin has two decharging methods implemented: the *global GF2RLGF* and the *local GF2RLGF*. They work according
to the same principle, but in the local one correct the correction is done only locally, in order reduce as much as
possible the modification in the input image.


Global GF2RBGF
--------------


In the *global GF2RBGF*, the correction algorithm is applied to the whole input image :math:`I` directly. GF2RLGF stands
for "Gaussian Filter 2 times - Rolling Ball - Gaussian Filter" which are the basic operations applied in order to
estimate the charging contribution to the input image, :math:`I_{charged}`. Once that :math:`I_{charged}` has been
estimate, it is simply subtracted to the input image, obtaining the decharged image :math:`I_{decharged}`. More
precisely, let :math:`G[\sigma]` be a gaussian kernel with standard deviation :math:`\sigma`, and let :math:`*` denote
the usual 2d convolution operator. Let :math:`RB[r]` denote the *rolling ball* algorithm [Sternberg1983]_ with radius
parameter :math:`r`, an algorithm used to estimate the background in an image. Then the GF2RLGF charging correction
procedure can be summarized as follow:

.. math::

    \begin{cases}
        I_{HF_1}(j,i) &= I(j,i)-(G[\sigma_{GF_1}] * I) (j,i)   \\
        I_{HF_2}(j,i) &= I_{HF_1}(j,i)-(G[\sigma_{GF_2}] * I_{HF_1})(j,i)    \\
        I_{charged}(j,i) &= G[\sigma_{GF_3}]*RB[r](I_{HF_2})(j,i)    \\
        I_{decharged}(j,i) &= I(j,i) - I_{charged}(j,i).
    \end{cases}

The procedure is simple. In the first step the slowly varying part of the image (low spatial frequencies) are
subtracted to the input image, following the same strategy adopted for the :doc:`Flatter <flatter>` plugin. This
procedure is iterated two times. At the end of this process the image :math:`I_{HF_2}` should contains only the high
frequency details, i.e. the small structure in the image *plus* most of the charging artifact. However, the charging
artifact is still expected to vary more slowly with respect to the small structure of the image: as such it can be
considered as a background. This background can be estimated by applying the rolling ball algorithm with a suitable
radius. The output of the rolling ball algorithm may have to much high frequency details in it, therefore a further
gaussian smoothing with small standard deviation is applied. The result obtained is :math:`I_{charged}`, which is
then subtracted to the input image. The whole procedure described here will be denoted with he symbol
:math:`gDECH[\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}]`.

Summarizing, given a stack :math:`S(j,k,i)` the global GF2RBGF decharger is applied to each slice :math:`S[k](j,i)` as
follow


.. math::

   S[k](j,i) \rightarrow S_{output}[k](j,i) = gDECH[\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}](S[k](j,i))


.. note::

 Note that with this procedure it is assumed that the charging is present in any pixel of the image: that is why
 the correction algorithm is said 'global'.


Local GF2RBGF
-------------


In the *local GF2RBGF* the correction algorithm above is not applied to the whole image: the charging contribution
is subtracted only locally, where charging is present.

In order to do that a mask, indicating where the charging is, is estimated from the input image. Proceeding similarly
to [Spehner2020]_, the estimation is done by using the downhill filter [Robinson2004]_ followed by a thresholding
operation. To proceed with the morphological reconstruction done with the downhill filter, one needs to define a seed
image: this is obtained from the original image whose color are shifted down of a value :math:`c_{shift}`, and then
setting every pixel value equal to the minimum pixel value of the image *except* at the image borders, which are left
unchanged. The threshold operation is done after the downhill filter to select the parts of the reconstructed image
with the highest brightness. Regions found in this way are filtered according to their area: only the regions having
area above a threshold :math:`A_{th}` are considered as region with charging. The operations briefly described here
will be all denoted with the symbol :math:`DHF[c_{shift},A_{th}]`. To better estimate the charged image it is better,
to apply a low pass filter to remove the slowly varying part of the image from the charging estimation. Summarizing,
let :math:`M(j,i)` be the mask containing the estimated charged region, then


.. math::

 \begin{cases}
    I_{HF}(j,i) &= I(j,i) - (G[\sigma_{GF_1}] * I) (j,i) \\
    M(j,i) &= DHF[c_{shift},A_{th}](I_{HF})(j,i).
 \end{cases}


The mask :math:`M(j,i)` obtained clearly depends on the input image :math:`I` and will we useful also for the
optimization. Once that the mask is obtained, the estimation of the charged image proceed exactly as for the global
GF2RBGF correction, except for a difference in the last step, i.e. when the estimated :math:`I_{charded}` is subtracted
from the input image. In the local GF2RBGF correction the following formula is used


.. math::

 I_{decharged}(j,i) = \left[1-M(j,i)-\partial M(j,i)\right] \cdot I(j,i)-\left[M(j,i)
                      + \partial M(j,i)\right] \cdot I_{charged}(j,i),


where :math:`\partial M` is obtained from the mask :math:`M` and is zero everywhere expect in external border region
of :math:`M`, where the values are increased linearly form 0 to 1 as one moves from the most external regions
outside :math:`M` to :math:`M` itself. :math:`\partial M` is used to smoothly pass form the corrected to the
uncorrected parts of the input image. The whole procedure described here will be denoted with he symbol
:math:`lDECH[c_{shift},A_{th},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}]`. This kind of correction method, try to
correct charging by removing the less is possible, but it may be slow.

Summarizing, given a stack :math:`S(j,k,i)` the local GF2RBGF decharger is applied to each slice :math:`S[k](j,i)` as
follow


.. math::

   S[k](j,i) \rightarrow S_{output}[k](j,i) =
                         lDECH[c_{shift},A_{th},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3}](S[k])(j,i).


In both versions, in case of stack with multiple channels, the Decharger is applied independently to each channel.


Optimization details
~~~~~~~~~~~~~~~~~~~~


The optimization is possible only for the local method, since only in this case one can get an estimation of the typical
value one would have in the images without charging. Given the mask :math:`M(j,i)`, one can decompose it into connected
regions. Let  :math:`Q` be one of these connected region, then one defines the region :math:`Q^s` by dilating :math:`s`
times the mask :math:`Q`, and then subtract (in set theoretic sense) :math:`Q` itself to the dilation result, i.e.


.. math::

   Q^s = \mbox{ dilate }(Q,s) - Q


This region is interesting because, if it has no superposition with any non-null part of :math:`M`, this can be
considered as a region without charging close to :math:`Q` itself, therefore is can be a good guess on how the charged
region :math:`Q` would look like if no charged is present. Therefore one can compare the two regions in order to find
the best parameter combination for the decharger as the ones which make the two regions closest as possible. The
'closeness' of the two regions need to be defined in a proper manner. Charging is expected to shift up (or down in the
case of inverse charging) the brightness of the image. This should be visible at the level of the "local" image
histograms, i.e. the histograms made with the gray levels of the pixels belonging to the two regions :math:`Q` and
:math:`Q^s`.

Let :math:`\mbox{hist }[I,Q]` be the *normalized* histogram constructed using the value of the pixels of the image
:math:`I` in the region :math:`Q` only. It is expected that charging simply shift the (normalized) histogram (up or
down depends on the kind of charging). Therefore, the decharger should reduce/eliminate this shift making the
normalized histograms in :math:`Q` and :math:`Q^s` closer. Using the total variation distance between discrete
probability distributions to measure the closeness of the two normalized histograms, the loss below can be defined


.. math::

   \mathcal{L}[\alpha](I,Q,Q^s) =
   \sum_{b} | \mbox{hist }\left[lDECH[\alpha](I),Q\right](b) - \mbox{hist }\left[lDECH[\alpha](I),Q^s\right](b) |,


where :math:`\alpha = (c_{shift},\sigma_{GF_1},\sigma_{GF_2},r,\sigma_{GF_3})` are the optimizable parameters of the
decharger and the sum is over the normalized histograms bins.


.. note::

   Note that the parameter :math:`A_{th}` is not present in the loss and no optimization procedure is available for it.


Given a :math:`K \times J \times I` stack :math:`S(k,j,i)` take a collection of its slices
:math:`\{S[k](j,i)\}_{k \in V_K}` where :math:`V_K \subset \{0,1,\cdots,K-1\}` (i.e. the subset of slices selected for
the optimization), then the decharger optimization routine solve the following problem


.. math::

   c_{shift}^{best},\sigma_{GF_1}^{best},\sigma_{GF_2}^{best},r^{best},\sigma_{GF_3}^{best} =
   \mbox{argmin}_{\alpha} \left( \sum_{k \in V_K} \sum_{Q_k} \mathcal{L}[\alpha](S[k],Q_k) \right)


The solution is obtained via a simple grid search over a given parameters space. To speed up this operation, the sum
over :math:`Q_k` is not done over all the connected components of the mask :math:`M_k`, but over a subset of the first
:math:`N` connected component having the biggest area.


Further details
===============


Tutorials:


* `skimage tutorial on rolling ball algorithm <https://scikit-image.org/docs/stable/auto_examples/
  segmentation/plot_rolling_ball.html>`_.

* `skimage tutorial on downhill filter algorithm
  <https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_regional_maxima.html>`_.

* :doc:`../Miscellaneous/decharger optimization`.


Articles:


.. [Sternberg1983] "Biomedical Image Processing" - Sternberg S. R. - Computer - Volume: 16, Issue: 1, Jan 1983 -
   doi: 10.1109/MC.1983.1654163.

.. [Spehner2020] "Cryo-FIB-SEM as a promising tool for localizing proteins in 3D" - Spehner D., Steyer A. M.,
   Bertinetti L., Orlov I., Benoit L., Pernet-Gallay K., Schertel A., Schultz P. - J. Struct. Biol. 2020
   Jul 1;211(1):107528,doi: 10.1016/j.jsb.2020.107528.

.. [Robinson2004] "Efficient morphological reconstruction: A downhill filter" - Robinson K., Whelan P. F. - Pattern
   Recognition Letters 25(15):1759-1767, November 2004 - doi:10.1016/j.patrec.2004.07.002.
