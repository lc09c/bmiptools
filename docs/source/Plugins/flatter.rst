=======
Flatter
=======


.. admonition:: Cropper in a nutshell.
   :class: note

   1. Plugin to remove slowly-varying brightness variation on the slices of the input stack;
   2. This plugin is multichannel;
   3. This plugin can be optimized on the stack;
   4. Python API reference: :py:class:`bmiptools.transformation.restoration.flatter.Flatter`.


This plugin can be used remove in the slices of a stack the slowly-varying brightness variation.


The Python API reference of the plugin is :py:class:`bmiptools.transformation.restoration.flatter.Flatter`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.


.. code-block::

    {'auto_optimize': True,
    'optimization_setting':{'sigma_deriv_smoother': 5,
                           'sigma_min': 5,
                           'sigma_max': 'auto',
                           'sigma_step': 5,
                           'entropy_setting':{'image_range': (0,1),
                                              'derivative_range': (0,0.039),
                                              'n_bins': 1024},
                           'fit_step': 10,
                           'regularization_strength': 1,
                           'use_early_stopping': True,
                           'patience': 5},
    'sigma_low_pass': 80}


The optimization-related plugin-specific parameters contained in the ``optimization_setting`` field of this dictionary
are:


* ``sigma_deriv_smoother``: it is the standard deviation used to compute the image derivative. Its default value is
  ``5`` is usually a good choice.

* ``sigma_min``: is the smallest value of the parameter ``sigma_low_pass`` used during the optimization. This
  value is also used for the definition of the loss parameter (see :ref:`below <flatter_optimization_loss>`).

* ``sigma_max``: is the maximum value of the parameter ``sigma_low_pass`` used during the optimization. It can be:

                    * the actual maximum value of ``sigma_low_pass``;

                    * ``'auto'``, to automatically infer from the image shape the maximum value of ``sigma_low_pass``,
                      imposing the filter size to be not to big with respect to the image.

* ``sigma_step``: is the step size used for the variation of ``sigma_low_pass`` during the optimization routine.

* ``entropy_setting``: its a dictionary containing the setting to compute the entropy od an image and of its derivative
  using histograms having the same binning, so that they are compatible. The keys of this dictionary are:

    * ``image_range``, which is a tuple containing the minimum and maximum value of an image (i.e. the dynamic range
      of the image)  which are used to define the histogram range for the image;

    * ``derivative_range``,  which is a tuple containing the minimum and maximum value of the modulus of the
      derivative of the image (i.e. the dynamic range of the modulus of the image derivative) which are used to
      define the histogram range for the image derivative;

    * ``n_bins``, which is the number of bins used to compute the histograms needed in the optimization.

* ``regularization_strength``: is the strength of the regularization used during the plugin optimization.

* ``use_early_stopping``: if ``True`` an early stopping policy for the line-search optimization is used, with patience
  specified in the field below.

* ``patience``: patience of the early stopping policy, i.e. the number of epochs with no improvement in the loss before
  to stop the optimization routine.


The plugin-specific parameters contained in this dictionary are:


* ``sigma_low_pass``: it is  the standard deviation parameter of the low-pass filter in the flatter transformation.
  For stack with multiple channels, a list with the low-pass filter parameters for each channel can be given.


When ``auto-optimize = True`` the plugin-specific parameters above are ignored, since the one selected by the
optimization procedure are used. Finally, the meaning of the remaining parameters can be found in
:ref:`General information#Transfomation dictionary <transformation_dictionary>`.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Flatter <bmiptools.transformation.restoration.flatter.Flatter>`.


Use case
========


The typical use of this plugin are:


1. remove the slowly-varying brightness in the input stack;

2. flatten the image in order to make it easier the finding of an universal threshold to segment objects;

3. when charging is particularly strong and diffuse on the input slices, part of the charging can be removed/reduced
   with this plugin.


.. tip::

   The following things turn out to be useful, from a practical point of view.

   1. When slow brightness variation are expected for some reason, this plugin may simply remove part of the information
      content. Therefore its use is not suggested in this case.

   2. It is warmly suggested to avoid to change the ``entropy_setting``, unless there is a good reason for doing that.


Application example
===================


As example consider the slice of a stack of a biological sample obtained via cryo-FIB-SEM, where the brightness slowly
increase moving from the left to the top-right of the image. In order to make this artifact clearly visible in the slice
showed below, a preliminary standardization step (using the :doc:`standardizer` plugin with
``standardization_type = '0/1'``) has been applied.


.. image:: ../_images/Plugins/flatter/pre_flatter.png
   :class: align-center
   :width: 1000px
   :height: 1000px
   :scale: 60


After the application of the Flatter plugin with the default parameters (i.e. the one present in the
``empty_transformation_dictionary`` of the plugin), the result obtained is given below.


.. image:: ../_images/Plugins/flatter/post_flatter.png
   :class: align-center
   :width: 1000px
   :height: 1000px
   :scale: 60


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/flatter>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


Implementation details
======================


The plugin simply subtract from the input image a low-pass filtered version of the same image. Low-pass filtering is
obtained with the application of a simple gaussian filter with standard deviation :math:`\sigma_{LP}`. More precisely,
given an image :math:`I(j,i)` and let :math:`G[\sigma_{LP}]` be a gaussian kernel with standard deviation
:math:`\sigma_{LP}`, the flattened version of the input image, :math:`I_{flat}(j,i)` is obtained by simply using the
equation below


.. math::

   I_{flat}(j,i) = I(j,i) - (G[\sigma_{LP}]*I)(j,i)


where :math:`*` denotes the 2d convolution. The operation above will be denotes with the symbol :math:`FL[\sigma_{LP}]`.
The cut-off (spatial) frequency of the gaussian filter, is clearly determined by the kernel standard deviation. In
practical terms, the details in the input image with are significantly smaller than :math:`\sigma_{LP}` are are de fact
eliminated in the  gaussian filter output, leaving unchanged only those structures of the image which are significantly
larger than :math:`\sigma_{LP}`. These remaining structure are then subtracted from the original image. Therefore the
:math:`\sigma_{LP}` parameter in this plugin defines the scale below which the brightness variation are considered
slowly-varying.

Summarizing, given a :math:`K \times J \times I` stack :math:`S(k,j,i)`, the flatter plugin acts on each slice
:math:`S[k](j,i)` as follow


.. math::

   S[k](j,i) \rightarrow S_{output}[k](j,i) = FL[\sigma_{LP}](S[k])(j,i).


In case of stack with multiple channels, the Flatter is applied independently to each channel.


Optimization details
--------------------


The optimization routine try to find a reasonable value for :math:`\sigma_{LF}`. It is reasonable both in the sense of
preserving the image content, and in the sense of computational resources needed. The optimization itself is
multichannel: when more than one channel is present in the input stack, the best parameters is found for each channel
independently.

For the optimization of this plugin, the shannon entropies associated to the histogram of image and the histogram of the
(modulus of the) gradient of it turns out to be useful. Given an image :math:`I`, let :math:`{h_I(b)}_{b=0}^{N-1}` be
its :math:`N` bin histogram, obtained by dividing the image range in :math:`N` intervals and counting how many times a
pixel has its value falling in a given bin. The shannon entropy associated to this image can be defined as follow


.. math::

   H(I) = -\sum_{b=0}^{N-1} \tilde{h}_I(b)\log \tilde{h}_I(b)


where :math:`\tilde{h}_I(b) = h_I(b)/\sum_{b'}h_I(b')` is the normalized histogram. Given an image :math:`I_0(j,i)` a
slowly varying would contribute to the image histogram as a more or less constant contribution to all the non-zero bin
of the histogram. Therefore the removal of this contribution would lead to a decreasing in the image entropy. On the
other hand if value of the image entropy decrease too much, this may indicate that less and less details are present in
image. To counterbalance that, two things can be taken into account:

* given the modulus of the gradient of the image, :math:`dI(j,i) = \sqrt{[\nabla_y I(j,i)]^2+[\nabla_x I(j,i)]^2}`
  (here :math:`\nabla_l` for :math:`l=x,y` corresponds to the a discrete differentiation followed by a suitable
  smoothing, as usually computed the derivative for an image), the entropy of :math:`dI` is expected to grow when more
  details (edges in particular) are present. Therefore its inverse is expected to be very small if the flatter preserve
  as many details as possible when applied to the input image.

* the contribution due to a slowly-varying component is not only more or less constant for all the non null bins, but is
  also small. Therefore, it is not expected that entropy of the flatten image is too differnt with respect to the input
  image.

The three terms of the loss below contain the 3 conditions explained above. Given a image :math:`I(j,i)`, obtained by
applying the flatter to the corresponding input image :math:`I_0(j,i)`, one can define the following:


.. _flatter_optimization_loss:

.. math::

   \mathcal{L}_0(I) = \frac{1}{3} \left[ \alpha H(I)+\frac{\beta}{H(dI)} + \gamma |H(dI)-H(dI_0)|\right],


where :math:`\alpha`, :math:`\beta` and :math:`\gamma` are three parameters which are used to make the ranges of the
three terms in the loss comparable. The combination below gives good results


.. math::

   \alpha = \frac{1}{H(I_{min})} \mbox{ , } \beta = H(dI_{min})
   \mbox{ , } \gamma = \frac{1}{|H(dI_{min})-H(dI_0)|},


where :math:`I_{min} = FL[\sigma_{LP}^{min}](I)` and :math:`dI_{min} = FL[\sigma_{LP}^{min}](dI)`.
Since the typical value of :math:`\sigma_{LP}` is usually high, the convolution operation turns out to be particularly
demanding from the computational point of view. From an empirical point of view, it has been observed that little or no
visible is obtained by increasing too much the value of :math:`\sigma_{LP}`. For this reason a regularization term is
added to the previous loss


.. math::

   \mathcal{L}_{reg}(\sigma_{LP}) = \frac{(\sigma_{LP} - \sigma_{LP}^{min})^n}{\sigma_{LP}^{max}},


where :math:`\sigma_{LP}^{min}` and :math:`\sigma_{LP}^{max}` are the minimum maximum allowed values for
:math:`\sigma_{LP}`, while :math:`n \geq 2`. To reduce the influence of this term for the low value of
:math:`\sigma_{LP}`, an high value of :math:`n` is be used. The loss function use in the optimization routine is the
following


.. math::

   \mathcal{L}(I,\sigma_{LP}) = \mathcal{L}_0(I) + \lambda\mathcal{L}_{reg}(\sigma_{LP}),


where :math:`\lambda` is a parameter regulating the strength of the regularization. Given a :math:`K \times J \times I`
stack :math:`S(k,j,i)` take a collection of its slices :math:`\{S[k](j,i)\}_{k \in V_K}` where
:math:`V_K \subset \{0,1,\cdots,K-1\}` (i.e. the subset of slices selected for the optimization), then the
flatter optimization routine solve the following problem


.. math::

   \sigma_{LP}^{best} = \mbox{argmin }_{\sigma_{LP}}  \sum_{k \in V_K}\mathcal{L}(FL[\sigma_{LP}](S[k]),\sigma_{LP}).


Further details
===============


Websites:

* `Shannon entropy on wikipedia <https://en.wikipedia.org/wiki/Entropy_(information_theory)>`_

