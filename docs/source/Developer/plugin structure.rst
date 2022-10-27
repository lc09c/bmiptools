========================
General plugin structure
========================


The general structure of a plugin is explained here.The developer creating a new plugin according to the rules explained
here, get the following functionalities for free:

1. The plugin can be used in a pipeline in automatic way, i.e. with automatized fitting and application on the input
   stack of the pipeline.

2. The all parameters of the plugin are tracked during the pipeline application and save when the pipeline is saved.
   More generally, they can be all stored in a single dictionary with their current value at any time by
   calling a single command.

3. The GUI for the plugin is created automatically and is integrated with the general bmiptools GUI for free.

Therefore, by using the structure and conventions described here, a new plugin can be fully integrated with bmiptool.


.. _TransformationBasic:

Basic transformation structure
==============================


The prototype plugin is declared in the class :py:class:`bmiptools.transformation.base.TransformationBasic`, which is
copied entirely below. **This class need to be always inherited by any new plugin**.


.. code-block::

    class TransformationBasic(CoreBasic):

        empty_transformation_dictionary = {}
        _guipi_dictionary = {}
        # _undillable_attribute_path = ''
        #
        # P.A. : A global attribute of the class, named '_undillable_attribute_path' need to be created
        #        specifying the name of the class attribute used to specify the loading link. See
        #        DenoiseDNN for an example.
        #
        def __init__(self,*args,**kwargs):
            """
            Initialize here all the parameters of the transformation and execute all the setup operations.
            """
            super(TransformationBasic,self).__init__()
            self.fit_enable = True
            pass

        def _setup(self,*args,**kwargs):
            """
            Execute all the setup operations of the transformation. All the operations which have to be executed before
            to apply the transformation and does not depend on the Stack object on which they are applied, should be placed
            here.
            """
            return None

        def fit(self,x,*args,**kwargs):
            """
            Fit the transformation to the stack on which is applied.

            :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
            """
            return None

        def transform(self,x,inplace=True,*args,**kwargs):
            """
            Apply the initialized transformation.

            :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
            :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                            False, the transformation result is returned in the for of numpy array and the content of the
                            input Stack is left unchanged.
            """
            return None

        def inverse_transform(self,x,inplace=True,*args,**kwargs):
            """
            Apply the inverse transformation (if possible) on the stack

            :param x: (bmiptools.stack.Stack) stack object on which the inverse transformation is applied.
            :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                            False, the transformation result is returned in the for of numpy array and the content of the
                            input Stack is left unchanged.
            """
            return None

        def save(self,*args,**kwargs):
            """
            Save the plugin state (or all the necessary information to recover a functional plugin state). This method need
            to be implemented ONLY if the plugin contain some "non-pickable"/"non-dillable" object. In this case the default
            saving methods of the saving class will not be able to save the plugin state. A simple way to check the
            "pickability/dillability" of an object, the code below can be used to check if the object f is dillable:

            >>> import dill
            >>> dill.pickles(f)

            It is recommended to make this test with a plugin that has already been initialized, (eventually) fitted and
            applied to some stack, so that all the attributes of the plugin has been initialized.

            P.A. : In case of undillable plugin, a global attribute of the plugin class, named 'undillable_path_attributes'
            need to be created specifying the name of the class attribute used to specify the loading link of the undillable
            objects.
            See DenoiseDNN for an example.

            """
            return None

        def get_transformation_dictionary(self,*args,**kwargs):
            """
            Return the transformation dictionary of the plugin filled with the current values of the variables of the
            plugin class at the time at which this method is called. The transformation dictionary of the plugin has the
            same organization of the 'empty_transformation_dictionary', a (global) attribute of the plugin class.
            """
            if hasattr(self.__class__, 'empty_transformation_dictionary'):

                if not self.__class__.empty_transformation_dictionary is None:

                    transformation_dictionary = copy(self.__class__.empty_transformation_dictionary)
                    key_branches_list = ut.get_branch_of_key_tree(transformation_dictionary)
                    for element in key_branches_list:

                        if element[-1] in self.__dict__.keys():

                            ut.set_by_path(transformation_dictionary, element, eval('self.{}'.format(element[-1])))

                    return transformation_dictionary

                return None

            else:

                return None


As said above, this template class have to be always inherited by the plugin class. In this way all the flags specified
in the global setting can be used also in the new plugin. The ones useful for the creation of a plugin may be:

* ``use_multiprocessing``, when ``True`` multiprocessing can be used.

* ``plugin_parallelization``, when equal to 1 the parallelization is done at plugin level (currently this flag is not
  used, it is always equal to 1).

* ``use_gpu``, when ``True`` the gpu can be used (currently this flag is not used, it is always equal to 0).

* ``cpu_buffer``, number of cpu not used during the parallelization.


.. _default_global_attributes_plugins:

Default global attributes
-------------------------


Every plugin has always two dictionaries by default.


* ``empty_transformation_dictionary``: every plugin need to have its own empty transformation dictionary, where all the
  parameters are initialized with some default value. The structure of this dictionary has to be the same of the
  ``transformation_dictionary``, which is used to initialize the plugin. This for two reasons:

  1. the user can check how the transformation dictionary of the plugin have to look like, *before* the plugin
     initialization;

  2. the empty transformation dictionary is used as template to register the state of then plugin when the
     :py:meth:`.get_transformation_dictionary <bmiptools.transformation.base.TransformationBasic.get_transformation_dictionary>`
     method is called.

.. _guipi_dictionary_plugin_strucure:

* ``_guipi_dictionary``: this dictionary contains the information need to automatically create the GUI out of the
  python class. In particular, here is where one has to specify which kind of widget is used to create the graphical
  interface for the input of a given parameter. It has to have exactly the same structure of the transformation
  dictionary (i.e. the same structure of the empty transformation dictionary), but the value associated to the key
  corresponding to a given parameter (see `below <transformation_dictionary_dev>`_ for the convention about these keys)
  have now a :doc:`GuiPI <../Developer/guipi>` object specifying the nature of the parameter, from the GUI point of
  view.


.. attention::

   **For plugins which are not dill-compatible**, i.e. they cannot be pickled as Python objects using
   `dill <https://dill.readthedocs.io/en/latest/dill.html>`_  the user need to specify a custom saving method (see
   `below <save_method_dev>`_) capable to store the status of the Python object in a way that can be loaded in a second
   moment. In this case an additional global attribute need to be present

   * ``_undillable_attribute_path``, which contains the name of the key in the transformation dictionary containing the
     path to the file to be used to load the previous plugin status.

   The dill compatibility of a Python object ``f`` can be checked with the simple code below

    .. code-block::

       import dill
       dill.pickles(f)



Default methods
---------------

.. py:method:: __init__(self,*args,**kwargs)

   It is the standard initializer of a class, and it has typically the two input parameters below:

   .. _transformation_dictionary_dev:

   * ``transformation_dictionary``: it is a dictionary containing all the input parameters needed to initialize the
     plugin. It can be a nested dictionary, i.e. a key can have another dictionary as value. Each key of this dictionary
     is the name of a parameter, except if the value of that key is another dictionary: in this case the keys of the
     deepest dictionary are the names of the parameters. For more about the transformation dictionary from the plugin
     usage point of view, see :ref:`here <transformation_dictionary>`.

   * ``force_serial``: it is used as flag to force the serial execution of the internal operation of a plugin. It is
     an optional argument and is not tracked by a :py:class:`Pipeline <bmiptools.pipeline.Pipeline>` object.


   .. attention::

      Since the :py:class:`TransformationBasic <bmiptools.transformation.base.TransformationBasic>` need to be inherited
      by any plugin, recall that one always needs to add the ``super`` function in the ``__init__()`` of the new plugin.
      The example below, show that


      .. code-block::

         from bmiptools.transformation.base import TransformationBasic


         class MyPlugin(TransformationBasic):

               empty_transformation_dictionary = {}
               _guipi_dictionary = {}
               def __init__(self,transformation_dictionary):

                   super().__init__(MyPlugin)   # <- this line is always needed.
                   ...


.. py:method:: _setup(self,*args,**kwargs)

   This method execute all the setup operations of the plugin. The setup operations are all those preliminary
   operations which can be done by the plugin without the need to have access to some input stack.

.. py:method:: fit(self,x,*args,**kwargs)

   This method execute fit the plugin on a given input stack ``x``. This fitting operations have to be understood either
   as the actual optimization routine, or as all those operations which need a stack in order to be done (e.g. get the
   stack shape, get the slice dimension, ecc...).

.. py:method:: transform(self,x,inplace=True,*args,**kwargs)

   This method apply the initialized transformation of the plugin on the input stack ``x``. The ``inplace`` flag is used
   to decide if the result of the transformation is returned as numpy array (``inplace = False``), or the input stack is
   overwritten with the result (``inplace = True``).


.. py:method:: inverse_transform(self,x,inplace=True,*args,**kwargs)

   This method apply the inverse of the initialized transformation of the plugin on the input stack ``x``. The
   ``inplace`` flag is used to decide if the result of the transformation is returned as numpy array
   (``inplace = False``), or the input stack is overwritten with the result (``inplace = True``).

.. _save_method_dev:

.. py:method:: save(self,*args,**kwargs)

   This method need to be implemented **only** if the plugin contain some dill-incompatible object, and is used to save
   the plugin state, or all the necessary information to recover a functional plugin state able to replicate the
   plugin output.

.. py:method:: get_transformation_dictionary(self,*args,**kwargs)

  This method is used to get the transformation dictionary with the values all the parameter has when it is called.


These methods are the default one, which should be present to integrate a plugin in bmiptools. Other methods can be
clearly added if needed, but they will not be called by the other tools in bmiptools. Typically they are used for the
internal operations in a plugin.



Conventions for the plugin construction
=======================================


The following conventions are also used:


1. **All the parameters of a given plugin need to be specified in the transformation dictionary of the plugin**, which
   is the main input of the ``__init__()`` method of the plugin. This transformation dictionary can be a nested
   dictionary and only the keys at the deepest level corresponds to the parameter name. In the initialization of the
   plugin, **each parameter need to be assigned to local attribute of the plugin class having exactly the same name of
   the keys of the (deepest level of the nested) dictionary**. For example, given a plugin with transformation
   dictionary equal to


   .. code-block::

      {'a': 1,
       'b':{'nested_w': 4,
            'nested_v':{'nested2_x': [3,2,1],
                        },
            },
       'c': 'val',
      }


   has the following parameters: ``a``, ``nested_w``, ``nested2_x``, and ``c``. Therefore in the plugin initialization
   one need to have the following local attributes.


  .. code-block::

     ...
     def __init__(self,transformation_dictionary):

         ...
         self.a = transformation_dictionary['a']
         self.nested_w = transformation_dictionary['b']['nested_w']
         self.nested2_x = transformation_dictionary['b']['nested_v']['nested2_x']
         self.c = transformation_dictionary['c']
         ...

     ...


2. When a new plugin is created, the methods of
   :py:class:`TransformationBasic <bmiptools.transformation.base.TransformationBasic>` are overwritten with the one of
   the new plugin. All except
   :py:meth:`get_transformation_dictionary <bmiptools.transformation.base.TransformationBasic.get_transformation_dictionary>` ,
   since it is able to return the update transformation dictionary filled with the current value of the parameters,
   provided that the point 1. is fulfilled.

3. **The input of a plugin is always a stack**. Therefore in the
   :py:meth:`fit <bmiptools.transformation.base.TransformationBasic.fit>`,
   :py:meth:`transform <bmiptools.transformation.base.TransformationBasic.transform>` and
   :py:meth:`inverse_transform <bmiptools.transformation.base.TransformationBasic.inverse_transform>` (when available)
   one has to use the methods and attributes of the stack class, like the ``.data`` attribute and the
   :py:meth:`from_array <bmiptools.stack.Stack.from_array>` method. As example, below is is shown two common step in
   the :py:meth:`transform <bmiptools.transformation.base.TransformationBasic.transform>` method of practically all the
   plugins


   .. code-block::

      ...
      def transform(self,x,inplace=False):

          x_to_transform = x.data          # get the stack content and store in a numpy array
          ...
          x_transformed = ...              # result of the transformation stored in a numpy array
          if not inplace:

             return x_transformed          # return a numpy array

          else:

             x.from_array(x_transformed)   # overwrite the stack content

      ...


4. The new implemented methods of the plugin class should be divided in two groups: *visible* and *hidden*. Visible
   methods are the ones which can be access to the user normally, while the hidden ones contain the parts of the plugin
   which are necessary for its correct working, but that does not perform any operation useful to the user in a normal
   usage scenario.
