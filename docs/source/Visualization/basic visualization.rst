======================================
Basic visualization tools in bmiptools
======================================


bmiptools has also *basic* visualization tools based on `matplotlib <https://matplotlib.org/>`_, which can be used for
a rapid inspection of the slices of a stack. In particular, there are:

* the :py:class:`Basic2D <bmiptools.visualization.graphic_tools.basic_graphic_tools.Basic2D>` class, for some basic 2d
  visualization tools;

* the :py:class:`Basic3D <bmiptools.visualization.graphic_tools.basic_graphic_tools.Basic3D>` class, for some basic 3d
  visualization tools.

About that, the most useful visualisation tools are the 2d ones, whose usage is showed below.


Basic slice visualization
=========================


The code below shows how to use some of them to visualize the slice of the stack ``stack``.


.. code-block::


    from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2D as b2d

    # plot the slice 0
    b2d.show_image(stack[0])


Compare two slices
==================


Another useful operation can be the comparison of two slices of a stack. This can be done easily with the code below.


.. code-block::

   # compare slice 0 and slice 1
   b2d.compare_images(stack[0],stack[1])


Visualizing image grey-levels as surface
========================================


For segmentation purposes, it can be useful to visualize the gray level of a slice as a 3d surface. In bmiptools this
can be done as follow.


.. code-block::

    # plot the 2d image of slice 0 as 3d surface
    b2d.plot_image_as_surface(stack[0])


Plot masks on slices
====================


Given a mask, it is also possible to visualize it superimposed over the slice of a stack.


.. code-block::

    # plot a mask on the slice 0
    mask = ....                                     # numpy array containig the mask
    b2d.show_threshold_on_image(stack[0],mark)