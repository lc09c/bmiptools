===========================================
GuiPI: automatic GUI generation for plugins
===========================================


bmiptools has a system for the automatic GUI creation, which uses `magicgui <https://napari.org/magicgui/>`_ as backend.
In bmiptools, each parameter of a plugin corresponds to a widget, which represent the part of the graphical interface
responsible for the setting of the parameter values. For each plugins widgets are packed one on top of the other in
order to create the plugin gui. At the end a button is always present. Pressing this but the plugin is initialized with
the parameters specified in the gui in that moment.

In addition to the native magicgui widgets, in bmiptools custom widgets for specific data types and format has been
developed (see :py:class:`bmiptools.gui.gui_basic`). The association between a given data type and a given widget is
regulated by GuiPI.


GUI Parameters Information, i.e. GuiPI
======================================


GuiPI, i.e. Gui Parameter Information, is an object which store information about the parameters relevant for
the automatic gui construction. A ``GuiPI`` object have the following initialization


.. py:function:: __init__(self,p_type=None,min=None,max=None,options=None,description=None,name=None,filemode=None,visible=True)

   The inputs required for initialize a GuiPI object are:

   * ``p_type``, which stands for *parameter type*, which determine the selection of the corresponding widget. In
     addition to the standard python data-type **int**, **bool**, **float**, **str**, and **list**, there are also
     other useful GuiPI parameters type. They are:

     * ``'path'``, to specify a path to a file or a folder;
     * ``'options'``, to specify list of objects among which the user can choose;
     * ``'range int'``, to specify an integer range object, i.e. integer numbers going from A to B *with a step of C*,
       where A,B,C integer;
     * ``'range float'``, to specify a floating point range object, i.e. floating point numbers going from A to B
       *with a step of C*, where A,B,C float;
     * ``'span int'``, to specify an integer linear span object, i.e. integer numbers going from A to B *in C steps*,
       with A,B,C integer;
     * ``'span float'``, to specify a floating point linear span object, i.e. floating point numbers going from A to B
       *in C steps*, with A,B,C float;
     * ``'math'``, to specify a mathematical object, e.g. vector,matrix,ecc..., and the slicing notation described in
       the :ref:`bbox_convention` subsection;
     * ``'table'``, to specify a tabular data. This has to be done as a list-of-list having structure

       .. code-block::

          [[key1, value1],[key2,value2],...].

   * ``min``, minimum value the parameter can take. This field is optional and ignored for non-numeric fields;

   * ``max``, maximum value the parameter can take. This field is optional and ignored for non-numeric fields;

   * ``options``, when ``p_type = 'options'`` in this field, the list with the available options for a given parameter
     is specified. For other values of ``p_type`` this field is ignored.

   * ``description``, is an optional brief description of which should appear when the mouse stops on the widget.

   * ``name``, is the name of the parameter displayed in the widget.

   * ``filemode``, when ``p_type = 'path'`` this is the kind of widget for the specification of a path. It can be:

     * ``'r'``, to specify one existing file;
     * ``'rm'``, to specify one or more existing files;
     * ``'w'``, to specify one file name that does not have to exist;
     * ``'d'``, to specify one existing directory.

     For other values of ``p_type`` this field is ignored.

   * ``visible``, when ``False`` the widget is not visualized in the final plugin GUI.


To get the corresponding widget one have to call the method

.. py:function:: widget(self,name=None)

   This method returns the widget object. The name of the widget can be set by specifying the ``name`` field (if needed,
   this is optional). In addition to the widget itself, two functions are returned:

   * the setter function, i.e. the function to set the values initially displayed in the widget;
   * the reader function, i.e. the function to read the value currently set in the widget, and possibly organize them
     in a suitable format.


.. note::

   GuiPI objects are used in the ``_guipi_dictionary`` attribute of the various plugins (see also
   `here <guipi_dictionary_plugin_strucure>`_).


Guize
=====


In bmiptools the automatic gui creation of from a class is possible. This is done by means of the guize methods. Two are
the available guize methods:

1. :py:class:`GuizeObject <bmiptools.gui.gui_basic.GuizeObject>`, which creates a GUI out of a Python class. The
   parameters displayed in the gui are the input parameter of the ``__init__`` method.

2. :py:class:`GuizeObjectFromDict <bmiptools.gui.gui_basic.GuizeObjectFromDict>`, which creates a GUI out of a Python
   class, when the class input parameters are all contained in a dictionary (as in the case of bmiptools plugins). The
   parameters displayed in the gui are the one contained in the ``empty_transformation_dictionary``.

In both cases, the widget can be assigned in two ways:

* the widgets are determined from parameters types using the magicgui-data type conversion rules. In case of bmiptools
  this does not always give a good result: for this reason GuiPI objects has been developed.

* the widgets are determined from the ``_guipi_dictionary`` attribute of the input classes.

In both cases, first the method look for a ``_guipi_dictionary`` and only if it is not found, creates the gui using the
standard magicgui-data type conversion rules.

As example of application of these two methods, one can consider the :py:class:`Stack <bmiptools.stack.Stack>` class and
a plugin, say the the :py:class:`Destriper <bmiptools.transformation.restoration.destriper.Destriper>`. The ``Stack``
class has a ``_guipi_dictionary``, but it is not initialized via a dictionary. Therefore ones have to use
:py:class:`GuizeObject <bmiptools.gui.gui_basic.GuizeObject>`, as the example below shows.


.. code-block::

   from bmiptools.stack import Stack
   from bmiptools.gui.gui_basic import GuizeObject

   stack_gui = GuizeObject(Stack)
   stack_gui()                                 # run the gui


Note that :py:class:`GuizeObject <bmiptools.gui.gui_basic.GuizeObject>` returns a gui object. To actually run the gui,
one has to call this object, which is the last line of the code snapshot above. The
:py:class:`Destriper <bmiptools.transformation.restoration.destriper.Destriper>`, being a plugin, needs
:py:class:`GuizeObjectFromDict <bmiptools.gui.gui_basic.GuizeObjectFromDict>` in order to me the gui. The code below
shows how this is done.


.. code-block::

   from bmiptools.transformation.restorer.destriper import Destriper
   from bmiptools.gui.gui_basic import GuizeObject

   destriper_gui = GuizeObjectFromDict(Destriper)
   destriper_gui()                                 # run the gui


.. attention::

   The gui obtained both from :py:class:`GuizeObject <bmiptools.gui.gui_basic.GuizeObject>` and from
   :py:class:`GuizeObjectFromDict <bmiptools.gui.gui_basic.GuizeObjectFromDict>` have always a button 'ok' at the end.
   No action is performed when one clicks it: one has to connect this button to a suitable function in order to make
   some action according to the magicgui rules (see `here <https://napari.org/magicgui/usage/direct_api.html>`_). This
   button always correspond to the gui object attribute ``pbutton``. If the plugin transformation dictionary is nested,
   for each level of the dictionary a separator contained a series of '###' and the key corresponding to the level is
   added in the final gui. The whole plugin gui organized as a magicgui container can be found in the attribute ``gui``
   of the gui object produced by the guize methods.

