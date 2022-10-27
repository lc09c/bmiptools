============
Denoiser DNN
============


.. admonition:: Denoiser DNN in a nutshell.
   :class: note

   1. Plugin to crop region of a stack;
   2. This plugin is **not** multichannel;
   3. This plugin can be optimized on a stack;
   4. Python API reference: :py:class:`bmiptools.transformation.restoration.denoiser.DenoiserDNN`.


This plugin can be used to reduce the noise level on the slices of a stack by using Deep Neural Network based
techniques. In particular, in this plugin 2d and 3d Noise2Void denoiser are available.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.restoration.denoiser.DenoiserDNN`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.


.. code-block::

   {'auto_optimize': True,
   'optimization_setting': {'tested_filters_list': ['n2v_2d'],
                            'n2v_2d': {'unet_kern_size_2d_list': [3,5,7],
                                       'train_batch_size_2d_list': [128],
                                       'n2v_patch_shape_2d_list': [64],
                                       'train_epochs_2d_list': [30],
                                       'train_loss_2d_list': ['mse','mae'],
                                       'n2v_manipulator_2d_list': ['uniform_withCP','normal_withoutCP',
                                                                   'normal_additive','normal_fitted'],
                                       'n2v_neighborhood_radius_2d_list':[5,10,15,20]
                                       },
                            'n2v_3d': {'unet_kern_size_3d_list': [3,5,7],
                                       'train_batch_size_3d_list': [128],
                                       'n2v_patch_shape_3d_list': [(32,64,64)],
                                       'train_epochs_3d_list': [30],
                                       'train_loss_3d_list': ['mse','mae'],
                                       'n2v_manipulator_3d_list': ['uniform_withCP','normal_withoutCP',
                                                                   'normal_additive','normal_fitted'],
                                       'n2v_neighborhood_radius_3d_list': [5,10,15,20]
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


The optimization-related plugin-specific parameters contained in the ``optimization_setting`` field of this dictionary
are:

* ``tested_filter_list``: contains the list of denoiser that are compared among each other during the optimization. The
  currently available denoiser are:

  * ``'n2v_2d'``, for 2d Noise2Void denoiser;

  * ``'n2v_3d'``, for 3d Noise2Void denoiser.

* ``n2v_2d``: contains a dictionary which is used to define the parameter space used for the optimization of the 2d
  Noise2Void denoiser. It contains the following keys:

  * ``unet_kern_size_2d_list``, contains a list of all the possible kernel sizes of the convolution layers used in the
    2d Noise2Void which are tested during the hyperparameters optimization routine. The kernel size can be equal only
    to 3,5 or 7. Putting other numbers in this list would give rise to errors.

  * ``train_batch_size_2d_list``, contains a list of all the possible batch sizes used for the training of the 2d
    Noise2Void model which are tested during the hyperparameters optimization routine.

  * ``n2v_patch_shape_2d_list``, contains a list of the shapes of all the possible patches used in the Noise2Void
    which are tested during the hyperparameters optimization routine. The shape can be specified as a single integer
    number, meaning that a square patch of that size is used, or a usual tuple according the usual `numpy convention
    <https://numpy.org/devdocs/user/quickstart.html#the-basics>`_.

  * ``train_epochs_2d_list``, contains a  list of all the possible epoch parameter used for the training of the 2d
    Noise2Void model which are tested during the hyperparameters optimization routine.

  * ``train_loss_2d_list``, contains a list of all the possible loss function for the training of the 2d
    Noise2Void model which are tested during the hyperparameters optimization routine. This parameter can be:

    * ``'mse'``;

    * ``'mae'``.

  * ``n2v_manipulator_2d_list``, contains a list of all the possible 'n2v_manipulator' parameter used for the training
    of the 2d Noise2Void model which are tested during the hyperparameters optimization routine. The 'n2v_manipulator'
    is the criteria used to replace the value of the masked pixels during the Noise2Void training. This parameter can
    be:

    * ``'uniform_withCP'``, to replace the masked pixel with a randomly selected pixel of the patch *with* the pixel to
      mask;

    * ``'normal_withoutCP'``, to replace the masked pixel with a randomly selected pixel of the patch *without* the
      pixel to mask;

    * ``'normal_additive'``, to replace the masked pixel with a pixel having the value of the pixel itself plus some
      guassian noise with 0 mean standard deviation equal to the parameters specified in the
      ``n2v_neighborhood_radius_2d_list`` field ;

    * ``'normal_fitted'``, to replace the masked pixel with a pixel having the value of the pixel itself plus some
      guassian noise with 0 mean and standard deviation estimated from the patches;

    * ``'idenitity'``, the pixel is not replaced.

  * ``n2v_neighborhood_radius_2d_list``, contains a list of all the possible radii used to define the neighborhood of
    a pixel used in the training of the Noise2Void models which are tested during the hyperparameters optimization
    routine.

* ``n2v_3d``: contains a dictionary which is used to define the parameter space used for the optimization of the 2d
  Noise2Void denoiser. It contains the same keys of the previous dictionary, except that '3d' have to be used in the
  name rather than '2d'.

The plugin-specific parameters contained in this dictionary are:

* ``filter_to_use``: it contains the name of the filter chosen. This field is ignore when the auto-optimization is done.
  It can be:

  * ``'n2v_2d'``, for 2d Noise2Void denoiser;

  * ``'n2v_3d'``, for 3d Noise2Void denoiser.

* ``filter_params``: list whose elements are the denoiser parameter. Each denoiser parameter have to be specified with
  a list of two elements: the parameter name and the parameter value. This field is ignored when the plugin optimization
  is done, and in that case the parameter of the best filters found during the optimization routine are used.
  For manual specification of the parameters of the filter available in this plugin, see https://github.com/juglab/n2v
  (in particular in the 'n2v/models/n2v_config.py' file). It has to be specified as below

  .. code-block::

     [[name_parameter_1, value_parameter_1], [name_parameter_2, value_parameter_2], ...].

* ``trained_n2v_setting``: it is a dictionary containing the setting relative to the loading/saving of trained n2v
  models. This dictionary has the following fields:

  * ``use_trained_n2v_model``, a boolean such that if True, a trained n2v model is loaded from the path contained in the
    field ``'path_to_trained_n2v_model'``.

  * ``path_to_trained_n2v_model``, which contain the path to a trained n2v model. This field is ignored if the previous
    field is ``False``.

  * ``save_trained_n2v_model``, a boolean such that if True after training, the best n2v model is saved a the path
    contained in the field ``'saving_path'``.

  * ``saving_path``, which containt the path where the best n2v model is saved. This field is ignored if the previous
    field is ``False``.

When ``auto-optimize = True`` the plugin-specific parameters above are ignored, since the one selected by the
optimization procedure are used. Finally, the meaning of the remaining parameters can be found in
:ref:`General information#Transfomation dictionary <transformation_dictionary>`.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`DenoiserDNN <bmiptools.transformation.restoration.denoiser.DenoiserDNN>`.


Use case
========


The typical use of this plugin are:


1. Reduce noise level in the input stack.


.. tip::

    From the practical point of view, the following empirical findings

    1. It has been observed that use the optimization routine for the hyperparameter search does not perform well when
       2d and 3d denoiser are compared among each other. Therefore, the option
       ``tested_filter_list = ['n2v_2d', 'n2v_3d']`` is not advised. Hyperparamter search based on the optimization
       routine of this plugin, has shown to perform well when restricted to 2d models only or 3d models only, i.e. with
       the option ``tested_filter_list = ['n2v_2d']`` or ``tested_filter_list = ['n2v_3d']``.

    Keep also in mind that, for the application of 3d Noise2Void model, the stack has to be already aligned, for
    example with the :doc:`Registrator plugin <registrator>`.


Application example
===================



As example consider the slice of a stack of a biological sample obtained via SEM, where the noise is
clearly present.


.. image:: ../_images/Plugins/denoiserdnn/pre_denoiserdnn.png
   :class: align-center
   :width: 1500px
   :height: 1536px
   :scale: 40


A zoomed part of the center-top/right part of the slice can be found below. One can clearly see some complex structures
under the vertical stripes.


.. image:: ../_images/Plugins/denoiserdnn/pre_denoiserdnn2.png
   :class: align-center
   :width: 200px
   :height: 200px
   :scale: 200


Applying the denoiserDNN plugin with default setting (i.e. with using a 2d noise2void model), except for the use of the
bounding box, which was defined in the central part of the image, the best hyperparameters for the noise2void model has
been selected. By applying the trained model with these hyperparameters, the result one obtains is the following.


.. image:: ../_images/Plugins/denoiserdnn/post_denoiserdnn.png
   :class: align-center
   :width: 1500px
   :height: 1536px
   :scale: 40


Zooming-in in the same place, one can see that the noise level on the image is reduced.


.. image:: ../_images/Plugins/denoiserdnn/post_denoiserdnn2.png
   :class: align-center
   :width: 200px
   :height: 200px
   :scale: 200


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/denoiserdnn>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


Implementation details
======================


This plugin use the original implementation of Noise2Void which can be found `here <https://github.com/juglab/n2v>`_.
All the parameters can be found in the 'n2v/models/n2v_config.py' file ot that repository, where a brief explanation of
their meaning is given. For some of them, the original work [Krull2019]_ may help in clarifying the meaning.

The Noise2Void idea can be easily understood by looking the previous work about denoising with deep neural network. More
precisely the Noise2Noise work [Lehtinen2018]_ can be very helpful. In Noise2Noise the idea is the following. Consider
two noisy images reproducing exactly the same object (i.e. the image content is the same but the noise, being random, is
different). Given a dataset of couples of this kind, it is possible to train a deep neural network in the following
manner. For any couple in the dataset, one of the two images is given as network input and the other as target. What has
been observed is that, since the network cannot learn random input-output relation, the only thing that the network can
learn to reproduce is the image without noise, which is the same for both the images of the couple. Noise2Void goes one
step further showing that by masking the value of a pixel in the input of the network, and giving this pixel value as
target, the network can learn to denoise the image. Again, since the network cannot learn to reproduce the random
component in the pixel value, the best it can do is to estimate the deterministic component the masked pixel would have
based on the information available in the surrounding pixels. This procedure, if done exactly as described here is
very inefficient, and the Noise2Void authors derive an approximated procedure, which speed up the network training a
lot.

Summarizing given a stack :math:`S(k,j,i)` and call :math:`N2V_{2d}[\alpha]` and :math:`N2V_{3d}[\alpha]` represent
the trianed 2d and 3d Noise2Void model, where :math:`\alpha` represents the set of the possible hyperparameters of the
network. In the 2d case, given a slice :math:`S[k](j,i)` the output stack is composed as follow


.. math::

   S[k](j,i) \rightarrow S_{output}[k](j,i) = N2V_{2d}[\alpha]( S[k](j,i) ).


In the 3d case, the network is applied to the whole stack directly, therefore


.. math::

   S(k,j,i) \rightarrow S_{output}(k,j,i) = N2V_{3d}[\alpha]( S(k,j,i) ).


Optimization details
--------------------


The optimization routine of this plugin is done in order to find the best combination among (a reasonable subset of)
the possible hyperparameters of network, and is based on the J-invariance principle [Batson2019]_. A brief discussion of
the J-invariance and why it can be used for this kind of optimization can be found
:ref:`here <denoiser_optimization_details>`. Despite the Noise2Void training scheme does not guarantee the trained model
to be J-invariant (see section 2 in [Batson2019]_), it has been empirically observed that the model with hyperparameters
selected using the J-invariance criteria lead to very good results.


Further reading
===============


Articles:


.. [Lehtinen2018] "Noise2Noise: Learning Image Restoration without Clean Data" - Jaakko Lehtinen, Jacob Munkberg,
   Jon Hasselgren, Samuli Laine, Tero Karras, Miika Aittala, Timo Aila - https://arxiv.org/abs/1803.04189

.. [Krull2019] "Noise2Void - Learning Denoising from Single Noisy Images" - Alexander Krull, Tim-Oliver Buchholz,
   Florian Jug - https://arxiv.org/pdf/1811.10980.pdf

.. [Batson2019] "Noise2Self: Blind Denoising by Self-Supervision" - Joshua Batson, Loic Royer Proceedings of the 36th
   International Conference on Machine Learning, PMLR 97:524-533, 2019.
