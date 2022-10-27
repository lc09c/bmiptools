========================
Change coordinate system
========================


An useful visualization tool in bmiptools is
:py:class:`ChangeCoordinateSystem <bmiptools.visualization.geometric.change_coordinate_system.ChangeCoordinateSystem>`,
which allows to change the coordinate system on which the stack is visualized. Its structure is similar to a plugin,
but it has no transformation dictionary. After the initialization, this tool takes a given stack :math:`S(k,j,i)`
evaluated on a 3d grid with coordinates :math:`(k,j,i)` and return another stack :math:`S'(r,s,t)` evaluated on a
different 3d grid with coordinates :math:`(r,s,t)`, related to the previous coordinate by a change of reference frame.


.. attention::

   This tool can be used via Python API only.


.. _preliminary_facts_crf:

Preliminary facts
=================


Given a stack :math:`S` the value assumed in the voxel :math:`(k,j,i)` has to be understood as the value of some
physical quantity describing the sample in the point :math:`(k\Delta Z,j\Delta Y,i \Delta X)` of the 3d space, where
:math:`(\Delta Z,\Delta Y,\Delta X)` are the voxel size. All the points :math:`(k,j,i)` associated to the various
voxels of the stack form a 3d grid, which is typically cartesian, i.e. expressed in a cartesian reference frame. For
visualization purpose one may want to see the stack using a different coordinate system.

Let :math:`(z,y,x)` and :(s,t,u): be two coordinate system related by the invertible function :math:`f` such that


.. math::

   (s,t,u) &= f(z,y,x) \\
   (z,y,x) &= f^{-1}(s,t,u).


Given a :math:`K \times J \times I` stack :math:`S(k,j,i)` evaluated in the :math:`(z,y,x)` coordinates with voxel size
given by :math:`(\Delta z, \Delta y, \Delta x)`, it can be evaluated on the :math:`(s,t,u)` coordinate system by
following this procedure.

1. Define the new grid in the :math:`(s,t,u)` coordinate system. Practically this means to specify two of the following
   3 quantities: number of points for each coordinate, coordinate range, and step size for each coordinate. By
   specifying two of them, the third follow. Indeed:

   * specifying for the coordinate :math:`s` the number of points :math:`N_s` and its range :math:`[S_{min},S_{max}]`,
     then the step step is given by :math:`\Delta s = (S_{max}-S_{min})/N_s`. Similar considerations hold for the other
     two coordinates.

   * specifying for the coordinate :math:`s` the number of points :math:`N_s` and its step size :math:`\Delta s`,
     then the coordinate range is :math:`[0,N_s \Delta s]` which can be translated by specifying an offset value.
     Similar considerations hold for the other two coordinates.

   * specifying for the coordinate :math:`s` its range :math:`[S_{min},S_{max}]` and its step size :math:`\Delta s`,
     then the number of points is given by :math:`N_s = (S_{max}-S_{min})/\Delta s`. Similar considerations hold for
     the other two coordinates.

   The new grid will contain :math:`N_s \times N_t \times N_u` points :math:`(l,m,n)` corresponding to the point of the
   3d space having :math:`(s,t,u)`-coordinates :math:`(l\Delta s, m\Delta t, u\Delta u)`.

2. Interpolate the stack :math:`S` on the grid defined in the :math:`(z,y,x)` coordinate system, obtaining the
   function :math:`\tilde{S}(k,j,i)`.

3. Evaluate the interpolated stack on the new grid, by using the inverse function :math:`f^{-1}`. More precisely, given
   a point in the new grid :math:`(l,m,n)` one computes the corresponding point in the 3d space
   :math:`(s_l,t_m,u_n) = (l\Delta s, m\Delta t, n\Delta u)`. Then one compute the corresponding point in the grid
   expressed in the old coordinate system :math:`(z,y,x)`, this can be done first by computing the point


   .. math::

      (z_{(l,m,n)},y_{(l,m,n)},x_{(l,m,n)}) = f^{-1}(l\Delta s, m\Delta t, n\Delta u),


   and later diving each coordinate by the corresponding step size, obtaining


   .. math::

      (k_{(l,m,n)},j_{(l,m,n)},i_{(l,m,n)}) =
      \left(\frac{z_{(l,m,n)}}{\Delta z},\frac{y_{(l,m,n)}}{\Delta y},\frac{x_{(l,m,n)}}{\Delta x}\right).


   At this point the stack in the expressed in the new coordinate system :math:`S'`, is defined as


   .. math::

      S'(l,m,n) = \tilde{S}(k_{(l,m,n)},j_{(l,m,n)},i_{(l,m,n)}).


Spherical and cylindrical may be particularly useful and will be briefly described below.


Spherical coordinates
---------------------

The function :math:`f` mapping the cartesian coordinates :math:`(z,y,x)` into spherical coordinates
:math:`(r,\theta,\phi)` is defined as follow


.. math::

   \left(\begin{array}{c}
   r \\
   \theta \\
   \phi \\
   \end{array}\right) = \left(\begin{array}{c}
   \sqrt{x^2+y^2+z^2} \\
   \mbox{arccos} \left(\frac{z}{r}\right) \\
   \mbox{arctan2} \left(y,x\right) \\
   \end{array}\right)


where :math:`\mbox{arctan2}` is the `"2-argument arctangent" <https://en.wikipedia.org/wiki/Atan2>`_, and the
inverse transformation is


.. math::

   \left(\begin{array}{c}
   z \\
   y \\
   x \\
   \end{array}\right) = \left(\begin{array}{c}
   r\cos(\theta) \\
   r\sin(\theta)\sin(\phi) \\
   r\sin(\theta)\cos(\phi) \\
   \end{array}\right)


In bmiptools :math:`f` and :math:`f^{-1}` corresponds to the function :py:func:`cartesian_to_spherical
<bmiptools.core.math_utils.cartesian_to_spherical>` and :py:func:`spherical_to_cartesian
<bmiptools.core.math_utils.spherical_to_cartesian>`.


Cylindrical coordinates
-----------------------


The function :math:`f` mapping the cartesian coordinates :math:`(z,y,x)` into spherical coordinates
:math:`(r,\theta,z)` is defined as follow


.. math::

   \left(\begin{array}{c}
   r \\
   \theta \\
   z \\
   \end{array}\right) = \left(\begin{array}{c}
   \sqrt{x^2+y^2} \\
   \mbox{arctan2} \left(y,x\right) \\
   z \\
   \end{array}\right)


where :math:`\mbox{arctan2}` is the `"2-argument arctangent" <https://en.wikipedia.org/wiki/Atan2>`_, and the
inverse transformation is


.. math::

   \left(\begin{array}{c}
   z \\
   y \\
   x \\
   \end{array}\right) = \left(\begin{array}{c}
   z \\
   r\sin(\theta) \\
   r\cos(\theta) \\
   \end{array}\right)


In bmiptools :math:`f` and :math:`f^{-1}` corresponds to the function :py:func:`cartesian_to_cylindrical
<bmiptools.core.math_utils.cartesian_to_cylindrical>` and :py:func:`cylindrical_to_cartesian
<bmiptools.core.math_utils.cylindrical_to_cartesian>`.


Tool usage
==========


To use this tool the first thing to is to initialize it. During the initialization the following information need to be
declared:

* ``reference_frame_origin``: it is the position of the origin in the new reference frame, and have to be specified as a
  list, or tuple, or a numpy array.

* ``xyz_to_XYZ_inv_map``: this is a python function with 3 input representing the inverse mapping between the reference
  frame 'xyz' and the new reference frame 'XYZ' (i.e. is the function :math:`f^{-1}`
  :ref:`above <preliminary_facts_crf>`).

* ``xyz_to_XYZ_specs``: this is a dictionary used to define the new reference frame, which need to have the following
  structure:

  * ``new_shape``,  a tuple specifying the shape of the stack in the new reference frame, i.e. the number of points for
    each new coordinate of the new grid on which the stack will be define after the coordinate change.

  * ``X_bounds``, a list with two arguments: the minimum and maximum value of the new X coordinate.

  * ``Y_bounds``, a list with two arguments: the minimum and maximum value of the new Y coordinate.

  * ``Z_bounds``, a list with two arguments: the minimum and maximum value of the new Z coordinate.

  * ``XYZ_ordering``, is used to specify the ordering of the new coordinates. If None the order is the 'ZYX' otherwise
    on can specify a list with the new ordering, e.g. for 'XYZ' use [2,1,0], for 'YXZ' use [1,2,0], while for 'XZY' use
    [2,0,1].

* ``use_xyz_ordering``: if ``True``, the default ordering of the axis in the stack (which is 'zyx') is converted to
  the cartesian ordering (i.e. 'xyz').


Therefore to initialize this tool the code below can be used, which assume the initial coordinate system as cartesian,
the new coordinate system as spherical.


.. code-block::

   import numpy as np
   from bmiptools.visualization.geometric.change_coordinate_system import ChangeCoordinateSystem
   from bmiptools.core.math_utils import spherical_to_cartesian


   ccs = ChangeCoordinateSystem(reference_frame_origin = [100,100,100],
                                xyz_to_XYZ_inv_map = spherical_to_cartesian,
                                xyz_to_XYZ_specs = {'new_shape': (100,180,360),
                                                    'X_bounds': [0,100],
                                                    'Y_bounds': [0,np.pi],
                                                    'Z_bounds': [0,2*np.pi]},
                                use_xyz_ordering = True)


Once the initialization is done, the application to this tool to a stack ``stack`` can be done as for the plugin with
the method ``.transform``.


.. code-block::

   from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2d as b2d

   # load/ create a stack.
   # stack = ...

   # See slice 0 before the change of coordinate system.
   # b2d.show_image(stack[0])

   ccs.transform(stack)

   # See slice 0 after the change of coordinate system.
   b2d.show_image(stack[0])


.. attention::

   Also in this case the ``inplace`` option is present: when ``inplace = True`` (default value) the stack content is
   overwritten with the new stack, while using ``inplace = False`` the new stack is returned as numpy array.

   .. code-block::

      from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2d as b2d

      # load/ create a stack.
      # stack = ...

      transformed_stack = ccs.transform(stack,inplace=False)

      # Compare slice 0 of the stack and the same slice of the transformed_stack numpy array
      b2d.compare_images(stack[0],transformed_stack[0])


Further reading
===============


Technical notes:

* `"NumPy/sciPy recipes for image processing: general image warping" <https://www.researchgate.net/publication/
  330204359_NumPy_SciPy_Recipes_for_Image_Processing_General_Image_Warping>`_ - Christian Bauckhage.
