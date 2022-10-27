============
Standardizer
============


.. admonition:: Standardizer in a nutshell.
   :class: note

   1. Plugin for image dynamic standardization;
   2. This plugin is multichannel;
   3. Python API reference: :py:class:`bmiptools.transformation.dynamics.standardizer.Standardizer`.


This plugin can be used to rescale and shift the image dynamics. It is a global transformation (the same for all the
voxels of the stack) and has no practical effect on the visualization. Image readers which use relative color range
would not show any difference with the original image, while the ones which use absolute color range may show some
variation. Keep in mind that this variation is apparent, since it depends on how the image is read by the image reader
software.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.dynamics.standardizer.Standardizer`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.

.. code-block::

    {'standardization_type': 'mean/std'
     'standardization_mode': 'stack'
    }

The plugin-specific parameters contained in this dictionary are:

    * ``standardization_type``: Option selecting standardization methods used by the plugin. The currently implemented
      methods are:

        * ``-1/1``: all the values in the image are suitably rescaled between -1 and 1.

        * ``0/1``: all the values of the image are suitably rescaled between 0 and 1.

        * ``mean/std``: the image will have zero mean and standard deviation 1.

    * ``standardization_mode``: Option selecting how the standardization parameters are computed. The available modes
      are:

        * ``slice-by-slice``: the standardization parameters are computed for each slice.

        * ``stack``: the standardization parameters are computed considering the whole stack.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__`` method of the
class :py:class:`Standardizer <bmiptools.transformation.dynamics.standardizer.Standardizer>`


Use case
========


The typical use of this plugin is mainly technical. They are:


1. Increase the dynamics of the image;

2. Rescale the image value through a pipeline, useful when the next plugin need input values with a restricted
   dynamics (as is the case of man);

3. In case the input image is of type 'int', the ``0/1`` mode change the image type to 'float' in a way that is
   typically compatible with the common image readers.


.. attention::

   The effect of this plugin on a stack may depends on the image reader used to visualize the stack. Certain image
   readers implicitly standardize the images when they are reader: in this case the this plugin would not affect the
   visualization (despite the value of the pixels are changed in any case).



Application example
===================


As example consider the slice of a stack of a biological sample obtained via cryo-FIB-SEM, where the brightness slowly
increase moving from the left to the top-right of the image.


.. image:: ../_images/Plugins/standardizer/pre_standardizer.png
   :class: align-center
   :width: 1024px
   :height: 1024px
   :scale: 60


After the application of the Standardizer plugin with ``standardization_type = '0/1'`` and
``standardization_mode = 'slice-by-slice'``, the result obtained is given below.


.. image:: ../_images/Plugins/standardizer/post_standardizer.png
   :class: align-center
   :width: 1024px
   :height: 1024px
   :scale: 60


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/standardizer>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


Implementation details
======================


Let :math:`S(k,j,i)` be a single-channel :math:`K \times J \times I` stack, and let


* :math:`M = \max_{k,j,i} S(k,j,i)` be the maximum of the whole stack,

* :math:`m = \min_{k,j,i} S(k,j,i)` be the minimum of the whole stack,

* :math:`\mu = \frac{1}{KJI}\sum_{k=0}^{K-1}\sum_{j=0}^{J-1}\sum_{i=0}^{I-1} S(k,j,i)` be the mean value of the stack,

* :math:`\sigma = \sqrt{\frac{1}{KJI}\sum_{k=0}^{K-1}\sum_{j=0}^{J-1}\sum_{i=0}^{I-1} (S(k,j,i)-\mu)^2}` be the standard
  deviation of the stack.

* :math:`M_k = \max_{j,i} S(k,j,i)` be the collection of all the maxima of each slice :math:`k`,

* :math:`m_k = \min_{j,i} S(k,j,i)` be the collection of all the minima of each slice :math:`k`,

* :math:`\mu_k = \frac{1}{JI}\sum_{j=0}^{J-1}\sum_{i=0}^{I-1} S(k,j,i)` be the collection of all the mean values of
  each slice :math:`k`,

* :math:`\sigma_k = \sqrt{\frac{1}{JI}\sum_{j=0}^{J-1}\sum_{i=0}^{I-1} (S(k,j,i)-\mu_k)^2}` be the collection of all the
  standard deviation of each slice :math:`k`.


Assume to use the plugin with ``standardization_mode = 'stack'``. For the ``-1/1`` standardization type, the input stack
:math:`S(k,j,i)` is transformed as follow


.. math::

    S(k,j,i)    \rightarrow     S_{output}(k,j,i) = 2\frac{S(k,j,i)-m}{M-m}-1.


For the ``0/1`` standardization type, the input stack :math:`S(k,j,i)` is transformed as follow


.. math::

    S(k,j,i)    \rightarrow     S_{output}(k,j,i) = \frac{S(k,j,i)-m}{M-m}.


For the ``mean/std`` standardization mode, the input stack :math:`S(k,j,i)` is transformed as follow


.. math::

    S(k,j,i)    \rightarrow     S_{output}(k,j,i) = \frac{S(k,j,i)-\mu}{\sigma}.


When ``standardization_mode = 'slice-by-slice'``, the formula above holds true except that rather than use the
quantities :math:`m`, :math:`M`, :math:`\mu`, and :math:`\sigma` computed for the whole stack, the slice
dependent quantities :math:`m_k`, :math:`M_k`, :math:`\mu_k`, and :math:`\sigma_k` are used instead. For multichannel
stacks, the transformations above are applied for each channel independently.