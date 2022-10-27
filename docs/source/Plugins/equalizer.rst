=========
Equalizer
=========


.. admonition:: Equalizer in a nutshell.
   :class: note

   1. Plugin apply the CLAHE equalization algorithm to each slice of a stack;
   2. This plugin is multichannel;
   3. Python API reference: :py:class:`bmiptools.transformation.dynamics.equalizer.Equalizer`.


This plugin can be used to enhance the contrast in stack using CLAHE algorithm. This plugin uses the
`skimage implementation of CLAHE <https://scikit-image.org/docs/stable/api/skimage.exposure.html>`_, which is applied
slice-by-slice to the whole stack.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.dynamics.equalizer.Equalizer`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.

.. code-block::

   {'kernel_size': None,
   'clip_limit': 0.01,
   'nbins': 256
   }

The plugin-specific parameters contained in this dictionary are:

* ``kernel_size``: shape of the contextual region around a pixel from which the histogram is constructed. When ``None``
  is given, this parameter is set to the ``skimage.exposure.equalize_adapthist()`` function.

* ``clip_limit``: number between 0 and 1 used as clipping limit.

* ``nbin``: number of bins used to construct the histogram for the equalization.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__`` method of the
class :py:class:`Equalizer <bmiptools.transformation.dynamics.equalizer.Equalizer>`.


Use case
========


The typical use of this plugin are:


1. Apply then CLAHE equalization algorithm to each slice of the stack, to increase the contrast.


.. tip::

   Equalization may lead to an increase of the noise level present in a image. As such it suggested to apply this
   plugin after a denoising step (if any), and, more generally, after the removal of all the artifacts in the
   image if this is possible.


Application example
===================


As example consider a portion of slice of a stack of a biological sample obtained via FIB-SEM, with low contrast.


.. image:: ../_images/Plugins/equalizer/pre_equalizer.png
   :class: align-center
   :width: 1000px
   :height: 1000px
   :scale: 60


Applying the Equalizer plugin with its default parameters  (i.e. the one present in the
``empty_transformation_dictionary`` of the plugin), lead to the high contrast image below.


.. image:: ../_images/Plugins/equalizer/post_equalizer.png
   :class: align-center
   :width: 1000px
   :height: 1000px
   :scale: 60


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/equalizer>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.


Implementation details
======================


This plugin applies the CLAHE algorithm to each slice to the input stack. This plugin is essentially a wrapper around the
``skimage.exposure.equalize_adapthist`` implementation of CLAHE. The reference for this implementation can be found in
the corresponding page of the `scikit-image documentaion <https://scikit-image.org/docs/stable/api/
skimage.exposure.html>`_. In case of stack with multiple channels, the CLAHE equalization algorithm is applied
independently to each channel. Note that this behavior is different from what is typically done for standard RGB/RGBA
colored images.


Further details
===============


Websites:


* `wikipedia page <https://en.wikipedia.org/wiki/Adaptive_histogram_equalization>`_


Tutorials:


* `scikit-image technical notes: local histogram equalization <https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_local_equalize.html#sphx-glr-auto-examples-color-exposure-plot-local-equalize-py>`_
