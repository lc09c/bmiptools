==========================================
Basic operations with stacks and pipelines
==========================================

In this tutorial it is showed how to construct a pipeline for a given input stack, by arguing why a certain plugin is
used and its position in the pipeline when this is possible.


The input stack and its problems
================================


The input stack used for this tutorial is showed below.

.. image:: ../_images/Miscellaneous/basic_stack-pipeline/input_stack.gif
   :class: align-left
   :width: 4000px
   :height: 3000px
   :scale: 20

The first thing to do, is to understand which kind of artifacts are present on these images, and define a pipeline
accordingly. Consider the slice below.

.. image:: ../_images/Miscellaneous/basic_stack-pipeline/input_slice.png
   :class: align-left
   :width: 4000px
   :height: 3000px
   :scale: 20

Since the interesting part of the sample is in the center, the two horizontal bands on the top and on the bottom of the
images should be eliminated. This can be done with the :doc:`Cropper <../Plugins/cropper>` plugin. This should helps
for two reasons:

1. First of all, eliminating the uninteresting parts of the stack reduce the overall ammount of computations needed
   for the artifacts correction, i.e. the time and RAM memory taken to perform the corrections are reduced.

2. Second, the kind of discontinuities between the central part of the sample and the two horizontal bands, may
   introduce additional artifacts in the border regions, when certain plugins are applied (e.g. the
   :doc:`Destriper <../Plugins/destriper>` plugin).

Therefore the first plugin in the pipeline in this case should be the :doc:`Cropper <../Plugins/cropper>`.

Many algorithm works better if the pixels of the input images takes value in [0,1]. Moreover may of the default
parameters of the bmiptools plugins has been derived with images taking value son the [0,1] range. Therefore at this
point it is a good idea to apply the :doc:`Standardizer <../Plugins/standardizer>` plugin, to rescale each slice of the
stack in the [0,1] range.

After that it is logical to apply all the plugins which may "homogenize the stack along the z-axis" which does not
need an optimization procedure. The only plugin available for this scope at the moment is the
:doc:`HistogramMatcher <../Plugins/histogram matcher>`. The logic behind this "homogenization along the z-axis" is that
the estimation of the parameters of the optimizable plugins should be more robust in this way. By the way keep in mind,
that this step can be  applied only if no meaningful variation along the z-axis of the stack is expected (which is
assumed for this example). Moreover from the animation above, one can clearly see some sudden brightness variation which
is typically not expected.

Summarizing according to the motivations above, the next two plugins of the pipeline should be the
:doc:`Standardizer <../Plugins/standardizer>` followed by the :doc:`HistogramMatcher <../Plugins/histogram matcher>`.

At this point it is reasonable to start to correct the main artifacts of the stack: curtaining and charging. By the
way it can be reasonable to estimate now the parameters of the :doc:`Registrator <../Plugins/registrator>` plugin.
Indeed, being the vertical stripes real, they can be very helpful in the estimation of the parameters for the
registration. Because of that, at this point of the pipeline the :doc:`Registrator <../Plugins/registrator>` is
*fitted*.

After that one can really start to remove the curtaining artifact by means of the
:doc:`Destriper <../Plugins/destriper>` plugin. According to the tips which can be found in the plugin documentation
page, being the stripes stronger in the bottom part of the image, one should use a bounding box centered on this part
of the slice.

After destriping, one can proceed with the reduction of the charging artifact. Therefore at this point the
:doc:`Decharger <../Plugins/decharger>` plugin can be applied. After decharging one may flatten the image using the
:doc:`Flatter <../Plugins/flatter>` plugin, however here it is assumed that the variation of brightness in the yx-plane
still has meaning: as such this plugin is not applied.

The last artifact to remove is the noise. This can be done before applying the registration algorithm provided that only
2d denoising algorithm are applied (otherwise the denoising step has to be applied *after* the application of the
registration algorithm). It is a good idea to denoise the stack towards the end of the pipeline since the other steps
may "introduce some further noise" or amplify the existing one (a denoiser reduce the noise level but does not eliminate
it in general). At this point of the pipeline it is not clear how the noise distribution should look like, therefore it
is better to use denoising algorithm which do not require assumptions about the noise structure. The :doc:`DenoiserDNN
<../Plugins/denoiserDNN>` plugin has this feature, and therefore will be used in this pipeline.

The last operation to do is the application of the :doc:`Registrator <../Plugins/registrator>` plugin, with the
parameters estimated before the removal of the curtaining artifact. Possibly the refinement with the optical flow
registration can be done. However before to do that, a technical step may be necessary. It is not indeed guaranteed that
the range of the images remains between 0 and 1, after the application of the 3 previous plugins. The registration step
need to "expand" the input images, in order to accommodate the possible movements. This "expansion" is done by filling
the new pixels with some value (0 is the default value for that). By the way if the images may assume negative values,
it can be that 0 (assuming to use the default value) is in between the image range, i.e. would correspond to regions
of the sample which are not empty. This would give rise to a final result which is not very natural. For that reason it
is a good idea to apply again the :doc:`Standardizer <../Plugins/standardizer>` (with ``standardizer_mode = 0/1``)
*before* to apply the :doc:`Registrator <../Plugins/registrator>` plugin. In this way, one is certain that the lowest
possible value in the image corresponds to the value used to "expand" the image during the registration.

To conclude, according to all the considerations above, the pipeline that can be deduced from the observation of a
slice of the stack and from some additional consideration on the nature of the sample, is the following


.. code-block::

    [Cropper, Standardizer, HistogramMatcher, fit_Registrator, Destriper, Decharger, DenoiseDNN,
     Standardizer, Registrator].



Post-processing using bmiptools pipelines
=========================================


The code below show how to load the stack and apply the pipeline described in the previous section, saving the
result obtained at the end. For the details about the various function used and their meaning, the section
:doc:`../Usage/basic api usage` contains all the necessary informations.


.. code-block::

    ### Imports

    import numpy as np

    from bmiptools.stack import Stack
    from bmiptools.pipeline import Pipeline
    from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2D as b2d


    ### Inputs

    # stack related
    path_to_sample_stack = ...  # path to the stack to correct
    final_stack_path = ...      # saving path of the final stack
    final_stack_name = ...      # saving name of the final stack

    # pipeline related
    pipeline_folder_path = ...  # path to the pipeline working folder
    pipeline_name = None        # name of the pipeline (optional)
    pipeline_op_list = ['Cropper','Standardizer','HistogramMatcher',
                        'fit_Registrator','Destriper','Decharger',
                        'DenoiseDNN','Standardizer','Registrator']


    ### Correct stack using a pippeline

    # load a sample stack
    sample = Stack(path=path_to_sample_stack,load_metadata=True,from_folder=True)

    # create a pipeline
    pip = Pipeline(operation_list = pipeline_op_list,
                   pipeline_folder_path = pipeline_folder_path,
                   pipeline_name = pipeline_name)

    # initialize the pipeline AFTER specification of the parameters in json of the pipeline
    pip.initialize()

    # apply the pipeline
    pip.apply(sample)

    # save the pipeline
    pip.save()

    # save the final stack
    sample.save(saving_path = final_stack_path,
               saving_name = final_stack_name,
               standardized_saving = True,
               data_type = np.uint8,
               mode = 'slice_by_slice')


Alternatively one can use the bmiptools GUI. The section :doc:`../Usage/GUI usage` and the videos therein should be
sufficient to clarify how this can be done.

The animation below shows how a slice of the input stack changes throughout the pipeline (see
:ref:`here <pipeline_preview>` to understand how previews can be obtained in the python API, or
:ref:`here <gui_apply_and_preview>` in the bmiptools GUI).


.. image:: ../_images/Miscellaneous/basic_stack-pipeline/pipeline_animation.gif
   :class: align-left
   :width: 710px
   :height: 564px
   :scale: 100


Final result
============


The result of the pipeline described above using the code described in the previous section can be seen in the animation
below.


.. image:: ../_images/Miscellaneous/basic_stack-pipeline/processed_stack.gif
   :class: align-left
   :width: 4000px
   :height: 3000px
   :scale: 20


Considering the same slice considered above, the result obtained is the following.


.. image:: ../_images/Miscellaneous/basic_stack-pipeline/processed_slice.png
   :class: align-left
   :width: 4000px
   :height: 3000px
   :scale: 20


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Miscellaneous/basic_stack-pipeline>`_. To reproduce the images showed
   above one may consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/
   tree/master/examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can
   find all the necessary input data.