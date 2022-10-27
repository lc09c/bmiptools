===========
Registrator
===========



.. admonition:: Registrator in a nutshell.
   :class: note

   1. Plugin to align among each other the slices of a stack;
   2. This plugin is **not** multichannel;
   3. Python API reference: :py:class:`bmiptools.transformation.alignment.registrator.Registrator`.


This plugin can be used to align among each other the slices of the input stack, in order to get a proper 3d
reconstruction. The registration procedure of this plugin consist in at most two steps:

1. *rigid registration*, where a global affine transformations is applied to each slice to match it geometrically with
   the next. The rigid registration can happen in two ways: either via ECC based matching algorithm [Evangelidis2008]_
   (slower but it is more precise in principle) or via phase correlation based matching algorithm [Reddy1996]_ (faster
   but it may be less precise).

2. *non-rigid registration*, which is used to eventually refine the result of the previous step, where a pixelwise
   transformation is applied to each pixel of a slice to match it with the corresponding pixel in the next slice
   (keeping into account the pixel surrounding) based on optical-flow-based matching [LeBesnerais2005]_. This step
   is optional.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.alignment.registrator.Registrator`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.


.. code-block::

   {'load_existing_registration': False,
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


The plugin-specific parameters contained in this dictionary are:

* ``load_existing_registration``: if ``True`` an existing registration produced by this plugin is loaded and all the
  other fields below except ``loading_path`` are ignored.

* ``loading_path``: contains the path to the files containing the existing registration parameters.

* ``registration_algorithm``: field where one has to specify the algorithm used to perform the *rigid* registration. The
  possible options are:

  * ``'ECC'``
  * ``'Phase_correlation'``

* ``padding_val``: it is the value used for padding the images in order to reach a certain shape during the application
  of the registration.

* ``destandardize``: when True at the end of the registration ,the image is destandardized (image standardization take
  place before the optimization of the registration algorithm and is done according to the 0/1 mode of the
  :doc:`standardizer` plugin).

* ``ECC_registration_setting``: contains the setting for the ECC registration algorithm. It is a dictionary and
  has to be specified as below:

  * ``n_iterations``, is  number of iterations used for the maximization of the ECC loss.

  * ``termination_eps``, is epsilon value used to determine the convergence of the ECC maximization algorithm:
    if the difference between the ECC values after two iterations is less then this value, then the maximization stops.

  * ``motion_model``, is the kind of motion model used for the estimation of the parameters used for the
    registration, and can be equal to

    * ``'Translation'``;
    * ``'Euclidean'`` ( i.e. rotation + translation);
    * ``'Affine'``.

  * ``template_lh_boundary_factor``, it is the left/high boundary factor for the template window definition
    (recommended value: 1)

  * ``template_rb_boundary_factor``, it is right/bottom boundary factor for the template window definition
    (recommended value: 1)

  * ``ecc_threshold``, is the threshold on the ECC value at the end of the maximization procedure below which a two
    steps estimation procedure for the estimation of the transformation parameters is run.

* ``phase_correlation_registration_setting``: contains the setting for the registration algorithm based on the phase
  correlation techniques. It is a dictionary having the keys below:

  * ``motion_model``, *do not change. currently only* ``'Translation'`` *is possible*.

  * ``phase_corr_threshold``, is threshold on the normalized correlation below which the two steps registration
    optimization is executed.

* ``refine_with_optical_flow``: if ``True`` a final refinement with optical flow registration is applied at
  after that the rigid registration has been applied on the stack.

* ``OF_setting``: is a dictionary containing the setting of the optical flow registration. This dictionary has to be
  specified as follow:

  * ``optical_flow_attachment``, it is the attachment parameter of the optical flow registration algorithm.

  * ``save_mod_OF``, if ``True`` the modulus of the optical flow field is saved.

  * ``mod_OF_saving_path``, is the path where the modulus of the optical flow registration field is saved.
    If the above field is False this field is ignored.

* ``save_fitted_registration``:  if ``True`` the parameters estimated for the rigid-registration are saved.

* ``saving_path``: is the path where the registration parameters are saved.


Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Registrator <bmiptools.transformation.alignment.registrator.Registrator>`.


Use case
========


The typical use of this plugin are:


1. Align the slices of a stack in order to get a proper 3d reconstruction.


.. tip::

  The following things turn out to be useful, from a practical point of view.

  1. Using the bounding box the the time necessary for the estimation of the rigid registration can be reduced. By the
     way the time for the refined optical flow registration (if used to refine the result), does not change.

  2. The parameter describing the *rigid registration* can be saved and loaded in a later time, allowing the
     registration of a stack by using the parameter estimated using a different stack. This may be particularly useful
     in case one has to register two stack which are produced at the time from the same sample but with different
     imaging techniques.

  3. It can be reasonable to fit this plugin in the beginning of the image processing pipeline but *apply it only at*
     *the end*. This because this plugin change the dimension of the images, making the stack bigger. This means that
     more RAM memory is required and the overall computation is increased. Therefore, *if there is no need to use the*
     *3-dimensional information for the application of a plugin*, is a good strategy. Note that practically all the
     image processing plugin in bmiptool act on the slices directly, and works without the need of information coming
     from (the local structures of) the other slices.

  4. The use of the ``'Translation'`` motion model advised for the rigid-registration step.

  5. To achieve a non-rigid registration, the a rigid registration is always done before. This is done because the
     non-rigid registration is not good in estimating big translations, which can be vary easily estimated with
     rigid methods. Since the non-rigid method is particularly slow and is used to refine the registration, it is
     recommended to use ``Phase_correlation`` which is fast and enough to get a good result.

  6. In the ``ECC_registration_setting``, if there are no particular reasons, ``template_lh_boundary_factor`` and
     ``template_rb_boundary_factor`` should not be changed.


Application example
===================


As example consider the portion of a FIB-SEM stack of a biological sample, visualized as animated gif (saving mode
available in the python API, see :py:meth:`bmiptools.stack.Stack.save_as_gif`), in order to get the feeling of the
3-dimensional structure of the sample. Before any registration the stack look like below.


.. image:: ../_images/Plugins/registrator/pre_registration.gif
   :class: align-center
   :width: 95 %
   :scale: 95


A registration based on ``Phase_correlation`` only and using practically all the default parameters of the plugin (i.e.
the ones in the ``empty_transformation_dictionary``, but disabling the use of the bounding box only, due to the small
dimension of the image) would give the result below.


.. image:: ../_images/Plugins/registrator/post_registration.gif
   :class: align-center
   :width: 100 %
   :scale: 100


When after the ``Phase_correlation`` step, also the refinement with optical flow is applied (i.e. setting
``refine_with_optical_flow = True`` in the transformation dictionary of the plugin) would give the result below.


.. image:: ../_images/Plugins/registrator/post_registration_refined.gif
   :class: align-center
   :width: 100 %
   :scale: 100


Note that after the optical flow refinement, the central structure in the top-right corner of the image changes more
smoothly from one slice to the other. The other points of the slices are practically unchanged, showing the local
nature of the refinement step of the registrator plugin.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/registrator>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


Implementation details
======================


A registration algorithm in general takes as input two things: an input  image and a reference image. The reference
image is the reference on which the input image is aligned. The registration algorithms in this plugin consist
essentially in two steps:

1. In the first step a map between the pixel positions of the input image and the pixel position is established. This
   map can be the same for all pixels (in case of rigid registration) or be pixel dependent (in the non-rigid case).
   These maps are parametrized in a suitable manner, and the best parameters for this map are found by various
   optimization techniques.

2. In the second step the input image is evaluated on the new pixel position obtained from the map derived in before.
   This evaluation is done by computing the pixel value in the new position via interpolation.


In what follows :math:`\phi[\alpha]` will denote the registration procedure described by the two steps above, where
:math:`\alpha` are the registration parameters. For the rigid registration, implemented in this plugin it may take the
following form


* for translation, :math:`\phi[\alpha](I(x)) = I(x+t)`, where :math:`t` is a suitable translation vector.

* for a generic euclidean transformation, :math:`\phi[\alpha](I(x)) = I(Rx+t)`, where :math:`t` and :math:`R` is a
  suitable translation vector and rotation matrix respectively.

* for a generic affine transformation, :math:`\phi[\alpha](I(x)) = I(Ax+t)`, where :math:`t` and :math:`A` is a
  suitable translation vector and (invertible) matrix respectively.


For non-rigid transformations one can formally write :math:`\phi[\alpha](I(x)) = I(f_\alpha(x))`, where :math:`f_\alpha`
is a suitable parameterizable function which may depends also on other image pixels and not only on :math:`x`.

Given a :math:`K \times J \times I` stack :math:`S(k,j,i)` for each slice :math:`S[k](j,i)` the output of the
registration algorithm is given as follow


.. math::

   S[k](j,i) \rightarrow S'_{output}[k](j',i') = \phi[\alpha](S[k](j,i))


where :math:`S'_{output}[k](j',i')` is the :math:`k`-th slice of the :math:`K \times J' \times I'` output stack
:math:`S'_{output}(k,j',i')`. The input and output stack have different size: indeed this plugin change the image
dimension in order to accommodate the image "movements" due to the registration.


ECC
---


The ECC (Enhanced Correlation Coefficient) registration algorithm [Evangelidis2008]_ is a gradient-based registration
technique. Given an input image :math:`I(x)` and a reference image :math:`I_{ref}(x)`, the parameters of
:math:`\phi[\alpha]` are found by minimizing the following differentiable loss


.. math::

   \mathcal{L}_{ECC}(\alpha) =
   \sum_x\|\frac{I_{ref}(x)}{\|I_{ref}(x)\|}-\frac{\phi[\alpha](I(x))}{\|\phi[\alpha](I(x))\|}\|^2


where :math:`\|\cdot \|` is the euclidean norm. The implementation used in this plugin is based on the
`one <https://docs.opencv.org/3.4/dc/d6b/group__video__track.html>`_ available in openCV.


.. attention::

   If the optimization using this loss fails for a pair of slices in a stack (i.e. if the value of the loss function
   remains above a certain threshold :math:`ECC_{th}`), a two step estimation is done: a first translation is estimated
   using the Phase correlation routine on a smaller part of the image, and later a refined estimation is done using
   again the ECC on the whole image. If the second estimation is still unsuccessful, only the result of the first step
   is used.


Phase correlation
-----------------


The phase correlation registration algorithm [Reddy1996]_ simply compute the normalized cross-correlation between the
input image and the reference one. Since the cross-correlation can be computed with a simple multiplication in Fourier
space, by using `Fourier shift theorem <https://en.wikipedia.org/wiki/Discrete_Fourier_transform#Shift_theorem>`_, if
the input and reference image are linked by a rigid translation,the cross-correlation would be just a phase factor. When
transformed back to the real space, the cross-correlation corresponds to a delta function centered in a certain point
:math:`p`. The vector linking :math:`p` with the center of the image correspond to the translation linking the two
images.

In this plugin only translation vectors can be estimated with this method, despite in principle it is possible
to estimate also rotation angles by means of a change of coordinates. The implementation of this algorithm used in
this plugin is the one of `openCV <https://docs.opencv.org/4.1.1/d7/df3/group__imgproc__motion.html
#ga552420a2ace9ef3fb053cd630fdb4952>`_


.. attention::

   If the optimization using this loss fails for a pair of slices in a stack (i.e. if the value of normalized
   cross-correlation remains above a certain threshold :math:`PC_{th}`), a two step estimation is done: a first
   translation is estimated using the Phase correlation routine on a smaller part of the image, and later a refined
   estimation is done using again the  Phase correlation routine on the whole image. If the second estimation is still
   unsuccessful, only the result of the first step is used.


Optical flow
------------


The Lucas-Kanade optical flow registration algorithm [LeBesnerais2005]_ is another gradient based optimization
techniques allowing for non-rigid registration. It is based on the minimization of the following loss function


.. math::

   \mathcal{L}_{OF}(\alpha) = \sum_{(i,j)} \sum_{(j',i') \in G(j,i)}
                              \left[I_{ref}(j',i')-\tilde{I}(j'+f_j[\alpha](j',i'), i'+f_i[\alpha](j',i') )\right]^2


where :math:`\tilde{I}` is the interpolated version of the input image :math:`I`, so that it can be evaluated on a
generic point :math:`(j+f_j[\alpha](j,i), i+f_i[\alpha](j,i) )`, which does not lie necessarily on the pixel grid. The
non rigid character of this algorithm lies in the second sum, since :math:`G(j,i)` is a patch centred in :math:`(j,i)`.
The goal of the optimization problem is to find the parameters :math:`\alpha` defining the *optical flow vector field*,
which tells how the position of the pixels in the input image and the one in the reference image are mapped. In
particular, this quantity can be useful

.. math::

   \left(
   \begin{array}{c}
   j_{input}\\
   i_{input}\\
   \end{array}
   \right) =    \left(
   \begin{array}{c}
   j_{ref}+f_\alpha(j_{ref},i_{ref})\\
   i_{ref}+f_\alpha(j_{ref},i_{ref})\\
   \end{array}
   \right).

The two components of the optical flow field, :math:`f_\alpha(j_{ref},i_{ref})` and :math:`f_\alpha(j_{ref},i_{ref})`,
can be thought as two 2d images where the "movements" between the input and the reference image can be visualized.
The magnitude of these "movements" can be summarized in the image containing the magnitude of the optical flow field.


This plugin uses the `skimage implementation <https://scikit-image.org/docs/stable/api/skimage.registration.html
#skimage.registration.optical_flow_ilk>`_ of this algorithm.


Further details
===============


Websites:


* `Affine transformation on wikipedia <https://en.wikipedia.org/wiki/Affine_transformation>`_.

* `Phase correlation on wikipedia <https://en.wikipedia.org/wiki/Phase_correlation>`_

* `Optical flow on wikipedia <https://en.wikipedia.org/wiki/Optical_flow>`_


Articles:

.. [Evangelidis2008] "Parametric Image Alignment using Enhanced Correlation Coefficient Maximization" -
   G.D. Evangelidis, E.Z. Psarakis - IEEE Trans. on PAMI, vol. 30, no. 10, 2008

.. [Reddy1996] "An FFT-based technique for translation, rotation, and scale-invariant image registration." - Reddy B.S.,
   and B. N. Chatterji.  - IEEE transactions on image processing : a publication of the IEEE Signal Processing Society
   5 8 (1996): 1266-71 .

.. [LeBesnerais2005] "Dense optical flow by iterative local window registration" - G. Le Besnerais and F. Champagnat,  -
   IEEE International Conference on Image Processing 2005, 2005, pp. I-137, doi: 10.1109/ICIP.2005.1529706.

