==================
Advanced API usage
==================


The :py:class:`Pipeline <bmiptools.pipeline.Pipeline>` object is the most automatized way to apply a series of
transformations to a stack. By the way it does not allow to have a low level interaction with the individual plugins.
This can be important for example to control the result of a certain transformation on a stack, without applying a full
pipeline of transformation. In bmiptools a 'low-level' interaction with the plugins is possible.


Initialize a plugin
-------------------


In bmiptools the default plugins can be found in :py:mod:`bmiptools.transformation`. A list of the possible available
plugins can be found in the ``PLUGINS`` dictionary of the :py:mod:`bmiptools.setting.installed_plugins` module
(as explained :ref:`here <list_plugins_pipeline>`), which contains also the plugins installed locally by the user
(see :doc:`here <../Developer/plugin installation>` for more details)


.. code-block::

    from bmiptools.setting.installed_plugins import PLUGIN

    print(PLUGINS.keys())


Every plugin in bmiptools are initialized with a dictionary, called
:ref:`transformation dictionary <transformation_dictionary>`, which contains all the plugin parameters. Typically a
plugin has many parameters and the transformation dictionary need to have a specific structure. For this reason
every plugin is equipped with a global attribute called ``.empty_transformation_dictionary`` which can be read without
initializing the plugin. The value stored in this dictionary are the default parameters of the plugin, which can be
used for generic tasks.


.. code-block::

    from bmiptools.transformation import Destriper

    # get the default transformation dictionary
    transformation_dictionary = Destriper.empty_transformation_dictionary
    print(transformation_dictionary)


This system can be used also to set the parameters without the need to reproduce the transformation dictionary structure
so that the plugin can be initialized with the desired setting easily.


.. code-block::

    # set a parameter in the transformation dictionary
    transformation_dictionary['optimization_setting']['opt_bounding_box']['use_bounding_box'] = False

    # initialize the plugin
    destriper = Destriper(transformation_dictionary)


The transformation dictionary has a common structure, whose explanation can be found in :doc:`../Plugins/general`
(together with general information about the plugins), while all the plugin-specific parameters are explained in the
corresponding plugin documentation.

.. note::

    Once that the plugin is initialized, the initialized plugin acquires a series of attributes having the *same name*
    of the parameter in the transformation dictionary. Therefore one can check the parameters value after the
    initialization simply by checking the corresponding class attributes.


    .. code-block::

        # check the value of the parameter 'use_bounding_box'
        print(destriper.use_bounding_box)


    These attributes can also be used to change the parameters after the plugin initialization.


    .. code-block::

        # set parameter value after initialization
        destriper.use_bounding_box = True
        print(destriper.use_bounding_box)


Plugin optimization
-------------------


Many plugin can be optimized. The optimization can be run by calling the method
:py:meth:`.fit <bmiptools.transformation.base.TransformationBasic.fit>` which is present in any
plugin (but only when the plugin can be optimized, this method actually do something). This method takes always as input
the stack on which the optimization have to be done (for the meaning of plugin optimization see
:ref:`here <plugin_optimization_meaning>`). The optimization of the plugin can be done with the following line of code


.. code-block::

    # load/create a stack on which the plugin is applied
    # stack = ...

    # fit the previously initialized plugin
    destriper.fit(stack)


.. attention::

    At the end of the optimization the result of the optimization (i.e. the parameters value found) are stored in the
    corresponding attributes of the plugin class, overwriting the initial value assigned during the optimization.


Apply a plugin
--------------


The application of the plugin can be done with the method
:py:meth:`.transform <bmiptools.transformation.base.TransformationBasic.transform>`, which takes a stack input the stack
on which the plugin is applied.


.. code-block::

    # in place application of a plugin
    destriper.transform(stack)


It is important to know that the content of the `stack` is *overwritten* with the result of the plugin application, i.e.
at the end of the transformation application, the content of the initial stack is updated with th result of the
transformations. This is the default behavior, however this feature can be changed by setting ``inplace=False``.


.. code-block::

    result = destriper.transform(stack,inplace=False)


In this case, `stack` is not overwritten and still contain the initial data. The transformation result is stored in the
numpy array ``result``.


.. attention::

    If the field ``auto_optimize = True`` in the transformation dictionary of a plugin that can be optimized, when the
    :py:meth:`.transform <bmiptools.transformation.base.TransformationBasic.transform>` methods is called but the plugin
    was still not optimized (i.e. the :py:meth:`.fit <bmiptools.transformation.base.TransformationBasic.fit>` method
    was not called), the optimization is executed automatically (i.e. the
    :py:meth:`.fit <bmiptools.transformation.base.TransformationBasic.fit>` method is called internally before
    the application of the transformation).


Get plugin parameters
---------------------


It is possible to get the transformation dictionary with the *actual* status of all the plugin parameters with a single
command. this cna be done calling the
:py:meth:`.get_transformation_dictionary <bmiptools.transformation.base.TransformationBasic.get_transformation_dictionary>`.
This is particularly useful to get access to all the parameters of a plugin at the end of the optimization procedure.


.. code-block::

    current_transformation_dictionary = destriper.get_transformation_dictionary()
    print(current_transformation_dictionary)
