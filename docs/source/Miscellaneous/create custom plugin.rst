==================================
Create and install a custom plugin
==================================


In this tutorial, it will be showed how a custom plugin can be created and installed in bmiptools. The plugin created
will perform the gamma correction of images, and a simple optimization procedure to detect low contrast images and good
parameters to enhance it is also sketched. It is not guaranteed that the plugin here perform in a meaningful manner
on images, and have to be understood just as an example to illustrate the plugin creation and installation in bmiptools.


An example of custom plugin
===========================


The custom plugin created perform the gamma correction of the images. In particular, given a stack :math:`S(k,j,i)` it
perform the following transformation


.. math::

    S(k,j,i) \rightarrow S_{output}(k,j,i) = S(k,j,i)^\gamma


with :math:`\gamma > 0`. This plugins has also a simple optimization routine. By checking on how the average value of
the image compare with respect to the value corresponding to half of the image dynamical range associate to the image
type one can decide if the image dynamics need to be stretched (i.e. :math:`\gamma > 1`) or compressed
(i.e. :math:`0 < \gamma < 1`). Then the initial value of :math:`\gamma = 1` is increase or decreased till the output
image is not anymore a low contrast image (low contrast images are detected via the ``is_low_contrast``
function of `skimage.exposure
<https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.is_low_contrast>`_). Without
optimization, this plugin simply reduce to a wrapper round the ``adjust_gamma`` function of `skimage.exposure
<https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.adjust_gamma>`_


.. code-block::

    import numpy as np

    from skimage.exposure import is_low_contrast,adjust_gamma

    from bmiptools.transformation.base import TransformationBasic
    from bmiptools.gui.gui_basic import GuiPI


    class MyPlugin(TransformationBasic):

        empty_transformation_dictionary = {'auto_optimize': True,
                                           'optimization_setting': {'gamma_step': 0.1,
                                                                    'gamma_min': 0.1,
                                                                    'gamma_max': 3
                                                                    },
                                           'gamma': 1}
        _guipi_dictionary = {'auto_optimize': GuiPI(bool),
                             'optimization_setting': {'gamma_step': GuiPI(float,min=0.01,max=1),
                                                      'gamma_min': GuiPI(float,min=0.01,max=1),
                                                      'gamma_max': GuiPI(float,min=1,max=5),
                                                      },
                             'gamma': GuiPI(float,min=1,max=5)}
        def __init__(self,transformation_dictionary):

            super().__init__(TransformationBasic)
            self.fit_enable = True

            self.auto_optimize = transformation_dictionary['auto_optimize']
            if self.auto_optimize:

                self.gamma_step = transformation_dictionary['optimization_setting']['gamma_step']
                self.gamma_min = transformation_dictionary['optimization_setting']['gamma_min']
                self.gamma_max = transformation_dictionary['optimization_setting']['gamma_max']

            self.gamma = transformation_dictionary['gamma']
            self._setup()

        def _setup(self):

            if self.auto_optimize:

                self.gamma_range_above = np.arange(1,self.gamma_max,self.gamma_step)
                self.gamma_range_below = np.arange(1,self.gamma_min,-self.gamma_step)

        def fit(self,x):

            slice_tested = x[0,:,:]
            slice_tested = (slice_tested-slice_tested.min())/(slice_tested.max()-slice_tested.min())
            if np.mean(slice_tested) >= 0.5:

                par_range = self.gamma_range_above

            else:

                par_range = self.gamma_range_below

            parameter_found = False
            for gamma_tested in par_range:

                res = adjust_gamma(slice_tested,gamma=gamma_tested,gain=1)
                if not is_low_contrast(res,fraction_threshold=0.5,lower_percentile=10,upper_percentile=90):

                    self.gamma = gamma_tested
                    self.fit_enable = False
                    parameter_found = True
                    break

            if parameter_found == False

                self.gamma = 1
                self.fit_enable = False
                self.write('No gamma value found: gamma = 1 used instead.')

        def transform(self,x,inplace=True):

            if self.fit_enable:

                self.fit(x)

            result = []
            for i in range(len(x)):

                result.append(adjust_gamma(x[i,:,:],gamma=self.gamma,gain=1))

            if not inplace:

                return np.array(result)

            x.from_array(np.array(result))


This custom plugin has all the necessary features in order to be fully compatible with bmiptools. They are summarized
below


1. The plugin is equipped with the ``empty_transformation_dictionary`` containing all the plugin setting and it is
   organized in the standard way (see :ref:`here <transformation_dictionary>` and
   :ref:`here <default_global_attributes_plugins>`).

2. The ``_guipi_dictionary`` contains all the variable specified in the empty transformation dictionary with the
   corresponding GuiPI (see :ref:`here <default_global_attributes_plugins>`).

3. The attribute names are the ones used in the transformation dictionary.

4. The input independent preliminary operations are contained in the ``_setup`` method, while the optimization routine
   is written in the :py:meth:`fit <bmiptools.transformation.base.TransformationBasic.fit>` methods. The ``fit enable``
   attribute is correctly created in the ``__init__`` methods, and disabled when the fitting procedure terminate.

5. The :py:meth:`transform <bmiptools.transformation.base.TransformationBasic.transform>` method is correctly implemented.

6. :py:class:`TransformationBasic <bmiptools.transformation.base.TransformationBasic>` correctly inherited by the plugin
   (see :ref:`here <TransformationBasic>` for more information).

7. Messages are printed using the verbosity controlled function :py:meth:`write <bmiptools.core.base.CoreBasic.write>`,
   so that the bmiptools global setting can silent them.


Plugin installation
===================


What is left to do is to install the custom plugin. According to the :doc:`../Developer/plugin installation` section,
it is sufficient to create a new python script containing the two lines below


.. code-block::

   from bmiptools.setting.configure import install_plugin


   install_plugin(r'../[...]/my_plugin.py','MyPlugin')


where here is assumed that script containing the custom plugin ``MyPlugin`` has (absolute) path
``../[...]/my_plugin.py``. It is sufficient to run the created script with the python interpreter (clearly in the same
python environment where bmiptools is installed) in order to permanently install the plugin. Once that this is
done, one cna check the installation by looking at the ``LOCAL_PLUGINs`` dictionary, i.e.


.. code-block::

   from bmiptools.setting.installed_plugins import LOCAL_PLUGINS

   print(LOCAL_PLUGINS)


.. warning::

   Once a plugin is installed, bmiptools will always look for that plugin at the path specified during the installation.
   As such it is recommend to do change the position of the script of the custom plugins once installed.