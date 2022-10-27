=========
GUI usage
=========


bmiptools is equipped also with a basic graphical interface. In order to use it, one need to have a python terminal
installed on its PC. Here the one provided by `Anaconda <https://www.anaconda.com/>`_ is used.


Run the GUI
===========


To run the bmiptool GUI it open the Anaconda Prompt and activate the bmiptools environment. At this point one has to
execute the ``run_gui`` module of bmiptools with the python interpreter using the ``-m`` option. More precisely,
assuming bmiptools has been installed in the environment called ``bmiptools_env``, the activation of the environment and
the launch of the GUI can be done with the two following line


.. code-block::

    $ conda activate bmiptools_env
    $ (bmiptools_env) python -m bmiptools.run_gui


The short clip below show how this can be done one a Windows 10 compute with anaconda already installed.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/HVc86Ih1mQY">
     </iframe>
     </centering>


Load a stack
============


The clip below show how a stack of tiff images can be loaded from a folder. The loading operation terminates when
``"Stack loaded!"`` is printed on the terminal.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/1K5QpdCfLoU">
     </iframe>
     </centering>


Create and initialize a pipeline
================================


The creation and initialization of a pipeline with the bmiptool GUI is showed in the clip below. By clicking on the
``create and initialize pipeline``, a windows where the pipeline can be created by adding the various plugins. In this
window one has also to specify the working folder of the pipeline. To initialize each plugin click on the ``setting``
button and, once the plugin configuration windows opens, click on ``ok``, after modifying the parameters if needed. When
this operation is fully executed, ``"Pipeline created and initialized!"`` appears on the terminal.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/NvrowwatwJ4">
     </iframe>
     </centering>


.. attention::

    In order to add and correctly initialize the plugins in the pipeline, always click on the setting ``setting`` and
    then click on ``ok``, possibly after modifying the parameters.


Load a pipeline template
========================


The creation and initialization of a pipeline can happens also ina different way: via a pipeline template. This is a
json file containing all the pipeline parameters (see :ref:`here <configure_pipeline_json>` to get more information
about its structure). At the end of this operation ``"Pipeline template loaded!"`` is printed on the terminal.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/EtGRb5iHYFs">
     </iframe>
     </centering>


.. _gui_apply_and_preview:

Apply pipeline and previews
===========================


To apply the pipeline crated to the stack (running also the plugins optimizations if available) simply click on the
button ``Apply pipeline``. If a preview of the final result is needed, *before* to click on 'Apply pipeline' one needs
to configure the preview. This can be done by clicking ``Preview setting``, specify the preview setting and then
apply the pipeline. Once that the pipeline has been applied on the stack, ``Pipeline applied!`` is printed on the
terminal.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/XmZYsoZcqXg">
     </iframe>
     </centering>


Save results
============


Once that pipeline has been applied to the stack, one can do two things: save the resulting stack and save the trained
pipeline. To save stack simply click on ``Save stack``: when the stack is saved in the selected folder
``"Stack saved!"`` is printed on the terminal. To save the pipeline click on ``Save pipeline``: a .dill file will be
produced in the pipeline folder selected, while the pipeline json will be updated with the parameters found
during the optimization routine (if any). The clip below shows both these operations.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/71aNem37SHE">
     </iframe>
     </centering>


Load an existing pipeline
=========================


Once that a pipeline has been saved, a '.dill' file is created in the pipeline folder (plus eventually a folder called
'undillable', see :ref:`here <pipeline_saving>` for more information). This file is the one containing all the pipeline
parameters (possibly determined by the optimization procedure) and can be read by bmiptools to reproduce exactly the
same pipeline later or on a different computer. the clip below show how to load a pipeline with the bmiptoos GUI. When
the loading is terminated, ``"Pipeline loaded!"`` appears in the terminal window.


.. raw:: html

     <centering>
     <iframe width="630" height="473"
      src="https://www.youtube.com/embed/6LLQSLOUd7Q">
     </iframe>
     </centering>


At this point, one can apply the pipeline simply by clicking on ``Apply pipeline`` button. In this case no optimization
routines are executed, and the (already trained) plugins are simply applied to the stack.


Further reading
===============


Tutorials:

* :doc:`../Miscellaneous/basic stack-pipeline`