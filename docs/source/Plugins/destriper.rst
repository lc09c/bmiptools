=========
Destriper
=========


.. admonition:: Destriper in a nutshell.
   :class: note

   1. Plugin to eliminate the curtaining artifacts (typical of Cryo FIB-SEM images) in a stack;
   2. This plugin is multichannel;
   3. This plugin can be optimized on the stack;
   4. Python API reference: :py:class:`bmiptools.transformation.restoration.destriper.Destriper`.


This plugin can be used to eliminate the curtaining artifacts, typical of Cryo FIB-SEM images. It implements the
Wavelet-FT filter described in [Beat2009]_ with an optimization procedure for the automatic selection of the
filter parameter. The Wavelet-FT filter is applied slice-wave to the input stack.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.restoration.destriper.Destriper`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.

.. code-block::

    {'auto_optimize': True,
    'optimization_setting': {'wavelet': {'use_wavelet': 'all',
                                        'wavelet_family': 'db'
                                        },
                            'sigma': {'sigma_min':0.01,
                                     'sigma_max': 50,
                                     'sigma_step':1
                                     },
                            'decomposition_level': {'set_decomposition_level_to_max_compatible': True,
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


The optimization-related plugin-specific parameters contained in the ``optimization_setting`` field of this dictionary
are:


* ``wavelet``: contains dictionary with the parameters related to the possible wavelet type which can be used by the
  Wavelet-FT filter during the parameter search. The key of this dictionary are:

    * ``use_wavelet``: it specify the kind of wavelet(s) and can take the following values:

        * ``'all'``, to check all the discrete wavelets available in the *PyWavelet* library during the optimization.

        * ``'family'``, to check just a single wavelet family during the optimization. When this option is used the
          wavelet family have to be specified in the field ``wavelet_family``.

        * A name of a discrete wavelet of the *PyWavelet* library which is kept fixed during the optimization (see
          `here <http://wavelets.pybytes.com/>`_ for the list of available wavelet).

    * ``wavelet_family``: name of a discrete wavelet family of the *PyWavelet* library to search only among the wavelets
      of this family during the optimization. This field is ignored if ``use_wavelet`` is not set equal to ``family``.

* ``sigma``: contains a dictionary for the setting defining the parameter space for the standard deviation of the
  gaussian filter used on vertical components of the wavelet decomposition of the image to be filtered. This dictionary
  has the following keys:

    * ``sigma_min``: minimum value of standard deviation of the gaussian filter used by the Wavelet-FT filter used
      during the parameter search.

    * ``sigma_max``: maximal value of standard deviation of the gaussian filter used by the Wavelet-FT filter used
      during the parameter search.

    * ``sigma_step``: step value used to define the possible values of standard deviation of the gaussian filter used
      by the Wavelet-FT filter used during the parameter search.

* ``decomposition_level``: contains a dictionary for the setting related to the research of the decomposition level
  used in the wavelet decomposition of the image. It has to be specified as follow:

    * ``set_decomposition_level_to_max_compatible``: if set True only the maximal possible level of the wavelet
      decomposition, which would not not introduce boundary artifacts in the reconstruction of the unfiltered image, is
      used during the parameter search (see :ref:`here <destriper_tips>`).

    * ``decomposition_level_min``: it is the minimum decomposition level of the 2D wavelet transform used during the
      parameter search. If set equal to 'max' the maximal possible level of the wavelet decomposition, which would not
      not introduce boundary artifacts in the reconstruction of the unfiltered image, is used.

    * ``decomposition_level_max``: it is the maximal decomposition level of the 2D wavelet transform used during the
      parameter search. If set equal to ``'max'`` the maximal possible level of the wavelet decomposition, which would
      not introduce boundary artifacts in the reconstruction of the unfiltered image, is used.

    * ``increase_decomposition_level_during_inference``: if set True the decomposition level during the inference is
      increased by one. This typically further reduces the stripe artifacts in case the optimization does not find the
      visually best combination of parameters.


The plugin-specific parameters contained in this dictionary are:


* ``wavelet_decomposition``:  contains a dictionary for the setting of the wavelet transform part of the Wavelet-FT
  filter. The dictionary has to be specified as below:

    * ``wavelet_name``: is the wavelet name used by the Wavelet-FT filter

    * ``decomposition_level``: when an integer number is given, this number is the maximal decomposition level
      used in the wavelet transform. If ``'max'`` is given, the highest level which can be used in the wavelet
      decomposition without introduce border artifacts in the reconstruction of the unfiltered image is used.

* ``fourier_space_filter``: contain a dictionary for the setting related to the Fourier transform part of the filter
  used in this plugin. The only possible parameter is:

    * ``sigma``: is the standard deviation of the gaussian filter used in the Fourier space to remove vertical
      artifacts.

* ``match_in_out_contrast``: when True, the histogram of each slice of the stack after the Wavelet-FT filter is matched
  with the histogram of the corresponding input slice, increasing the contrast in the output.


When ``auto-optimize = True`` the plugin-specific parameters above are ignored, since the one selected by the
optimization procedure are used. Finally, the meaning of the remaining parameters can be found in
:ref:`General information#Transfomation dictionary <transformation_dictionary>`.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Destriper <bmiptools.transformation.restoration.destriper.Destriper>`.


Use case
========


The typical use of this plugin are:


1. Reduce the curtaining artifact present on the input stack.


.. _destriper_tips:

.. tip::

  The following things turn out to be useful, from a practical point of view.

  1. If the bounding box is used during the optimization, it should contain the region of the stack where the curtaining
     artifacts are stronger. Optimizing the plugin in a different region would lead to sub-optimal filter parameter for
     the input stack.

  2. Most of the time, setting the decomposition level to the maximum value allowing to the wavelet decomposition to
     reconstruct the image without introducing artifacts related the image boundaries, gives good result. This number
     depends on the image size and can be computed in advance. During the optimization by setting
     ``set_decomposition_level_to_max_compatible = True`` the decomposition level is kept constant to maximum value.
     If in ``wavelet_decomposition`` one set ``decomposition_level = 'max'``, the decomposition level used for the
     filter application is automatically set to the maximum value, without the need to the user to specify it.

  .. _bb_tip:

  3. Empirically, it has been observe that:

        * if stripes are of the same intensity along the entire image, not using the bounding box (i.e set
          ``use_bounding_box = False``) and increasing the decomposition level of the Wavelet transform during the
          filter application (i.e. set ``increase_decomposition_level_during_inference = True``) gives good result.

        * if stripes have a stronger intensity in some part of the image, using the bounding box  "centered" in this
          region (i.e set ``use_bounding_box = True`` and
          :ref:`set the correct coordinates for the bounding box <bbox_convention>`)
          *without* increasing decomposition level during the filter application (i.e. set
          ``increase_decomposition_level_during_inference = True``) gives good result.

  4. The ``match_in_out_contrast`` option typically increase the contrast in the output image. However, it may also
     amplify some artifact that can be introduced by the Wavelet-FT filter.


Application example
===================


As example consider the slice of a stack of a biological sample obtained via FIB-SEM, where the striping artifact is
clearly present.


.. image:: ../_images/Plugins/destriper/pre_destriper.png
   :class: align-center
   :width: 3000px
   :height: 2000px
   :scale: 20


A zoomed part of the center-top/right part of the slice can be found below. One can clearly see some complex structures
under the vertical stripes.


.. image:: ../_images/Plugins/destriper/pre_destriper2.png
   :class: align-center
   :width: 1000px
   :height: 1000px
   :scale: 60


Applying the destriper plugin with default setting, except for the use of the bounding box, which was defined in the
center-bottom part of the image and increasing the decomposition level during the inference (i.e. setting
``increase_decomposition_level_during_inference = True``, see :ref:`tip number 3 <bb_tip>` of the previous section)


.. image:: ../_images/Plugins/destriper/post_destriper.png
   :class: align-center
   :width: 3000px
   :height: 2000px
   :scale: 20


Zooming-in in the same place, one can see that the structure now are well visible and the stripes are almost absent.

.. image:: ../_images/Plugins/destriper/post_destriper2.png
   :class: align-center
   :width: 1000px
   :height: 1000px
   :scale: 60


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/destriper>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


.. _destriper_implementation_details:

Implementation details
======================


The core operation of this plugin is the application of the Wavelet-Fourier filter described in [Beat2009]_. Given a
:math:`K \times J \times I` stack :math:`S(k,j,i)`, the Wavelet-Fourier filter is
applied to each slice :math:`S[k](j,i)`. The filter consists essentially of 3 steps:


1. 2D wavelet decomposition using a certain wavelet :math:`w` up a to certain decomposition level :math:`l` of the input
   image. This operation consists essentially in the iterated application of a (single-level) 2D wavelet transform
   with wavelet :math:`w` for :math:`l` times. Given an input slice :math:`S[k](j,i)`, the application of a
   (single-level) 2D discrete wavelet transform :math:`WT[w]` produces 4 different output images, having half of the
   size of the input, (also called *subbands*) namely


   .. math::

       \{ S_{LL}[k](j',i'), S_{LH}[k](j',i'), S_{HL}[k](j',i'), S_{HH}[k](j',i') \} = WT[w]( S[k](j,i) ),


   which represents the wavelet decomposition at the level 1. :math:`S_{LL}` contains an approximation of the input
   image, :math:`S_{LH}` contains mainly the horizontal features of the input image, :math:`S_{HL}` contains mainly the
   vertical features of the input image, while :math:`S_{HH}` contains essentially the diagonal features of the input
   image. To go on to the next level, the 2D wavelet transform is applied recursively to the approximation image
   :math:`S_{LL}` for :math:`l` times. The full transformation will be denoted with :math:`WD2d[w,l]`.

2. Filtering in the fourier space the vertical component at all levels. This filtering consist in the application of
   a 2D discrete Fourier transform, :math:`DFT`, then multiply the result by a suitable filter function
   :math:`g(\nu_j,\nu_i)`, and finally applying the 2D inverse discrete fourier transform. The filter function
   :math:`g(\nu_j,\nu_i)` is chosen such that the vertical components due to stripes artifact are suppressed, and turns
   out to be equal to


   .. math::

        g(\nu_j,\nu_i) = g_\sigma(\nu_j,\nu_i) = 1-e^{-\frac{\nu_j^2}{2\sigma^2}},


   which depends only on the parameter :math:`\sigma`.  Let :math:`S_{HL,u}[k](j,i)` be the vertical component produced
   by the wavelet transform at the level :math:`u \in [1,...,l]`.


   .. math::

        S_{HL,u}^{filt}[k](j,i) = DFT^{-1}[  g_\sigma \cdot DFT[ S_{HL,u}[k] ] ](j,i).


   This is done for all decomposition levels :math:`u \in [1,...,l]`. The whole filtering operation will be denoted by
   :math:`FF[\sigma]`.

3. 2D wavelet reconstruction using the wavelet :math:`w` and decomposition level :math:`l` used in initial step.
   It works exactly as the 2d wavelet reconstruction, but rather than using the 2D wavelet transform, it uses
   its inverse. For each level :math:`u`, the input of the inverse wavelet transform is composed by the 4 outputs
   described in step 1, except that :math:`S_{HL,u}^{filt}` is now used instead of :math:`S_{HL,u}`. This operation
   will be denoted with :math:`WD2d^{-1}[w,l]`.


Summarizing, the Wavelet-Fourier filter consists in the following operation


.. math::

    S[k](j,i) \rightarrow S_{output}[k](j,i) = WD2d^{-1}[w,l]( FF[\sigma]( WD2d[w,l]( S[k](j,i) ) ) ).


This operation is applied on all the slices of the stack. It can be seen that this plugin depends on 3 parameters:

* the wavelet used :math:`w`,

* the decomposition level :math:`l`,

* the parameter :math:`\sigma` of the filter in the Fourier space,

which corresponds to the parameters of the transformation dictionary contained in the fields ``wavelet_decomposition``
and in ``fourier_space_filter``. In case of stack with multiple channels, the destriper is applied independently to each
channel.


Optimization method
~~~~~~~~~~~~~~~~~~~


The possible combinations of the 3 parameters for the wavelet-Fourier filter are a lot. Most of the time a simple
criteria can be used for the selection of the level (see :ref:`here <destriper_tips>`), but even in this case the
parameters combinations are too many. Find the right combination of parameters can be therefore a time consuming
operation. An optimization procedure has been developed to automatize this step, rendering the plugin almost
parameter-less. What the user have to do is just to define the parameters space boundaries. This is done in the in
``optimization_setting`` section of the transformation dictionary. The default parameter space boundaries specified
in the ``empty_transformation_dictionary`` of the plugin, seem to be good enough for majority of the typical application
cases of this plugin.

The optimization is done by finding the parameters combinations which minimize a suitable loss function. More precisely,
let :math:`f_{w,l,\sigma}` be the wavelet-Fourier filter described in the previous section. Given an input image
:math:`I(j,i)` of size :math:`J \times I` with curtaining artifact, one can trivially write that


.. math::

    I(j,i) = O(j,i) + D(j,i),


where :math:`O(j,i)` is the *output image*, i.e. :math:`O(j,i) = f_{w,l,\sigma}[I](j,i)`, while :math:`D(j,i)` is
called *stripe image*, which can be simply defined as :math:`D(i,j) := O(i,j) - I(i,j)`. For the perfect filter, the
stripe image would contain only the stripes, while the output image would contain the image without any curtaining
artifact. Consider the ideal case, where the curtaining artifacts consist in perfectly vertical stripes of constant
intensity superimposed to the true image (in the real case the stripes are slightly swinging and the intensity may
vary). Assume also that the stripe intensity is high if compared to the typical intensity of the true image. By using
the perfect filter, the gradient along the vertical direction of the destriped output image would match exactly gradient
of the true image, while the gradient of the stripe image along the same direction would be zero everywhere. For the
horizontal direction the situation is different: the gradient along the horizontal direction of the stripe image would
be close but not equal to the gradient of the input image, since most of the variations along horizontal direction are
due to the stripes. Keeping that in mind, one can define the following loss function


.. math::

    \mathcal{L}[w,l,\sigma](I) = P+Q+R,


with

* :math:`P = \frac{1}{JI}\sum_{j,i} |\nabla_y O(j,i) - \nabla_y I(j,i)|`, is the term favoring the match between the
  gradient along the vertical direction between the output image and the input image;

* :math:`Q = \frac{1}{JI}\sum_{j,i} |\nabla_x D(j,i) - \nabla_x O(j,i)|`, is the term favoring the match between the
  gradient along the horizontal direction of the stripe image and the output image;

* :math:`R = \frac{1}{JI}\sum_{j,i} |\nabla_y D(j,i)|`, is the term favoring the vanishing of the gradient of the stripe
  image along the vertical direction.

These three conditions are *weighted in equal manner* in the loss. :math:`\nabla_y` and :math:`\nabla_x` are the
gradient operators along the corresponding directions. In the current implementation, the gradient is approximated using
the central difference scheme, typically used to discretize derivatives. By using simple math, it easy to see that


.. math::

    \mathcal{L}[w,l,\sigma](I) = 2R+Q.


.. note::


   The loss function :math:`\mathcal{L}[w,l,\sigma]` is asymmetric in how the X- and Y- direction are treated:
   apparently what happens in the Y-direction seems to have the double of the importance of what happens in the
   X-direction. The reason for this asymmetry lies in the fact that there is no term keeping into account that the
   variation of the destriped output image along the X-direction are small, compared to the variation of the stripe
   image in the same direction. By the way, a term encoding this requirements can be added to the loss. It has a
   similar structure to the one of the :math:`R` term , and in particular it is


   .. math::

        W = \frac{1}{JI}\sum_{j,i} |\nabla_x O(j,i)|.


   It is however important to note, that the derivative of the destriped output image along the horizontal directions,
   even in the ideal case cannot vanish: the true image still vary along the horizontal direction in general.
   This means that if :math:`R` is present in the loss to force :math:`\nabla_y D` to vanish, the term :math:`W` need
   to have less importance in the loss with respect to :math:`R`. This can be achieved by multiplying :math:`W` for a
   suitable weight :math:`\lambda`, i.e.


   .. math::

      W = \lambda \cdot \frac{1}{JI}\sum_{j,i} |\nabla_x O(j,i)|,


   with :math:`\lambda << 1`. The condition on :math:`\lambda`, encode exactly the fact that :math:`W` have to be less
   important than :math:`R`. However if :math:`\lambda << 1` this term can be neglected without altering too much the
   position of the minimum of the loss. That is the reason why this term is absent in the definition of the loss.


At this point, given a stack :math:`S(k,j,i)` of size :math:`K \times J \times I`, the optimization problem can be
formulated as follow:


.. math::

    (w_{best}, l_{best}, \sigma_{best}) = \mbox{argmin}_{w,l,\sigma} \left(
                                          \frac{1}{N}\sum_{n=0}^{N-1} \mathcal{L}[w,l,\sigma]( S[k_n] ) \right)


where the loss function is the average over some subset of slices :math:`S[k_0],...,S[k_{N-1}]` (with :math:`N \leq K`)
of the stack :math:`S(k,j,i)`. This subset of slices is defined by means of the parameter ``fit_step`` in the
``optimization_setting`` field of the transformation dictionary.


.. note::

    When a bounding box is used, the loss :math:`\mathcal{L}[w,l,\sigma]` is not computed using the whole slice
    :math:`S[k_n](j,i)` but using the part of the slice selected with the bounding box.


From the algorithmic point of view, the current implementation of the optimization routine is rather trivial. The
parameter space is defined according to the parameter specified in the ``optimization_setting`` field of the
transformation dictionary, and the best parameter combination is found with a simple grid search.


Further details
===============

Tutorials:

* :doc:`../Miscellaneous/destriper optimization`.


Articles:

.. [Beat2009] "Stripe and ring artifact removal with combined wavelet—Fourier filtering" - Beat Münch, Pavel Trtik, Federica
   Marone, and Marco Stampanoni - https://doi.org/10.1364/OE.17.008567