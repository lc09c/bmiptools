===============
Basic API usage
===============

bmiptools can be used as Python API in your script. The two basic objects of this API are:

* :ref:`Stack objects <stack>`, which can be used to do all the I/O operations;

* :ref:`Pipeline object <pipeline>`, which can be used to apply a series of transformations to a Stack objects.


.. _stack:

Stack
=====

A Stack is the basic object of bmiptools where the data can be stored. A stack can be loaded from an multitiff image or
from a folder containing a collection of tiff images, and saved in the same way. In addition a stack can also be saved
as gif file, to have a rapid 3D preview of the content. Finally one can also initialize an empty Stack and fill it in a
second time with a numpy array. Details on Stack objects and its methods can be found in
:py:class:`bmiptools.stack.Stack`.


Load a Stack
------------


A single multitiff or a collection of tiff images in a folder can be loaded in stack object. For a multitiff one can
use the code below


.. code-block::

    from bmip_tools.stack import Stack

    path_to_multitiff_image = r'PATH_TO_MULTITIFF'
    stack = Stack(path = path_to_tiff_image)


In case the stack is contained in a folder (as collection of tiff) images, the code below show how to load it. Note that
this time you have to specify the path of the folder containing the images.


.. code-block::

    from bmip_tools.stack import Stack

    path_to_tiff_folder = r'PATH_TO_FOLDER'
    stack = Stack(path = path_to_tiff_image,from_folder = True)


.. note::

    Alternatively one can always initialize an empty stack and later use the method
    :py:meth:`Stack.load_stack <bmiptools.stack.Stack.load_stack>` or
    :py:meth:`Stack.load_stack_from_folder <bmiptools.stack.Stack.load_stack_from_folder>`, to load a multitiff stack or
    a stack contained in a folder. The code below shows as example, how to load a stack from a folder in this way.

    .. code-block::

            from bmip_tools.stack import Stack

            path_to_tiff_folder = r'PATH_TO_FOLDER'
            stack = Stack()
            stack.load_stack_from_folder(path=path_to_tiff_folder)


.. _slice_ordering:

Slice loading order
~~~~~~~~~~~~~~~~~~~


The stack is reconstructed assuming that the alphabetic order of the single tiff images is equal to the ordering along
the z-axis. Note that this may not always give the correct order of the slice. For example, if the slice name are

.. code-block::

    slice_01.tiff
    slice_02.tiff
    ...
    slice_09.tiff
    slice_10.tiff

reading the slice in alphabetic order would give

.. code-block::

    slice_01.tiff
    slice_10.tiff
    slice_02.tiff
    ...
    slice_09.tiff

which is clearly the wrong order if the enumeration of files have some sense. This is why the user can choose among
different ordering possibility. This can be done by specifying the ``image_type`` field during the initialization of
the stack.


.. code-block::

    from bmip_tools.stack import Stack

    path_to_tiff_folder = r'PATH_TO_FOLDER'
    stack = Stack(path = path_to_tiff_image,from_folder = True,image_type = 'FIB-SEM')


At the moment two options are possible:

- ``image_type = None``: the slices are loaded according to a simple alphabetic order.

- ``image_type = 'FIB-SEM'``: it is the default value for this field. It assumes that each slice of the stack loaded
  has the following structure:

  .. code-block::

        [ARBITRARY_NAME]slice_[NUMBERS].tiff

  where ``[ARBITRARY_NAME]`` is an arbitrary string of character, while ``[NUMBERS]`` is an arbitrary number. With this
  option, the slice are orderd in increasing order with respect to the number specified in the ``[NUMBER]`` part of the
  name. In this way the problem with the example above disappear.


.. note::

    **How to specify the file extension.**
    Sometimes one need to specify the file extension in order to correctly load the stack (both from folder or from
    multitiff). This can be done by specifying it in the variable ``loading_extension`` of a Stack when you initialize
    it (it is set equal to ``tiff`` as default.)


Load slices
~~~~~~~~~~~


Rather than loading the whole stack, one can load just subset of slices. This can be done initializing an empty stack
al call later the method :py:meth:`Stack.load_slices <bmiptools.stack.Stack.load_slices>` specifying the slice list.
The code below show how this can be done for a multitiff image.


.. code-block::

    from bmiptools.stack import Stack

    path_to_multitiff_image = r'PATH_TO_MULTITIFF'
    stack = Stack()

    slice_list = [0,3,10]                                       # list of slices to load (enumeration start from 0)
    stack.load_slices(path_to_multitiff_image,S=slice_list)


In case the stack is contained in a folder of tiff images, the last line need to be replaced as follow

.. code-block::

    stack.load_slices_from_folder(path=path_to_tiff_folder,S=slice_list)

Keep in mind that the number in the slice list are the position of the path to the slices ordered according to a given
convention. As already explained, the ordering can be specified during the stack initialization via the variable
``image_type`` (see :ref:`above <slice_ordering>`).


Fill a stack
------------


Finally a stack can be initialized empty, and filled later using a numpy array.


.. code-block::

    import numpy as np
    from bmip_tools.stack import Stack

    # empty stack
    stack = Stack(load_stack = False)

    # generate some random content
    x = np.random.uniform(0,1,size=(30,200,200))

    # fill the stack
    stack.from_array(x)


.. _save_stack:

Save a Stack
------------


The content of stack can be saved using the method :py:meth:`Stack.save <bmiptools.stack.Stack.save>`. The code below
show that, producing a tiff file containing the stack.


.. code-block::

    import numpy as np

    saving_path = 'PATH_TO_THE_FOLDER_WHERE THE_STACK_IS_SAVED'
    saving_name = 'STACK_NAME'
    stack.save(saving_path,saving_name,standardized_saving=True,data_type=np.uint8,mode='all_stack')


This code will save the stack as a single multitiff image. To save the stack as a folder containing a tiff image for
each slice, one have to set ``mode = 'slice_by_slice'``. With this option

Another possibility to save a stack is via the method :py:meth:`Stack.save_as_gif <bmiptools.stack.Stack.save_as_gif>`,
which save the stack content as an animated gif. This may help to visualize the 3d features of the stack, but the
resolution is limited by the feature of the GIF format. The code below show how this can be done.


.. code-block::

    import numpy as np

    saving_path = 'PATH_TO_THE_FOLDER_WHERE THE_STACK_IS_SAVED'
    saving_name = 'STACK_NAME'
    stack.save_as_gif(saving_path,saving_name,standardized_saving=True,data_type=np.uint8)


.. note::

    The options ``standard_saving`` and ``data_type`` present in both saving methods are particularly important, and
    deserve some discussion. In order produce images that can be open with the usual image reader, the images need to
    be saved in a specific way, depending on the data format chosen. In particular for an 8-bit integer representation
    (using ``data_type = np.uint8``) the typical image viewer expect that in all the image channels the values are
    integers between 0 and 256. Similarly, for a 32-bit float representation (using ``data_type = np.float32``) the
    typical image viewer expect that in all the image channels the values are 32 bit float between 0 and 1. Even if the
    input stack is in a viewer compatible format, this is not guaranteed anymore after the application of a plugin. The
    option ``standard_saving = True`` rescales the images in a suitable way (based on the data type chosen), so that the
    saved tiff are all viewer compatible.


Basic Stack operations
----------------------


Slicing
~~~~~~~


The data in an a Stack object is stored in the attribute ``.data``, but one can access to the data in a more natural
why. Stack allow a numpy-like slicing, as the code below show


.. code-block::

    import numpy as np
    from bmiptools.stack import Stack

    # fill a stack with some data
    content = np.random.uniform(0,1,size=(20,20,20))
    stack = Stack(load_stack=False)
    stack.from_array(content)

    # get the first 5 slices
    a1 = stack[:5]
    print(a1 == content[:5])

    # get the stack content in the top-left 10x10 square
    a2 = stack[:,:10,:10]
    print(a2 == content[:,:10,:10])

    # get whole stack content and store in a numpy array
    a3 = stack.data
    print(a3 == content)

    a4 = stack[:,:,:]
    print(a4 == content)


Stack statistics
~~~~~~~~~~~~~~~~


As soon as some data is loaded in stack, or a stack is filled, a series of simple statics are computed. In particular,
they are:

* ``.stack_mean``, contains the mean value of the *whole* stack;

* ``.stack_std``, contains the standard deviation of the *whole* stack;

* ``.slices_means``, contains a list of mean values *for each slice* of the stack;

* ``.slices_stds``, contains a list of standard deviations *for each slice* of the stack;

* ``.min_stack``, contain the smallest pixel/voxel value of the *whole* stack;

* ``.max_stack``, contains the largest pixel/voxel value of the *whole* stack;

* ``.min_slices``, contains a list of the smallest pixel values *for each slice* of the stack;

* ``.max_slices``,  contains a list of the largest pixel values *for each slice* of the stack.


The method :py:meth:`Stack.statistics <bmiptools.stack.Stack.statistics>` of a stack object returns a dictionary
containing all these quantities.


.. code-block::

    import numpy as np
    from bmiptools.stack import Stack

    # fill a stack with some data
    content = np.random.uniform(0,1,size=(20,20,20))
    content[2,2,2] = 100                                    # set the maximum of the stack
    stack = Stack(load_stack=False)
    stack.from_array(content)

    # get maximum of the stack
    print(stack.stack_max)

    # get statistics
    print(stack.statistics())


Stack metadata
~~~~~~~~~~~~~~


Sometimes tiff images contains relevant metadata. To load them when also the images are loaded just use the code below:


.. code-block::

    from bmip_tools.stack import Stack

    path_to_stack = r'PATH_TO_STACK'
    stack = Stack(path_to_stack,load_metadata=True)


To load metadata, one have to specify ``load_metada = True`` during the stack initialization. There are 3 type of
metadata that are loaded:

1. **image metadata**: are those metadata containing image information like image color depth, image dimension, image
type, ecc... namely the basic metadata TAG of the tif format, (see
`here <https://www.awaresystems.be/imaging/tiff/tifftags/baseline.html>`_).

2. **experimental metadata**: are those metadata containing the information related to the image acquisition process.
The experimental metadata reading and interpretation in bmiptool is done by
:py:class:`bmiptools.stack.ExperimentalMetadataInspector`.

3. **image processing metadata**: are those metadata containing the information relate to the image processing
transformations done by bmiptools itself. They are produced at the end of the application of a bmiptools Pipeline
(see :ref:`later <pipeline_application>`).


.. attention::

    At the moment the automatic loading of the experimental metadata may work only in a restricted number of cases, due
    to the lack of standardization in the metadata organization.


To access to the metadata at later times one can use the attribute ``.metadata``.


.. code-block::

    print(stack.metadata)


Metadata can be added also at later time, using the method
:py:meth:`Stack.add_metadata <bmiptools.stack.Stack.add_metadata>`. The code below show how to add the
metadata called 'added_metadata' having as content the string 'example content' can be added.


.. code-block::

    stack.add_metadata('added_metadata','example content')
    print(stack.metadata)


The added content can be of any kind (e.g. int, list, dictionary,ecc..) and not only string. Finally, when a stack is
saved and the option ``save_metadata = True`` is used, the metadata dictionary is saved as json file in the same path in
which the stack is saved.


.. _pipeline:

Pipeline
========


The second basic object of the library is the Pipeline object. A pipeline is an object which apply a series of
image-processing transformation to a given input stack. Those image-processing transformation are the so called
bmiptools plugins (see section :doc:`../Plugins/general` to have a list and a description of the currently available
plugins). The main features of a bmiptools pipeline are:

1. A pipeline keeps track automatically of all the parameters used, both the ones chosen by the user and the ones
obtained at the end of an optimization process.

2. A pipeline can be saved and loaded in a later time reproducing exactly the same result.

3. A pipeline can save automatically a preview of a restricted number of slice of the input stack after the
application of each plugin of the pipeline.

To use a pipeline of transformation on a stack one have to create and initialize a Pipeline object. After
that the pipeline applied to a stack object and later can be saved. In general, this is the typical order that one need
to follow to use pipeline objects in bmiptools. Alternatively, rather that create and initialize a pipeline, one can
simply load an already existing one.


.. _list_plugins_pipeline:

List available plugins
----------------------


To have an idea on the kind of transformations that can be applied to a stack, one can list the available plugins.
The list of the currently available plugin is contained in the ``PLUGINS`` dictionary of the
:py:mod:`installed_plugins <bmiptools.setting.installed_plugins>` module. This dictionary is imported in
:py:mod:`bmiptool.pipeline` file, therefore ``PLUGINS`` is a global attribute of the pipeline module. Thus the
list of installed plugins can be obtained as follow:


.. code-block::

    from bmiptools.pipeline import PLUGIN

    print(PLUGINS.keys())


More information about currently installed plugins can be found in the section :doc:`../Plugins/general`.


Pipeline creation
-----------------


A pipeline can be created from scratch, with the method :py:meth:`Pipeline.create <bmiptools.pipeline.Pipeline.create>`.
When calling this method, one need to:

1. specify a list of plugins writing the name of the plugins and their order of application in the list (plugins can
   be repeated multiple times);

2. specify a folder used to save all the pipeline information;

3. (optional) specify a pipeline name.

The name of the plugins are the one that can be seen when they are listed (see :ref:`above <list_plugins_pipeline>`).
The code below is an example of how to create a pipeline.


.. code-block::

    from bmip_tools.pipeline import Pipeline

    operation_lists = ['Standardizer','Flatter','Decharger']
    pipeline_path = r'PATH_TO_PIPELINE_FOLDER'
    name = 'NAME'

    pipeline = Pipeline(operation_lists = operation_lists,
                        pipeline_folder_path = pipeline_path,
                        pipeline_name = name)


The order given in ``operation_list`` is the order in which the plugins are applied to the stack. Once that the pipeline
is created by executing the code above, a json file is created in the pipeline folder. This
``pipeline_[PIPELINE_NAME].json`` file is called *pipeline json* and contains all the information about the pipeline
and represent the way the user can interact with all the plugins setting, when pipeline objects are used. In this json
file, the field `pipeline_setting` contains a series of dictionary (one for each plugin) containing all the parameters
of the plugins. The user have to set these parameter manually and save the json file once that this is done. The meaning
of the various parameters for each plugins can be found in section :doc:`../Plugins/general`.


.. attention::

    **Fit order.**
    By default a plugin is fitted (if possible) just before the application of it on the stack. On the
    other hand the fit and application of the plugin may be done in different time. This can be done by specifying when
    the fit have to be done in the ``operation_lists`` by writing ``fit_`` before the name of the plugin. In the example
    below, the fit of the ``Flatter`` plugin happens before the application of the ``Decharger`` plugin, and only then
    the ``Flatter`` plugin is applied.


    .. code-block::

        operation_lists = ['Standardizer','fit_Flatter','Decharger','Flatter']


.. _configure_pipeline_json:

How to configure the pipeline json setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The pipeline json produced once a pipeline is created contains for each plugin of the pipeline all the parameters which
can be set by the user. The structure of this json is in general the following.


.. code-block:: none

    {"pipeline_name": "pipeline__01011901_0000",
    "pipeline_creation_date': "01/01/1901 at 00:00",
    "bmiptools_version": "v0.5",
    "plugins_list": ["Plugin_1",...,"Plugin_N"],
    "true_operations_list": ["fit_Plugin_1","Plugin_1",...,"fit_Plugin_N","Plugin_N"],
    "pipeline_setting":{"Plugin_1": {
                                     ...        # transformation dictionary Plugin_1
                                     },
                        ...
                        "Plugin_N": {
                                     ...        # transformation dictionary Plugin_N
                                     }
                        }
    }


As mentioned above, the parameters for each plugin can be found in the ``"pipeline_setting"`` field. In this field,
the parameters for the plugin ``Plugin_x`` can be found in the dictionary in the field having the same plugin name.
This dictionary is called *transfomation dictionary* and a description of its general structure and the explanation of
some general parameters can be found :ref:`here <transformation_dictionary>`, while for each plugin in this
documentation all the plugin specific parameters are explained in the corresponding plugin page.


.. _pipeline_json_rules:

.. attention::

    **Python dictionaries and json files.** bmiptools is written in Python. As such the code snapshot in this
    documentation are generally written in python. By the way the pipeline json is written in json (as the code snapshot
    above show). The code snapshots of the transformation dictionary of the various plugins are written in Python (since
    they are Python dictionaries).  Therefore if one want to use this documentation to fill the pipeline json, one need
    to *convert* the Python notation (data-structure to be precise) into the JSON one. Fortunately the two notations are
    already very similar, and only  few things need to be changed. The table below should be sufficient for this scope.


    .. table::
       :align: center

       +--------------------+------------------+
       |       Python       |       JSON       |
       +====================+==================+
       |       ``'``        |       ``"``      |
       +--------------------+------------------+
       | ``numpy.array([])``|       ``[]``     |
       +--------------------+------------------+
       |      ``True``      |     ``true``     |
       +--------------------+------------------+
       |      ``False``     |     ``false``    |
       +--------------------+------------------+
       |      ``None``      |     ``"null"``   |
       +--------------------+------------------+


    See `here <https://realpython.com/python-json/>`_ for more details on the Python-JSON conversion. An example of
    conversion can be the following.


    .. table::
       :align: center

       +----------------------------------------+------------------------------------+
       |            Python dictionary           |                JSON file           |
       +========================================+====================================+
       |.. code-block::                         |.. code-block:: json                |
       |                                        |                                    |
       |   {'key1': numpy.array([[0,1],[1,0]]), |   {"key1": [[0,1],[1,0]],          |
       |   'key2': None,                        |   "key2": "null",                  |
       |   'key3': False,                       |   "key3": false,                   |
       |   'key4': {'key41': None,              |   "key4": {"key41": "null",        |
       |           'key42': True                |           "key42": true            |
       |            }                           |            }                       |
       |   }                                    |   }                                |
       |                                        |                                    |
       +----------------------------------------+------------------------------------+


Load pipeline template
----------------------


Rather than create a pipeline from zero, one can create them one time and save the pipeline json produced in some folder
and use it different times. In order to create a pipeline object in this way, one has to first create an empty pipeline
object, and load the template in a later time with the method
:py:meth:`Pipeline.load_pipeline_template_from_json <bmiptools.pipeline.Pipeline.load_pipeline_template_from_json>`.
The code below show how this can be done.


.. code-block::

    from bmiptools.pipeline import Pipeline

    path_to_pipeline_template = r'PATH TO PIPELINE TEMPLATE JSON'
    path_to_pipeline_folder = r'PATH TO PIPELINE FOLDER'

    pipeline = Pipeline()                                                # initialize an empty pipeline
    pipeline.load_pipeline_template_from_json(pipeline_template_path = path_to_pipeline_template,
                                              new_pipeline_folder_path = path_to_pipeline_folder)



Pipeline initialization
-----------------------


Once that the pipeline is created and the pipeline json is filled, or once that a pipeline template is loaded, the
pipeline object can be initialized. This operation initialize all the specified plugins, i.e. executing all the input
independent operations for each plugin, so that the pipeline is ready for the application to a stack. The pipeline can
be initialized using simply the code below.


.. code-block::

    pipeline.initialize()


.. _pipeline_application:

Pipeline application
--------------------


The application of the pipeline (with eventual fitting according to the order specified during the creation) on some
stack called ``stack``, can be done simply as follow:


.. code-block::

    pipeline.apply(stack)

.. note::

    The order in which the plugins are fitted and applied can be seen from the pipeline json at the
    ``true_operations_list`` field. This field contains a list with the name of the true operations that are
    applied at a given step. For example given


    .. code-block::

        true_operations_list = ['fit_Flatter','Flatter','fit_Registrator','fit_HistogramMatcher',
                                'HisogramMatcher','Registrator']

    one can understand that the ``Flatter`` plugin is first fitted and then applied to the input stack, later the
    ``Registrator`` plugin is fitted *but not applied*. Indeed after this operation ``HistogramMatcher`` is fitted
    and then applied, and only at the end the (already fitted) ``Registrator`` plugin is applied.


.. _pipeline_preview:

Get a preview
~~~~~~~~~~~~~


There is the possibility to obtain a preview showing how the input stack is transformed at each step of the pipeline
(i.e. after the application of each plugin of the pipeline). In order to do that, one have to call the method
:py:meth:`Pipeline.setup_preview <bmiptools.pipeline.Pipeline.setup_preview>` *before* the application of the pipeline.
In this method, one has to specify:

1. ``slice_list``, namely the list of integer indicating slice used to produce the preview.

2. ``plugin_to_exclude``, namely a list containing the name of the plugins which are not considered for the
   construction of the preview.

The code below should be used in order to get the preview *during* the execution of the pipeline, instead of the
previous line of code.


.. code-block::

    pipeline.setup_preview(slice_list = [0,1,5,7],                              # specify preview setting.
                           plugin_to_exclude = ['Standardizer','Registrator'])
    pipeline.apply(stack)                                                       # apply pipeline on the stack.


As soon as the pipeline is applied, a folder inside the pipeline folder called ``preview`` is created, and inside the
slices specified in ``slice_list`` as saved before the application of any transformation in the folder 'original'.
During the pipeline application, after the application of each plugin a folder with the name of the plugin is created,
provided that the  plugin is not in the  ``plugin_to_exclude`` list. In this folder the selected slice of the stack at
that step of the pipeline are saved.


.. _pipeline_saving:

Pipeline saving
---------------


After the application of the pipeline two things happens:

1. The stack object now contains the result of all the plugin applied according the specified order.

2. The plugins forming the pipeline has been optimized (the ones that can be fitted) on the specific input (the input
   stack for the first plugin, the output of the plugins preceding the corresponding ``fit_`` methods for all the
   other).

The pipeline at this point can be saved with the :py:meth:`Pipeline.save <bmiptools.pipeline.Pipeline.save>` method.


.. code-block::

    pipeline.save()


.. attention::

    The stack have to be saved separately using the methods described :ref:`before <save_stack>`. Saving the pipeline
    does not save the stack automatically!

The saving process produces two file in the pipeline folder chose in the beginning (during the creation or during the
template loading):

1. A '.dill' file, which really contain the pipeline. This is the file that need to be used to load a pipeline. In case
   some plugin has dill incompatible component, an additional ``undillable`` folder is created. This folder contains the
   part of the pipeline that require a custom saving and loading operations. This folder need to be in the same folder
   of the dill file, in order to load the pipeline later.

2. A json file containing the pipeline json *update*, i.e. containing the parameters found during the optimization of
   the plugins (if any).

.. note::

    Note that a pipeline can be saved also after the initialization (but before the application).

Pipeline loading
----------------


Once that the pipeline has been saved, it can be load with the method
:py:meth:`Pipeline.load <bmiptools.pipeline.Pipeline.load>`. The code below, show how one can use it.


.. code-block::

    path_to_pipeline_file = r'PATH_TO_DILL_FILE'
    pipeline.load(path_to_pipeline_file)


After the loading the pipeline, it can be applied using the code explained in the
:ref:`apply subsection <pipeline_application>` above. However, in case the pipeline was saved after a fit, the application of
the loaded pipeline does not execute a new fit, but uses the parameters found previously.


Further reading
===============


Tutorials:

* :doc:`../Miscellaneous/basic stack-pipeline`
