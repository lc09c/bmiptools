=====================================
Case of study: destriper optimization
=====================================


Here the optimization routine of the destriper plugin is briefly discussed with a practical example. In the
:ref:`Implementation details <destriper_implementation_details>` section of the Destriper plugin was discussed how the
filter used by the plugin works, and how it can be optimized.


.. note::

    The following imports are needed to run the code snapshots below.

    .. code-block::

       import numpy as np
       import pywt

       from scipy import fftpack


From a practical point of view, the filter :math:`f_{w,l,\sigma}` used in the destriper plugin can be implemented with
the function below.


.. code-block::

   def destripe_slice(x, wavelet_name, sigma, level):
       """
       Core destriper transformation which is applied to a slice of a stack.

       :param x: (ndarray) array containing the image to process.
       :param wavelet_name: (str) name of the wavelet to be used.
       :param sigma: (float) standard deviation of the gaussian filter used to remove vertical lines.
       :param level: (int) decomposition level of the wavelet transform
       :return: (ndarray) the destriped image.
       """

       res = pywt.wavedec2(x, wavelet_name, level=level)
       filtred_res = []
       for coeff in res:

           if type(coeff) is tuple:

               cV = coeff[1]
               fft2_cV = fftpack.fftshift(fftpack.fft2(cV))
               size_y, size_x = fft2_cV.shape

               x_hat = (np.arange(-size_y, size_y, 2) + 1) / 2
               filter_transfer_function = -np.expm1(-x_hat ** 2 / (2 * sigma ** 2))
               filter_transfer_function = np.tile(filter_transfer_function, (size_x, 1)).T
               fft2_cV = fft2_cV * filter_transfer_function

               cV = fftpack.ifft2(fftpack.ifftshift(fft2_cV))
               filtred_res.append((coeff[0], np.real(cV), coeff[2]))

           else:

               filtred_res.append(coeff)

       return pywt.waverec2(filtred_res, wavelet_name)


This function is exactly equal to the current filter function implementation of the
:py:class:`Destriper <bmiptools.transformation.restoration.destriper.Destriper>` class.


The optimization routine
========================


The parameter space used for the optimization routine is defined as follow


* all the wavelet available in bmiptools should be tested;

* the values of :math:`\sigma` tested are the ones between 0.01 and 50 with a step of 1;

* the decomposition level :math:`l` is set to be equal to the maximum compatible with the image input shape and the
  wavelet used.


The function below can be used to generate the parameter space, according to the 3 conditions above. The function
takes as argument the input image shape, the list of the possible values of :math:`\sigma`, and the list of the possible
wavelets names.


.. code-block::

    def generate_destriper_parameter_space(image_shape,sigma_range,wavelet_range):
        """
        Compute all the possible parameters combinations given the individual parameters ranges.

        :param image_shape: (tuple) shape of the image used for the loss computation.
        :param sigma_range: (list[float]) list of values of possible sigma.
        :param wavelet_range: (list[str]) list of possible wavelet names.
        :return: (list[list]) the parameter space.
        """
        param_space = []
        for wname in wavelet_range:

            Lmax = pywt.dwtn_max_level(image_shape, wname)
            for sigma in sigma_range:

                param_space.append([wname,sigma,Lmax])

        return param_space


The list of all the available wavelets in bmiptools is stored in the variable ``SUPPORTED_WAVELET``, and can be
obtained as showed below.


.. code-block::

   from bmiptools.transformation import SUPPORTED_WAVELET


Assume to apply the optimization routine on the slice ``sl`` of some stack. In total, with the parameter space
boundaries chosen, there are 5300 possible combinations to test.


.. code-block::

    sl =  ... # slice of stack on which the destriper optimization is applied

    # define parameter space boundaries
    sigma_range = np.arange(0.01,50,1)
    wavelet_range = SUPPORTED_WAVELET
    image_shape = sl.shape

    # generate parameter space
    pspace = generate_destriper_parameter_space(image_shape,sigma_range,wavelet_range)
    N_param_comb = len(pspace)
    print('Total number of parameters combinations: ',N_param_comb)


For the optimization, the loss function :math:`\mathcal{L}[w,l,\sigma]` can be computed with the function below.


.. code-block::

   def self_supervised_decurtaining_loss(x,destriped):
       """
       Self-supervised loss used for the parameter search.

       :param x: (ndarray) input slice;
       :param destriped: (ndarray) destriped slice;
       :return: (float) loss value for the given parameters.
       """
       stripes = x-destriped
       R = np.mean(np.abs(np.gradient(stripes,axis=0)))
       Q = np.mean(np.abs(np.gradient(stripes,axis=1)-np.gradient(x,axis=1)))
       return 2*R+Q


The research of the best parameter combination can done by using a simple grid search. The loss value for all the
possible combinations of parameters in the parameter space generated, can be computed with the code below.


.. code-block::

    # optimization routine
    L = []
    for p in pspace:

        # initialize filter with a set of parameters
        filter = lambda x: destripe_slice(x,*p)

        # apply filter
        dest_sl = filter(sl)

        # compute loss
        L_p = self_supervised_decurtaining_loss(sl,dest_sl)
        L.append(L_p)


Clearly, the best parameters are the one corresponding to the lowest value of the loss.


.. code-block::

    # print results
    best_idx = np.argmin(L)
    print('Best parameters: ', pspace[best_idx])
    print('Loss value: ', L[best_idx])


The optimization routine described here, contains all the essential steps which are present in the :py:class:`Destriper
<bmiptools.transformation.restoration.destriper.Destriper>` class.


Results
=======


Consider the image below as input for the algorithm. The striping artifacts are clearly visible.


.. image:: ../_images/Miscellaneous/destriper_optimization/original.png
   :class: align-center
   :width: 700px
   :height: 700px
   :scale: 42


The loss value for all the 5300 combinations is showed in the graph below.


.. image:: ../_images/Miscellaneous/destriper_optimization/loss_value.png
   :class: align-center
   :width: 1923px
   :height: 1015px
   :scale: 40


Being not completely clear how the loss function look like, it can be useful to zoom around the global minimum of the
loss, as showed in the graph below.


.. image:: ../_images/Miscellaneous/destriper_optimization/loss_value_zoom.png
   :class: align-center
   :width: 1923px
   :height: 1015px
   :scale: 40


The best parameter combination corresponds to the loss value :math:`\mathcal{L}[w,\sigma,l] = 0.025176`, which gives
the visual result below


.. |fig-1| image:: ../_images/Miscellaneous/destriper_optimization/original.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig0| image:: ../_images/Miscellaneous/destriper_optimization/global.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig-1| |fig0|


Clearly, different values of the loss correspond to different level of destriping. The animation below show how the
filter quality changes in different points of the loss, confirming empirically that the loss function used is able
to capture the idea of image without vertical stripes.


.. image:: ../_images/Miscellaneous/destriper_optimization/animation.gif
   :class: align-center
   :width: 706px
   :height: 841px
   :scale: 80


To give a closer look at the different visual results, the different images showed above compared with the one
obtained with the best parameter combination are available below.


**Global minimum vs Local minimum**

On the right, one can see the result produced with the parameter combination corresponding to a local minimum of
the loss (:math:`\mathcal{L}[w,\sigma,l] = 0.025200`)


.. |fig1| image:: ../_images/Miscellaneous/destriper_optimization/global.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig2| image:: ../_images/Miscellaneous/destriper_optimization/local_minimum.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig1| |fig2|


There is not much difference between the one corresponding to the global and local minimum.


**Global minimum vs Local maximum**

On the right, one can see the result produced with the parameter combination corresponding to a local maximum of
the loss (:math:`\mathcal{L}[w,\sigma,l] = 0.029996`)


.. |fig3| image:: ../_images/Miscellaneous/destriper_optimization/global.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig4| image:: ../_images/Miscellaneous/destriper_optimization/local_maximum.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig3| |fig4|


Being completely far away from the global minimum, the stripes are still visible, as expected.


**Global minimum vs Away from minimum**

On the right, one can see the result produced with the parameter combination corresponding to a value in between a
local maximum and the global minimum of the loss (:math:`\mathcal{L}[w,\sigma,l] = 0.026342`).


.. |fig5| image:: ../_images/Miscellaneous/destriper_optimization/global.png
   :class: align-left
   :width: 700px
   :height: 700px
   :scale: 42


.. |fig6| image:: ../_images/Miscellaneous/destriper_optimization/away_global.png
   :class: align-right
   :width: 700px
   :height: 700px
   :scale: 42


|fig5| |fig6|


Note that the image on the right, appear too blurred and with diagonal details which seem amplified. This is a clear
sign that the filtering of the vertical component of the wavelet decomposition is too much.


.. note::

   The script used to produce the images displayed can be found `here <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools
   /-/tree/master/examples/documentation_scripts/Miscellaneous/destriper_optimization>`_. To reproduce the images showed
   above one may consult the `examples/documentation_scritps folder <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/
   tree/master/examples/documentation_scripts>`_, where is explained how to run the example scripts and where one can
   find all the necessary input data.