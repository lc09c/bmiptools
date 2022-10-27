=================
Histogram matcher
=================


.. admonition:: Histogram matcher in a nutshell.
   :class: note

   1. Plugin for match the brightness of one slice of a Stack with the next one;
   2. Do not use this plugin if meaningful global brightness variations along the Z-axis of a stack are expected;
   3. This plugin is multichannel;
   4. Python API reference: :py:class:`bmiptools.transformation.dynamics.histogram_matcher.HistogramMatcher`.


This plugin can be used to match the histograms among the various slices of a stack. This makes the brightness level of
the slice more uniform, reducing or eliminating the sudden brightness/contrast variation among one slices an the next
one.

The Python API reference of the plugin is
:py:class:`bmiptools.transformation.dynamics.histogram_matcher.HistogramMatcher`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.

.. code-block::

   {'reference_slice': 0
    }

The plugin-specific parameters contained in this dictionary are:

    * ``reference_slice``: position of the slice used as reference during the matching of the histograms.

Further details useful the the usage of this plugin with the Python API can be found in the ``__init__`` method of the
class :py:class:`HistogramMatcher <bmiptools.transformation.dynamics.histogram_matcher.HistogramMatcher>`


Use case
========


The typical uses of this plugin are:

1. Remove the sudden brightness variation along the Z-axis in a stack.

2. Homogenize the slices in a stack to easier the optimization of the other plugins in a pipeline.

.. tip::

    * Do not use this plugin on a stack where meaningful brightness variations slice after slice are expected. These
      variations

    * A good idea is to use this plugin in the beginning of a pipeline (first or second plugin), in order to have an
      homogenized stack as input of the core plugins of a pipeline. In this way, it is more likely that the application
      of the core plugins (initialized with parameters both set by the user or found by some optimization procedure)
      produces similar effects for each slice of the stack.


Application example
===================


As example consider the portion of a FIB-SEM stack of a biological sample, visualized as animated gif (saving mode
available in the python API, see :py:meth:`bmiptools.stack.Stack.save_as_gif`), in order to see how the overall
brightness level suddenly change from one slice to the next.


.. image:: ../_images/Plugins/histogram_matcher/pre_histogram_matcher.gif
   :class: align-center
   :width: 1024px
   :height: 1024px
   :scale: 60


Note the strong reduction of the overall brightness happening at approximately the half of the clip. After histogram
matching, the sudden changes in brightness disappear.


.. image:: ../_images/Plugins/histogram_matcher/post_histogram_matcher.gif
   :class: align-center
   :width: 1024px
   :height: 1024px
   :scale: 60


.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/histogram_matcher>`_. To reproduce the images showed above one
   may consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/
   master/examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find
   all the necessary input data.


Implementation details
======================


The core operation of this plugin is the matching of the histogram among two images. This is done by using the skimage
function ``skimage.exposure.match_histogram``
(see `here <https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.match_histograms>`_ for
further details). Given two slices of a stack :math:`a` and :math:`b`, let :math:`HM(a,b)` be the function matching the
histogram of the image :math:`b` with the histogram of the image :math:`a` (used as reference). Then, given the input
:math:`K \times J \times I` stack :math:`S(k,j,i)` and a reference slice in position :math:`k_0`, consider :math:`k`-th
slice :math:`S[k](x,y)`. The ``HistogramMatcher`` plugin perform the following operations:

1. Starting from :math:`k=k_0+1`, then

   .. math::

      S[k](j,i) \rightarrow S_{output}[k](i,j) = HM(S[k-1](j,i),S[k](j,i)).

   This operation is repeated *increasing* :math:`k` by 1 till :math:`k=K-1` is reached.

2. Going back to :math:`k=k_0-1`

   .. math::

      S[k](j,i) \rightarrow S_{output}[k](i,j) =  HM(S[k+1](j,i),S[k](j,i)).

   This operation is repeated *decreasing* :math:`k` by 1 till :math:`k=0` is reached.


For multichannel stack, the transformations above are applied for each channel independently.


Further details
===============


Websites:

* `wikipedia <https://en.wikipedia.org/wiki/Histogram_matching>`_

* `"Histogram Matching, Earth Engine by Example" - Noel Gorelik <https://medium.com/google-earth/histogram-matching-c7153c85066d>`_

* `"Histogram Matching" - Paul Bourke <http://paulbourke.net/miscellaneous/equalisation/>`_
