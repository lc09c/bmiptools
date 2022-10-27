========
Denoiser
========


.. admonition:: Denoiser in a nutshell.
   :class: note

   1. Plugin to denoise with classical methods the slices of a stack;
   2. This plugin is multichannel;
   3. This plugin can be optimized on a stack;
   4. Python API reference: :py:class:`bmiptools.transformation.restoration.denoiser.Denoiser`.


This plugin can be used to reduce the noise level of the slices using classical denoising techniques. In particular, the
following techniques are available:

* *wavelet based denoising*;
* *total variation denoising*, both the Chambolle algorithm and the Split-Bregman based algorithm;
* *bilateral filter*;
* *non-local means*.

The optimization routine which can be used to select the best filter and parameter combination is based on the principle
of J-invariance denoising. These denoising algorithms are essentially 2D, therefore they are applied
slice-wise to the stack.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.restoration.denoiser.Denoiser`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.


.. code-block::

    {'auto_optimize': True,
    'optimization_setting': {'tested_filters_list': ['wavelet','tv_chambolle','nl_means'],
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

The optimization-related plugin-specific parameters contained in the ``optimization_setting`` field of this dictionary
are:

* ``tested_filter_list``: contains the list of denoiser that are compared among each other during the optimization. The
  currently available denoiser are

  * ``wavelet``, for wavelet based denoising;

  * ``tv_chambolle``, for the Chambolle total variational denoising;

  * ``tv_bregman``, for the split-Bregman total variational denoising;

  * ``bilateral``, for bilateral filter;

  * ``nl_means``, for non-local mean denoising.

* ``wavelet``: contains a dictionary for the definition of the parameter space used to find the best parameter
  combination for the wavelet based denoiser (see :ref:`below <wavelet_denoiser>`). The key of this dictionary are:

  .. _range_example:

  * ``level_range``, it is a list of positive integer numbers specifying range of the possible decomposition levels
    used by the filter for wavelet decomposition. This list should look as follow :math:`[l,L,\delta l]`, where
    :math:`l` is the smallest level used in the parameter search, :math:`L` is the largest level used in the
    parameter search, and :math:`\delta l` is the step. This list produces the following decomposition levels for the
    parameter search: :math:`l,l+\delta l,l+2\delta l,...,L-2\delta l,L-\delta l(,L)`, where the last element is present
    or not depending if :math:`L-l` is an integer multiple of :math:`\delta l`.

  * ``wavelet_family``, name of a discrete wavelet family of the *PyWavelet* library to search only among the
    wavelets of this family during the optimization (see `here <http://wavelets.pybytes.com/>`_ for the list of
    available wavelet families).

  * ``mode_range``, it is a list containing the possible thresholding mode used in the wavelet filter to suppress
    the coefficients containing most of the noise information. The possible values in this list are ``soft`` and
    ``hard``.

  * ``method_range``, it is a list containing the possible methods used in the wavelet filter to define the
    threshold below which suppress the coefficients containing most of the noise information. The possible values
    in this list are ``BayesShrink``  and ``VisuShrink``.

* ``tv_chambolle``: contains a dictionary for the definition of the parameter space used to find the best parameter
  combination for the Chambolle total variational denoiser (see :ref:`below <tv_denoiser>`). The key of this dictionary
  are:

  * ``weights_tvch_range``, it is a list containing the values defining the parameter space for
    the 'weight' parameter of the Chambolle total variation denoiser. This list should have 3 numbers, i.e.
    :math:`[w,W,\delta w]`, generating the range :math:`w,w+\delta w,w+2\delta w,...,W-2\delta w,W-\delta w(,W)`.

* ``tv_bregman``: contains a dictionary for the definition of the parameter space used to find the best parameter
  combination for the split-Bregman total variational denoiser (see :ref:`below <tv_denoiser>`). The key of this
  dictionary are:

  * ``weights_tvbr_range``, it is a list containing the values defining the parameter space for
    the 'weight' parameter of the split-Bregman total variational denoiser. This list should have 3 numbers, i.e.
    :math:`[w,W,\delta w]`, generating the range :math:`w,w+\delta w,w+2\delta w,...,W-2\delta w,W-\delta w(,W)`.

  * ``isotropic_range``: it is a list containing the possible *boolean* value for the 'isotropic' parameter of the
    split-Bregman total variational denoiser, i.e. the parameter selecting the *kind* of optimization problem solved
    with the split-Bregman method.

* ``bilateral``: contains a dictionary for the definition of the parameter space used to find the best parameter
  combination for the split-Bregman total variational denoiser (see :ref:`below <bilateral_denoiser>`). The key of this
  dictionary are:

  * ``sigma_color_range`` it is a list containing the values defining the parameter space for the 'sigma_color'
    parameter of the bilateral filter. This list should have 3 numbers, i.e. :math:`[\sigma_c,\Sigma_c,\delta \sigma_c]`,
    generating the range :math:`\sigma_c,\sigma_c+\delta \sigma_c,\sigma_c+2\delta \sigma_c,...,
    \Sigma_c-2\delta \sigma_c,\Sigma_c-\delta \sigma_c(,\Sigma_c)`.

  * ``sigma_spatial_range`` it is a list containing the values defining the parameter space for the the 'sigma_spatial'
    parameter of the bilateral filter. This list should have 3 numbers, i.e. :math:`[\sigma_s,\Sigma_s,\delta \sigma_s]`,
    generating the range :math:`\sigma_s,\sigma_s+\delta \sigma_s,\sigma_s+2\delta \sigma_s,...,
    \Sigma_s-2\delta \sigma_s,\Sigma_s-\delta \sigma_s(,\Sigma_s)`.

* ``nl_means``: contains a dictionary for the definition of the parameter space used to find the best parameter
  combination for the non-local mean denoiser (see :ref:`below <nl_mean_denoiser>`). The key of this dictionary are:

  * ``patch_size_range``, it is a list containing the values defining the parameter space for the 'patch_size'
    parameter of the non-local mean denoiser. This list should have 3 numbers, i.e. :math:`[s,S,\delta s]`, generating
    the range :math:`s,s+\delta s,s+2\delta s,...,S-2\delta s,S-\delta s(,S)`.

  * ``patch_distance_range``, it is a list containing the values defining the parameter space for the 'patch_distance'
    parameter of the non-local mean denoiser. This list should have 3 numbers, i.e. :math:`[d,D,\delta d]`, generating
    the range :math:`d,d+\delta d,d+2\delta d,...,D-2\delta d,D-\delta d(,D)`.

  * ``h_relative_range``, it is a list containing the values defining the parameter space for the 'h_relative' from
    which the 'h' parameter of the non-local mean denoiser is computed. This list should have 3 numbers, i.e.
    :math:`[h_r,H_r,\delta h_r]`, generating the range :math:`h_r,h_r+\delta h_r,h_r+2\delta h_r,...,
    H_r-2\delta h_r,H_r-\delta h_(,H_r)`.

The plugin-specific parameters contained in this dictionary are:

* ``filter_to_use``: contain the name of the denoiser that is used if the optimization routine is not used (i.e. when
  ``auto_optimize = False``). The currently available denoiser are

  * ``wavelet``, for wavelet based denoising;

  * ``tv_chambolle``, for the Chambolle total variational denoising;

  * ``tv_bregman``, for the split-Bregman total variational denoising;

  * ``bilateral``, for bilateral filter;

  * ``nl_means``, for non-local mean denoising.

* ``filter_params``: list whose elements are the denoiser parameter. Each denoiser parameter have to be specified with
  a list of two elements: the parameter name and the parameter value. For example, to initialize the split-Bregman total
  variational denoiser with ``weight = 0.1``, and ``isotropic=False``, the following list have to be used


  .. code-block::

    [['weight',0.1],
     ['isotropic', False]]


  For a list of the parameters for each denoiser see the
  :ref:`Implementation details section <denoiser_implementation_details>`, where each of these denoiser is briefly
  explained and the reference to their algorithmic implementation is given, which is where the name of all the
  parameters can be found.


When ``auto-optimize = True`` the plugin-specific parameters above are ignored, since the one selected by the
optimization procedure are used. Finally, the meaning of the remaining parameters can be found in
:ref:`General information#Transfomation dictionary <transformation_dictionary>`.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Denoiser <bmiptools.transformation.restoration.denoiser.Denoiser>`.


Use case
========


The typical use of this plugin are:


1. Reduce noise level in the input stack.


.. tip::

    From the practical point of view, the following empirical findings

    1. ``bilateral`` should not be added in the list: most of the time is considered as the best filter despite after
       visual inspection it is not so.

    2. The parameter search for ``nl_means`` can be very time consuming, expecially for big images: consider that when
       it is added to the list.

    3. In general when the optimization is used, the use of a bounding box and a suitable ``fit_step`` value is highly
       recommended in order to drastically reduce the optimization time. The noise properties most of the times are the
       same or very similar in any point of the image. Therefore use the bounding box to select a small region of the
       stack which is sufficiently representing (in terms of "image variability") the stack should not affect the
       denoising performance. Similarly, the noise most of the time does not very to much along the Z-axis. Therefore
       using a suitable value for ``fit_step`` to reduce the number of slices considered in the optimization process,
       can reduce the optimization times.


Application example
===================


As example consider the slice of a stack of a biological sample obtained via SEM, where the noise is
clearly present.


.. image:: ../_images/Plugins/denoiser/pre_denoiser.png
   :class: align-center
   :width: 1500px
   :height: 1536px
   :scale: 40


A zoomed part of the center-top/right part of the slice can be found below. One can clearly see some complex structures
under the vertical stripes.


.. image:: ../_images/Plugins/denoiser/pre_denoiser2.png
   :class: align-center
   :width: 200px
   :height: 200px
   :scale: 200


Applying the denoiser plugin with default setting, except for the use of the bounding box, which was defined in the
central part of the image, the best denoiser with the best parameters has been selected. By applying it, the result
one obtains is the following.


.. image:: ../_images/Plugins/denoiser/post_denoiser.png
   :class: align-center
   :width: 1500px
   :height: 1536px
   :scale: 40


Zooming-in in the same place, one can see that the noise level on the image is reduced.


.. image:: ../_images/Plugins/denoiser/post_denoiser2.png
   :class: align-center
   :width: 200px
   :height: 200px
   :scale: 200


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/denoiser>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


.. _denoiser_implementation_details:

Implementation details
======================


The working principle of the different denoisers available in this plugin, are explained in the subsections below. There
the meaning of the main parameters are clarified, the reference to the library used is given, where the user can find
all parameters of a given filter. Finally the principles behind optimization routine used in the plugin is given.

In case of stack with multiple channels, the Denoiser is applied independently to each channel.


.. _wavelet_denoiser:

Wavelet denoising
-----------------


This plugin use the `skimage implementation <https://scikit-image.org/docs/stable/api/skimage.restoration.
html#skimage.restoration.denoise_wavelet>`_ of the wavelet denoiser, where all the parameter that can be used in the
``filter_param`` field, when the optimization routine is not used, can be found.

The wavelet denoiser of an image is essentially composed by 3 steps [Donoho1994]_. First a multilevel wavelet
decomposition using a certain *wavelet* :math:`w` and up a to certain *decomposition level* :math:`l`. This means to
apply the (single-level) 2D wavelet transform with wavelet :math:`w` iteratively for :math:`l` times to the input image.
Each iterations produces 4 different images with half of the size of the input image (called *subbands*), which are
typically labelled with the letters LL, LH, HL, HH. The LL subband is the one used as input of the next iterations.
This operation will be denoted with the symbol :math:`WD2d[w,l]`.

The "pixel values" of all the subbands obtained for all the level, are called *wavelet coefficients*. The next step in
the wavelet denoising consist in the shrinkage of wavelet coefficients below a certain threshold. Indeed in principle
the wavelet coefficients would be higher in those points where the input image at a given scale correlate with the
chosen wavelet (at that corresponding scale). The noise, being random, should not correlate particularly well with any
wavelet at any level. Therefore, the noise contribution to the wavelet coefficients would be small and more or less
constant for all the subbands. Thus it can be suppressed by eliminating the wavelet coefficients below a certain
threshold. Given a certain threshold :math:`\delta`, two are the popular *thresholding mode*:

* *hard thresholding* mode, which uses the following thresholding function

  .. math::

     y_{hard}(x) = \begin{cases}
                   x &\mbox{ if } |x|>\delta \\
                   0 &\mbox{ otherwise.}
                   \end{cases}

* *soft thresholding* mode, which uses the following thresholding function

  .. math::

     y_{soft}(x) = \begin{cases}
                   \mbox{sign}(x) |x-\delta| &\mbox{ if } |x|>\delta \\
                   0 &\mbox{ otherwise.}
                   \end{cases}

The threshold value :math:`\delta` can be selected according to various criteria. In the current implementation of the
wavelet denoiser used here, two are the one available:

* *ViSu shrink*, which employs an universal threshold for all the subbands, equal to


  .. math::

     \delta = \sigma\sqrt{2\log K}


  where :math:`K` is the total number of pixel of the input image, while :math:`\sigma` is the standard deviation of the
  noise in the image. Typically, :math:`\sigma` is estimated from the image from the median of the absolute value of the
  wavelet coefficients (:math:`MAV`) of the HH subband of the highest decomposition level, via the formula


  .. math::
     :label: euler

     \sigma = \frac{MAV}{0.6745}


* *Bayes shrink*, which employs a subband dependent threshold, equal for the level :math:`l` to


  .. math::

     \delta_l = \frac{\sigma_l^2}{\sqrt{\max(\sigma^2_G-\sigma_l^2,0)}}


  where :math:`\sigma_l` is the variance of the noise in the image estimated using :math:numref:`euler` but using the
  HH subband of the level :math:`l` and not only the highest, while


  .. math::

     \sigma_G^2 = \frac{1}{M} \sum_{j,i} c_{j,i}^2


  where :math:`c_{j,i}` are the wavelet coefficients at the level :math:`l`, and :math:`M` is the number of those
  coefficients. With the 'Bayes shrink' each decomposition level is filtered in a different manner, that is why this is
  an adaptive method for the threshold estimation [Chang2000]_ [Gupta2015]_.

The shrinking operation described here will be denoted with the symbol :math:`Sh[\delta,y]`, where :math:`\delta` is the
threshold selected according to one of the possible criteria, and :math:`y` is one of the two possible thesholding
function.

The last step is the reconstruction of the filtered image, by using the inverse 2D Wavelet decomposition using the same
wavelet :math:`w` and decomposition level `l` using in the beginning, operation denoted by :math:`WD2d^{-1}[w,l]`.

Therefore for the wavelet denoise, given a stack :math:`S(k,j,i)` each slice :math:`S[k](j,i)` is filtered as follow


.. math::

    S[k](j,i) \rightarrow S_{output}[k](j,i) = WD2d^{-1}[w,l](Sh[\delta,y](WD2d[w,l](S[k](j,i))).


.. _tv_denoiser:

TV denoising
------------


This plugin use the skimage implementation bot for the `Chambolle <https://scikit-image.org/docs/stable/api/skimage.
restoration.html#skimage.restoration.denoise_tv_chambolle>`_  and the `split-Bregman <https://scikit-image.org/docs/
stable/api/skimage.restoration.html#skimage.restoration.denoise_tv_bregman>`_ of the total variational denoiser, where
all the parameter that can be used in the ``filter_param`` field, when the optimization routine is not used, can be
found.

Total variational denoising is a techniques based the solution of a suitable optimization problem which is extremely
successful in reducing the noise preserving edges in the input image. In particular, in this technique for a given
input noisy image :math:`I_0`, the denoised image :math:`I_{output}` is the solution of the following problem


.. math::

   I_{output} = \mbox{argmin}_I \mathcal{L}(I;I_0)


where the loss function is

.. math::

   \mathcal{L}[w](I;I_0) = \frac{1}{2} \sum_{j=0}^{N-1}\sum_{i=0}^{M-1} \left(I(j,i)-I_0(j,i)\right)^2 +
                        w\sqrt{ \sum_{j'=0}^{N-1}\sum_{i'=0}^{M-1} \left(\nabla_j I(j',i')^2+\nabla_i I(j',i')^2\right) }


where :math:`I` is an image, :math:`I_0` is the initial image, and :math:`w` is the *weight* parameter of the
loss. In the loss, the gradients of an image have to be understood inn discrete sense. The meaning of this loss is not
difficult to understand:

1. the first term is simply the mean square error between the image :math:`I` and the initial image :math:`I_0`, which
   encode the simple requirement that the deionised image is not to different from the initial one;

2. the second term simply require that the variations between one pixel and its next along the X- and Y-axis is small,
   which is what one should expect for an image without noise, since the variation are slow, while the noise vary a lot
   from one pixel to the next.

Keeping this in mind, one can understand that the *weight* parameter :math:`w` determines how much one requirement is
important with respect to the other. The *Chambolle* [Chambolle2004]_ and *split-Bregman in its isotropic version*
[Goldstein2009]_ [Bush2011]_ are different algorithms which try to solve this problem.


.. note::

   For the *anisotrpic split-Bregman* [Goldstein2009]_ [Bush2011]_, the second term of the loss function changes in

   .. math::

      \sum_{j'=0}^{N-1}\sum_{i'=0}^{M-1} \left(|\nabla_j I(j',i')| + |\nabla_i I(j',i')|\right).


Therefore, for the total variational denoiser, given a stack :math:`S(k,j,i)` each slice :math:`S[k](j,i)` is filtered
as follow


.. math::

    S[k](j,i) \rightarrow S_{output}[k](j,i) =  \mbox{argmin}_S \mathcal{L}[w](S;S[k](j,i)).


.. _bilateral_denoiser:

Bilateral filter
----------------


This plugin use the `skimage implementation <https://scikit-image.org/docs/stable/api/skimage.restoration.
html#skimage.restoration.denoise_bilateral>`_ of the bilateral filter, where all the parameter that can be used in the
``filter_param`` field, when the optimization routine is not used, can be found.

This filter simply perform the convolution of the input image with a filter having *input-dependent* kernel


.. math::

   g[\sigma_s,\sigma_c](j,i,j',i',I) = \frac{1}{C_{j,i}}
                                       \exp{\left(-\frac{(j-j')^2+(i-i')^2}{2\sigma_s^2}
                                       -\frac{(I(j,i)-I(j',i'))^2}{2\sigma_c^2}\right)}


where


.. math::

   C_{j,i} = \sum_{j'} \sum_{i'}
             \exp{\left(-\frac{(j-j')^2+(i-i')^2}{2\sigma_s^2}-\frac{(I(j,i)-I(j',i'))^2}{2\sigma_c^2}\right)}

play the role of a pixel-dependent normalization constant. When convolved with the input image this filter perform a
gaussian smoothing both in the coordinate space (with spatial standard deviation :math:`\sigma_s`) and in the color
space (with color standard deviation :math:`\sigma_c`) [Paris2009]_.

Therefore, the denoising with spatial filter consist in the following. Given a stack :math:`S(k,j,i)` each slice
:math:`S[k](j,i)` is filtered as follow


.. math::

    S[k](j,i) \rightarrow S_{output}[k](j',i') =  \sum_{j',i'} g[\sigma_s,\sigma_c](j,i,j',i',S[k](j',i')) S[k](j',i')


.. _nl_mean_denoiser:

Non-local mean denoising
------------------------


This plugin use the `skimage implementation <https://scikit-image.org/docs/stable/api/skimage.restoration.
html#skimage.restoration.denoise_nl_means>`_ of the non-local mean denoiser, where all the parameter that can be used in the
``filter_param`` field, when the optimization routine is not used, can be found.

This denoising technique perform the noise reduction in an image, by using similar regions in the input image for the
computation of the denoised one [Buades2011]_. For a given image :math:`I(j,i)`, the


.. math::

   NL[f,h](I(j,i)) = \frac{1}{C(j,i)} \sum_{j',i'} \exp{\left(-\frac{\max(d(j,i;j'i')^2-2\sigma^2,0)}{h^2}\right)}


where :math:`sigma` is the standard deviation of the noise in the image, :math:`h` is the filtering parameters, since it
determine how much the noise is suppressed. :math:`d(j,i;j'i')` is the distance measure used to measure the similarity
among two pixels, which is defined to be equal to


.. math::

   d(j,i;j'i') = \frac{1}{(2f+1)^2} \sum_{(a,b) \in B((0,0),f)} \left( I(j+a,i+b) - I(j'+a,i'+b) \right)^2


with :math:`B((j,i),f)` denotes the :math:`(2f+1) \times (2f+1)` square patch centered in the pixel :math:`(j,i)`. From
this definition one can see that the similarity of two pixel is based not only on its value, but also on the geometrical
(and color) information in its surrounding. This implement the idea of using similar regions in an image to compute the
denoised value of a given pixel. Therefore, the non-local mean denoising for a given pixel can be understood as a
weighted mean of all the pixels in the image, where the weights depends on the similarities between pixels. From the
formula above one can see that regions, having distance :math:`d < 2\sigma`, have the maximum weight equal to 1, while
as far as the distance is 2 times bigger that the noise standard deviation of the image the weights start to decrease.
In bmiptool, the :math:`h` paramter is not given directly. Instead an :math:`h_{relative}` parameter is used, from which
:math:`h` is computed with the simple formula below


.. math::

   h = \sigma h_{relative}


where :math:`\sigma` is the estimated standard deviation of the noise present on the input image.


.. note::

   The originally proposed method has been later improved to increase the computational efficieny [Darbon2008]_.
   This improvement was reached with a little but clever modification of the weight function, which makes the
   computation of the new weights independent on the patch size.


Therefore, for the non-local mean denoiser, given a stack :math:`S(k,j,i)` each slice :math:`S[k](j,i)` is filtered
as follow


.. math::

    S[k](j,i) \rightarrow S_{output}[k](j,i) =  NL[f,h](S[k](j,i)).


.. _denoiser_optimization_details:

Optimization details
--------------------


The optimization routine of the denoiser plugin is based on the principe of J-invariance [Batson2019]_. In a nutshell,
given a certain denoiser :math:`f` depending on a set of parameters :math:`\alpha_1,\alpha_2,\cdots` the idea is to
find the best parameters by minimizing the following loss


.. math::

    \mathcal{L}(\alpha_1,\alpha_2,\cdots) = \frac{1}{N}\sum_{(i,j)}\|f[\alpha_1,\alpha_2,\cdots](I(j,i))-I(j,i)\|_2^2


where :math:`I` is the noisy image, :math:`N` is the total number of pixels, and the sum is over the pixels of the
image. This loss simple say that the best parameters are the one for which the mean square error between the filtered
image and the initial noisy image is smaller. It can be proved, that finding the minimum of this loss (i.e. find the
best parameters) is equivalent in finding the minimum of


.. math::

   \frac{1}{N}\sum_{(i,j)}\|f[\alpha_1,\alpha_2,\cdots](I(j,i))-I_0(j,i)\|_2^2


where :math:`I_0` is the true image without noise, *provided that the filter* :math:`f` *is J-invariant*. J-invariant
means that the output of the filter in the pixel :math:`(j,i)` does not depend on a set of pixels :math:`J` containing
:math:`(j,i)` itself. This means that for a J-invariant filter, the minimization of
:math:`\mathcal{L}(\alpha_1,\alpha_2,\cdots)` allows to find the parameters of the filter such that its output is as
closed as possible (in terms of the MSE) to the true image without noise. Given a classical filter, a J-invariant
version of it can be obtained by masking: for teh computation of the filter output in the pixel :math:`(j,i)`, the
region :math:`J` around each pixel :math:`(j,i)` of the input is masked with the mean value of the pixels
around this region, leaving the rest of the input image unchanged. By following this procedure, it is possible to obtain
the J-invariant version of a given filter :math:`f`. Empirically, it has been observed that the optimal
parameters for the J-invariant version of a filter are very close to the optimal parameter of the filter, most of the
times.


Further reading
===============


Articles:

.. [Chang2000] "Adaptive wavelet thresholding for image denoising and compression." - Chang, S. Grace, Bin Yu, and
   Martin Vetterli -Image Processing, IEEE Transactions on 9.9 (2000): 1532-1546. DOI:10.1109/83.862633

.. [Donoho1994] "Ideal spatial adaptation by wavelet shrinkage." - D. L. Donoho and I. M. Johnstone. - Biometrika 81.3
   (1994): 425-455. DOI:10.1093/biomet/81.3.425

.. [Gupta2015] "Image Denoising Using Bayes Shrink Method Based On Wavelet Transform" - Payal Gupta and Amit Garg -
   International Journal of Electronic and Electrical Engineering. Volume 8, Number 1 (2015), pp. 33-40

.. [Chambolle2004] "An algorithm for total variation minimization and applications" - Chambolle, A. - Journal of
   Mathematical Imaging and Vision. 20 (2004): 89–97

.. [Goldstein2009] "The split Bregman method for L1-regularized problems." - Goldstein, Tom, and Stanley Osher  - SIAM
   journal on imaging sciences 2.2 (2009): 323-343.

.. [Bush2011] "Bregman algorithms" - Bush J. - Senior Thesis (2011), `<https://web.math.ucsb.edu/~cgarcia/UGProjects/
   BregmanAlgorithms_JacquelineBush.pdf>`_

.. [Paris2009] "Bilateral Filtering: Theory and Applications" - Paris S., Kornprobst P., Tumblin J., Durand F. -
   Foundations and Trends® in Computer Graphics and Vision: Vol. 4: No. 1 (2009), pp 1-73.
   http://dx.doi.org/10.1561/0600000020

.. [Buades2011] "Non-Local Means Denoising" - Antoni Buades, Bartomeu Coll, and Jean-Michel Morel - Image Processing On
   Line, 1 (2011), pp. 208–212. https://doi.org/10.5201/ipol.2011.bcm_nlm

.. [Darbon2008] "Fast nonlocal filtering applied to electron cryomicroscopy" - J. Darbon, A. Cunha, T. F. Chan,
   S. Osher and G. J. Jensen,  2008 5th IEEE International Symposium on Biomedical Imaging: From Nano to Macro, 2008,
   pp. 1331-1334, doi: 10.1109/ISBI.2008.4541250.

.. [Batson2019] "Noise2Self: Blind Denoising by Self-Supervision" - Joshua Batson, Loic Royer Proceedings of the 36th
   International Conference on Machine Learning, PMLR 97:524-533, 2019.