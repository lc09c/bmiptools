===================
General conventions
===================


For developer it can be useful to have a rough idea about the bmiptools library organization and its basic building
blocks, which is briefly described here.

The source code of bmiptools is logically organized as follow:

1. in the *core* folder, all the low level utility functions and classes are collected. The utility functions are
   roughly divided by scope: there are the gpu related low level functions in ``gpu_utils.py``, the image processing
   related low level functions in ``ip_utils.py``, the math related functions in ``math_utils.py``, and the other
   general purpose utility functions are collected in ``utils.py``. In ``base.py`` the basic class used to propagate
   all the global setting through the bmiptool library is present. :ref:`Below <core_basic_class>` this class is
   decribed.

2. in the *gui* folder, all the gui related functions and classes are collected. The basic one are in ``gui_basic.py``,
   while classes producing the actual bmiptools gui are collected in ``bmiptools_gui.py``. For more about that, see
   :doc:`guipi`.

3. in the *setting* folder, all the functions an methods used to set global feature to the bmiptools library are
   collected. In the folder ``file`` can be found the ``global_setting.txt`` where all the global setting of the
   library are stored. Always in ``file`` the list of metadata tags used by the
   :py:class:`ExperimentalMetadataInspector <bmiptools.stack.ExperimentalMetadataInspector>` saved in a txt file can be
   also found.

4. in the *transformation* folder, all the plugin are collected. The plugins are organized according to their scope in
   different folder (``alignment``, ``dynamics``, ``geometric``, and ``restoration``), while functions and classes
   which may be useful for all kind of plugins are collected in the folder ``basic``. In ``base.py`` the basic structure
   of a plugin is contained (see :doc:`plugin structure`, for a code oriented description, and
   :doc:`../Plugins/general`, for plugin usage oriented description).

5. in the *visualization* folder, all the part of the library related to visualization tools are collected.


As general rule, bmiptools has been developed by following the Object-Oriented Programming (OOP) paradigm: each tool of
the library which can be used by the user, is a Python class. The propagation of global setting to the various
components of the library happens via class inheritance.


.. _core_basic_class:

The ``CoreBasic`` and the global settings
=========================================


In bmiptools the global setting of the library are stored in ``global_setting.txt`` which can be found in
``.\setting\file``. This file is read during the initialization of any object of the library, so that the library
behaves according to these setting. Every time a bmiptool onject is imported, the
:py:mod:`CoreBasic <bmiptools.core.base.CoreBasic>` class is run, since it is inherited by all the bmiptools objects.
This class is reported fully below (to show all its hidden methods) to show basic operations that are executed.


.. code-block::


    class CoreBasic:
        """
        Basic class inherited by all the classes of bmiptools.
        """

        def __init__(self):


            self._global_setting_dict = ut.read_global_setting(bmiptools.__global_setting_path__)
            self._basic_setup()

        def _basic_setup(self):

            # verbosity level
            self.verbosity = self._global_setting_dict['verbosity']

            # multiprocessing
            use_multiprocessing = {0:False,
                                   1:True}
            self._use_multiprocessing = use_multiprocessing[self._global_setting_dict['use_multiprocessing']]
            multiprocessing_type = {0:'parallelize_pipeline',
                                    1:'parallelize_plugin'}
            self._use_multiprocessing_type = multiprocessing_type[self._global_setting_dict['multiprocessing_type']]
            self._cpu_buffer = self._global_setting_dict['cpu_buffer']
            self.configure_multiprocessing()

            # gpu optimization
            self._use_gpu = self._global_setting_dict['use_gpu']

        # verbosity controlled i/o methods
        def write(self,x,**kwargs):
            """
            Print the input based to the chosen verbosity level.

            :param x: input to print.
            """
            if self.verbosity == 1:

                print(x,**kwargs)

        def progress_bar(self,i, i_max, bar_length, text_after='', text_before=''):
            """
            Simple and light verbosity controlled progress bar.

            :param i: (int) current index
            :param i_max: (int) max index
            :param bar_length: (int) max length of the progress bar
            :param text_after: (str) text after the progress bar
            :param text_before: (str) text before the progress bar
            """
            if self.verbosity == 1:

                bar = ''
                if text_before != '':

                    bar = text_before + ' | '

                bar = bar + '[' + '#' * int(i / i_max * bar_length) + ' ' * (bar_length - int(i / i_max * bar_length)) + ']'
                if text_after != '':

                    bar = bar + ' | ' + text_after

                print(bar, end='\r')

        def vtqdm(self,x):
            """
            Verbosity controlled tqdm counter for for cycle.

            :param x: iterator
            :return: tqdm(iterator)
            """
            if self.verbosity == 1:

                return tqdm(x)

            else:

                return x

        # multiprocessing methods
        def configure_multiprocessing(self):

            self._n_available_cpu = joblib.cpu_count() - self._cpu_buffer
            if self._n_available_cpu <= 1:

                self._use_multiprocessing = False
                warnings.warn('No multiprocessing possible due to an insufficient number of CPUs. Consider to change the'
                              '\'cpu_buffer\' global variable of the library. Execution continues in normal mode.')



This class is inherited by all the classes of bmiptools and should be inherited by the new ones. Inheritance is what
ensure the propagation of the setting present in ``global_setting.txt`` to any bmiptools object. The methods responsible
for that are the

* ``__init__``, which read the global setting and call the ``_basic_setup()`` to interpret it;

* ``_basic_setup``, which "translate" the global settings in more user friendly flags;

* ``configure_multiprocessing``, which perform basic configuration for the multiprocessing, which is done using the
  `joblib <https://joblib.readthedocs.io/en/latest/>`_ library.

There are also basic functions whose behavior depends on the global setting of bmiptools. This is that case for the
methods below.

.. py:method:: write(self,x)

   Verbosity controlled print.

.. py:method:: progress_bar(self,i, i_max, bar_length, text_after='', text_before='')

   Verbosity controlled progress bar for standard for cycles (it does not work for the one executed in parallel). The
   user needs to specify the current iteration index ``i``, the max number of iteration ``i_max``, and the
   ``bar_length`` parameter, which is the leght in character of the progress bar printed. Text can be added before or
   after the progress bar via the ``text_before`` and ``text_after``, respectively.

.. py:method:: vtqdm(self,x)

   Verbosity controlled `tqdm <https://tqdm.github.io/>`_. It can be used to have a verbosity controlled progress bar
   also fo parallelized for cycles.

These methods should be used in any new plugin to print out messages and/or progress bar, so that the verbosity setting
in the ``global_setting.txt`` effectively control the verbosity level of bmiptools.


General recommendations
=======================


The following general recommendations may help in keeping the code consistent and was (more or less) followed during
the development of the library.


1. The name of the variables, functions or classes should reflect their scope to help the user to inspect the code. It
   is recommend to avoid critical names: a long name made of few words, but with a clear meaning, is always better
   than a short name, which is fast to write for the developer but hard to follow for the rest of the word.

2. Variables names are written with small letters. If more than one word is present in the variable name, it is
   recommended to use underscores for blank spaces.

   e.g.   breaking bad episode -> ``breaking_bad_episode``

3. Functions names are written with small letters. If more than one word is present in the function name, it is
   recommended to use underscores for blank spaces.

   e.g.   play episode -> ``play_episode()``


4. Classes names begin with capital letter. If more than one word is present in its name, every word start with capital
   letters and blank spaces are removed.

   e.g.   House of cards -> ``HouseOfCards``

5. Each function and class should be properly commented. Commenting in a
   `.rst compatible <https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_ format would speed up the
   creation of new documentation for the new developed plugins.