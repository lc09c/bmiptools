# Title: 'equalizer.py'
# Date: 07/03/2022
# Author: Curcuraci L.
#
# Scope: Class performing the equalization of the slices of a stack.

"""
Plugin performing the equalization of the slices of a stack.
"""

#################
#####   LIBRARIES
#################


import numpy as np
from skimage.exposure import equalize_adapthist
from joblib import Parallel,delayed

from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI


#############
#####   CLASS
#############


class Equalizer(TransformationBasic):
    """
    Class for the CLAHE algorithm in bmiptools. Essentially a wrapper around the skimage implementation of CLAHE
    (i.e. skimage.exposure.equalize_adapthist).
    """

    __version__ = '0.1'
    empty_transformation_dictionary = {'kernel_size': None,
                                       'clip_limit': 0.01,
                                       'nbins': 256}
    _guipi_dictionary = {'kernel_size': GuiPI('math'),
                         'clip_limit': GuiPI(float,min=0,max=1),
                         'nbins': GuiPI(int,min=1)}
    def __init__(self,transfomation_dictionary,force_serial = False):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'kernel_size': (tuple or None) shape of the contextual region.

            'clip_limit': (float between 0 ans 1) clipping limit.

            'nbins': (int) number of bins used to construct the histogram for the equalization.

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        """

        super(Equalizer,self).__init__()
        self.force_serial = force_serial

        self.kernel_size = transfomation_dictionary['kernel_size']
        self.clip_limit = transfomation_dictionary['clip_limit']
        self.nbins = transfomation_dictionary['nbins']

    def _equalize(self,x):
        """
        Given a stack, equalize each slice using CLAHE.

        :param x: (nparray) array containing the collection of images. zyx convention is assumed for the interpretation
                  of the array and, the image is contained in the yx-slice.
        :return: the collection of equalized images.
        """
        if self._use_multiprocessing and self._use_multiprocessing_type == 'parallelize_plugin' \
                and not self.force_serial:

            def func_to_par(x):

                return equalize_adapthist(x,self.kernel_size,self.clip_limit,self.nbins)

            eq_x = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(x[i,...])
                                                          for i in self.vtqdm(range(len(x))))

        else:

            eq_x = []
            for i in range(len(x)):

                eq_x.append(equalize_adapthist(x[i,...],self.kernel_size,self.clip_limit,self.nbins))
                self.progress_bar(i,len(x),15,'{}/{}'.format(i+1,len(x)))

        return np.array(eq_x)

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if x.n_channels > 1:

            hm_x = []
            for C in range(x.n_channels):

                hm_x.append( self._equalize(x.data[..., C]) )

            if not inplace:

                return np.array(hm_x).transpose((1,2,3,0))

            x.from_array(np.array(hm_x).transpose((1,2,3,0)))

        else:

            if not inplace:

                return self._equalize(x.data)

            x.from_array( self._equalize(x.data) )