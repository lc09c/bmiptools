==============================
Installation and configuration
==============================


Installation
============


bmiptools is available on `PyPI <https://pypi.org/project/bmiptools/>`_ and can be installed simply using pip.
bmiptools has been developed using Python 3.8. To create and setup the python environment where bmiptools can run, one
needs to install `Anaconda <https://www.anaconda.com>`_ on the computer.

CPU
~~~

To install bmiptools and use it on CPU only open the Anaconda prompt and write the instruction below.

.. code-block::

    $ conda create -n bmiptools_env python=3.8
    $ conda activate bmiptools_env
    $ (bmiptools_env) pip install bmiptools

GPU
~~~

To run bmiptools with GPU acceleration you need a CUDA-compatible GPU having compute capability of 3.5 or higher. To
install bmiptools open the Anaconda prompt and write the instruction below.


.. code-block::

    $ conda create -n bmiptools_env python=3.8
    $ conda activate bmiptools_env
    $ (bmiptools_env) conda install cudatoolkit==10.1.243
    $ (bmiptools_env) conda install cudnn==7.6.5
    $ (bmiptools_env) pip install bmiptools


If all worked correctly, this package and the python environment which is necessary to make bmiptools works has been
installed. To check the successful installation, one may simply get some basic information about bmiptools by plotting
some information. This can be done by executing the 3 line of code below in a python terminal (e.g. in the
`anaconda propt <https://docs.anaconda.com/anaconda/user-guide/getting-started/#cli-hello>`_ which comes from free once
anaconda is installed).


>>> import bmiptools
>>> print(bmiptools.__version__)
'v0.4.0'
>>> print(bmiptools.info())
'Developed by  Curcuraci Luca  @  MPICI - Max Planck Institute of Colloids and Interfaces'
'Tool name:  BioMaterials Image Processing Tools - bmiptools'
'Version:  v0.4.0'
'Tool scope:  Image processing tools for typical FIB-SEM and micro-CT images acquired at the institute.'
'Contributors: '
' ['Bertinetti Luca']'
'Manual available @  https://bmiptools.readthedocs.io/en/latest/ '


.. note::


    It is also possible to install bmiptools from its GitLab repository. To to that it is sufficient to replace the
    last line of the code snapshot above with the line below.


    .. code-block::

       $ (bmiptools_env) pip install git+ssh:git@gitlab.mpikg.mpg.de:curcuraci/bmiptools.git


    This way should be preferred, if one wants to have the most updated version of bmiptools.


Unit test
~~~~~~~~~

It is also possible to check that bmiptools has been correctly installed, by running the unit tests. See `here
<https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/test>`_ to understand how to run them.


Configuration
=============


bmiptools can be configured in order to limit the computational resources used. This operation is normally done the
first time, if needed. The bmiptools configuration is contained in the *global_setting.txt* file, which can be found in
the *./setting/files* folder (the path is specified with respect to the bmiptools library folder). An example of its
content can be found below


.. code-block::

    verbosity = 1
    use_multiprocessing = 1
    multiprocessing_type = 1
    cpu_buffer = 2
    use_gpu = 0


Modifying the values in this file, one may change the global setting of bmiptools. What can be configured in bmiptools
is the following:

- set the verbosity level of the library. Setting ``verbosity = 0`` will reduce the number of printed messages,
  while with ```verbose=1`` all the messages will be printed.

- enable/disable multiprocessing. Setting ``use_multiprocessing=0`` the code is executed on a single core, while with
  ``use_multiprocessing=1`` multiprocessing is enables.

- select the type of parallelization (currently not used).

- specify the number of cpu that are not used. Given a processor with N>1 core and M<N, setting ``cpu_buffer = M`` only
  N-M core are used by bmiptool.

- enable/disable gpu usage (currently under development: leave it equal to 0. In the acutal version the GPU is always
  used if available when needed).


Rather than modifying the *global_setting.txt* directly, one can modify this file using some function of bmiptools. For
example the same configuration above can be obtained as follow:


.. code-block::

    import bmiptools
    bmiptools.set_verbosity(1)
    bmiptools.set_use_multiprocessing(1)
    bmiptools.set_multiprocessing_type(1)
    bmiptools.set_cpu_buffer(2)
    bmiptools.set_use_gpu(0)


A detailed documentation about these function can be found in :py:mod:`bmiptools.setting.configure`. As can be seen from the
documentation, it is possible to specify a different path for the *global_setting.txt*.


.. attention:: The *global_setting.txt* is read every time a plugin, a stack or a pipeline object is initialized. As
               such, changing the value in this file **after** the initialization of one of those object in your script,
               **does not** change the behavior of the library for that plugin/stack/pipeline object until it will be
               reinitialized.
