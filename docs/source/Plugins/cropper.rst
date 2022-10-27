=======
Cropper
=======


.. admonition:: Cropper in a nutshell.
   :class: note

   1. Plugin to crop region of a stack;
   2. This plugin is multichannel;
   3. Python API reference: :py:class:`bmiptools.transformation.geometric.cropper.Cropper`.



This plugin can be used to crop a specific region of a stack. When used inside a pipeline, it is better to apply this
plugin as soon as possible, in order to reduce the computation resource needed for the application of the other plugins
to a stack.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.geometric.cropper.Cropper`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.

.. code-block::

   {'z_range': [None,None],
   'y_range': [None,None],
   'x_range': [None,None]
   }

The plugin-specific parameters contained in this dictionary are:

* ``z_range``: list specifying the two extrema for the cropping along the Z-direction,

* ``y_range``: list specifying the two extrema for the cropping along the Y-direction,

* ``x_range``: list specifying the two extrema for the cropping along the X-direction,


The ranges above have to be expressed according to the convention explained :ref:`here <bbox_convention>` (also for the
Z-axis). Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Cropper <bmiptools.transformation.geometric.cropper.Cropper>`.


Use case
========


The typical use of this plugin are:


1. Crop part of the input stack.


Application example
===================


As example consider the slice of a stack of a biological sample obtained via cryo-FIB-SEM.


.. image:: ../_images/Plugins/cropper/pre_cropper.png
   :class: align-center
   :width: 1024px
   :height: 1024px
   :scale: 50


After cropping a square :math:`500 \times 500` pixels in bottom-left part of the slice, the result obtained is given
below.


.. image:: ../_images/Plugins/cropper/post_cropper.png
   :class: align-center
   :width: 500px
   :height: 500px
   :scale: 100


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/cropper>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


Implementation details
======================


In case of stack with multiple channels, the Cropper is applied independently to each channel.