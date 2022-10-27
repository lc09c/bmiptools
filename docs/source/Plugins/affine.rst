======
Affine
======


.. admonition:: Affine in a nutshell.
   :class: note

   1. Plugin to apply affine 3D geometric transformation to a stack;
   2. This plugin is **not** multichannel: the current implementation works only for single channel stack;
   3. This plugin uses the XYZ convention for expressing the coordinates in most of its field;
   4. Python API reference: :py:class:`bmiptools.transformation.geometric.affine.Affine`.


This plugin can be used to apply a generic geometric affine 3D transformation (e.g a rotation,...) on a stack.

The Python API reference of the plugin is :py:class:`bmiptools.transformation.geometric.affine.Affine`.


Transformation dictionary
=========================


The transformation dictionary for this plugin look like this.


.. code-block::

   {'apply': 'translation',
   'reference_frame_origin': 'center-yx',
   'translation': {'translation_vector': [0,0,0]
                   },
   'rotation': {'rotation_angle': 0,
                'rotation_axis': [0,0,1]
                },
   'scaling': {'scaling_factors': 1
               },
   'shear': {'shear_factors': [0,0,0]
             },
   'custom': {'affine_transformation_matrix': None
              }
   }


The plugin-specific parameters contained in this dictionary are:

* ``apply``: it is the field where name of the transformation to apply is specified. Currently possible options are:

  * ``'translation'``, for translation in 3D space;
  * ``'rotation'``, for rotation in 3D space (specified using the angle-axis notation);
  * ``'scaling'``, for scaling transformation in 3D space;
  * ``'shear'``, for shear transformation in 3D space;
  * ``'custom'``, for custom affine transformation, which as to be specified as 4x4 matrix representing the
    transformation in a projective 3D space.

* ``reference_frame_origin``: in this field the reference frame origin for the application of an affine geometric
  transformation is specified. In this field one have to specify the origin position *using the XYZ convention with
  respect in the front-top-left corner of the stack* (i.e. the [0,0,0] position in the numpy array containing the stack)
  using a tuple/list/array, if one wants to specify a precise point. On the other hand, one can also use the options
  below.

  * ``'center'``, to chose the origin of the reference frame is placed in the exact center of the stack;
  * ``'center-zy'``, to chose the origin of the reference frame is placed in the exact center of the ZY-plane and
    with x=0;
  * ``'center-zx'``, to chose the origin of the reference frame is placed in the exact center of the ZX-plane and
    with y=0;
  * ``'center-yx'``, to chose the origin of the reference frame is placed in the exact center of the YX-plane and
    with z=0;

  .. attention::

      The position of the reference frame origin can be any arbitrary point in the stack. The default origin is the one
      of the reference frame used for the definition of the bounding box. For some transformation (e.g translation) the
      position of the origin does not affect the result, while for other transformations the origin position may have
      non trivial effects. For example, the rotation is implemented such that the stack is rotated around the specified
      axis passing trough the origin: change the origin means to change the point around which the stack is rotated.

* ``translation``: contains a dictionary with the parameters for the translation transformation. These parameters
  are read only when ``'apply': 'translation'`` is used. The dictionary with the parameters contains the following
  field:

  * ``translation_vector``: is a tuple/list/numpy array containing the translation vector in a 3D space written using
    the XYZ convention.

* ``rotation``: contains a dictionary with the parameters for the translation transformation. These parameters are read
  only when ``'apply': 'rotation'`` is used. The rotation is expressed using the
  `axis-angle convention <https://en.wikipedia.org/wiki/Axis%E2%80%93angle_representation>`_. The dictionary with the
  parameters contains the following field:

  * ``rotation_angle``, where one express the rotation angle in grad;

  * ``rotation_axis``, where one express the vector (as tuple/list/numpy array) representing the direction of the
    rotation axis

  The rotation axis is automatically assumed to pass for the point specified in the ``reference_frame_origin`` field.

* ``scaling``: contains a dictionary with the parameters for the scaling/dilating transformation. These parameters
  are read only when ``'apply': 'scaling'`` is used. The dictionary with the parameters contains the following field:

  * ``scaling_factor``,  is the field where one specify scaling factor of the transformation. If a single number is
    given, it is assumed the same scaling transformation for each axis. On the other hand, if tuple/list/numpy array
    with 3 entries is given, it is assumed a different scaling for each axis, using the XYZ-convention.


* ``shear``: contains a dictionary with the parameters for the shear transformation. These parameters are read only when
  ``'apply': 'shear'`` is used. The dictionary with the parameters contains the following field:

  * ``shear_factors``, where the three parameters of a 3D shear transformation are specified in a tuple/list/numpy array
    using the XYZ-convention.

* ``custom``: contains a dictionary with the parameters for a generic affine transformation. These parameters are read
  only when ``'apply': 'custom'`` is used. The dictionary with the parameters contains the following field:

  * ``affine_transformation_matrix``, which is numpy array containing a 4x4 matrix representing a generic affine
    transformation. The affine transformation have to be expressed using the *augmented matrix* representation for
    affine transformations (see `here <https://en.wikipedia.org/wiki/Affine_transformation>`_).


Further details useful the the usage of this plugin with the Python API can be found in the ``__init__``
method of the class :py:class:`Affine <bmiptools.transformation.geometric.affine.Affine>`.



Use case
========


The typical use of this plugin are:


1. Apply affine geometric transformations (e.g translations, rotations,...) to the input stack.


.. tip::

   Since the result of an affine transformation is computed from the interpolation of voxels value of a stack, the
   quality of the interpolated function determine the quality of the final result. A 3d stack which is not aligned along
   one of their axis, would not produce the best interpolation function. Therefore, it is suggested to use the this
   plugin only after the stack alignment (for example via the :doc:`registrator` plugin).


Application example
===================


As example consider the slice of a stack of a biological sample obtained via cryo-FIB-SEM. The stack considered here
has been aligned, and below the 50 slices of it are showed in a single gif.


.. image:: ../_images/Plugins/affine/pre_affine_3d_anim50slices.gif
   :class: align-center
   :width: 400px
   :height: 400px
   :scale: 100


After the application of the Affine plugin to rotate the stack of 3° around the z-axis, and 5° around the x-axis, the
result obtained is given below.


.. image:: ../_images/Plugins/affine/post_affine_3d_anim50slices.gif
   :class: align-center
   :width: 400px
   :height: 400px
   :scale: 100


The weird behavior at the boundaries is unavoidable: it is due to the fact the the interpolation function in those
points is constructed interpolating between the image values at the border of some slice, and the empty part of the
image in the next slice, due to the translations necessary for the stack alignment.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Plugins/affine>`_. To reproduce the images showed above one may
   consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/
   examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can find all the
   necessary input data.



Implementation details
======================


This plugin rely on the basic transformations implemented in ``scipy.ndimage``
(see `here <https://docs.scipy.org/doc/scipy/reference/ndimage.html>`_. Useful technical notes about this kind of
transformations can be found :ref:`here <image_warping_tutorial>`.


Further details
===============


Websites:


* `Affine transformation on wikipedia <https://en.wikipedia.org/wiki/Affine_transformation>`_.


Technical notes:

.. _image_warping_tutorial:

* `"NumPy/sciPy recipes for image processing: affine image warping" <https://www.researchgate.net/publication/328968274_NumPy_SciPy_Recipes_for_Image_Processing_Affine_Image_Warping>`_ - Christian Bauckhage.
