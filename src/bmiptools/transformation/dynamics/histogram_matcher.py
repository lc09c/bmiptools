# Title: 'histogram_matcher.py'
# Date: 21/05/2021
# Author: Curcuraci L.
#
# Scope: Class performing the histogram matching of a stack.
#
# Observation: Note that this transformation is intrinsically serial, since the histogram matched slice N can be computed
#              if and only if the histogram matched slice N-1.

"""
Plugin performing the histogram matching of a stack.
"""

#################
#####   LIBRARIES
#################


import numpy as np
from skimage.exposure import match_histograms

from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI


#############
#####   CLASS
#############


class HistogramMatcher(TransformationBasic):
    """
    Class used to match  the histograms of different slices in a stack.
    """

    __version__ = '0.3'
    empty_transformation_dictionary = {'reference_slice': 0 }
    _guipi_dictionary = {'reference_slice': GuiPI(int,min=np.iinfo(np.int16).min,max = np.iinfo(np.int16).max)}
    def __init__(self,transfomation_dictionary):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'reference_slice': (int) number indicating the slice used as starting reference during the histogram
            matching.

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        """
        super(HistogramMatcher,self).__init__()
        self.reference_slice = transfomation_dictionary['reference_slice']

    def _match_histogram(self,x):
        """
        Given a collection of images, it matches the histogram of an image with the histogram of the previous. The first
        image is left unchanged.

        :param x: (nparray) array containing the collection of images. zyx convention is assumed for the interpretation
                  of the array and, the image is contained in the yx-slice.
        :return: the collection of images with matched histograms.
        """
        hm_x = [ x[self.reference_slice,...] ]
        for i in range(1,self.reference_slice):

            hm_x.append(match_histograms(x[self.reference_slice-i,...],hm_x[i-1]))
            self.progress_bar(len(hm_x)-1,len(x),15,'{}/{}'.format(len(hm_x)-1,len(x)))

        hm_x = list(reversed(hm_x))
        self.progress_bar(len(hm_x),len(x),15,'{}/{}'.format(len(hm_x),len(x)))
        for i in range(self.reference_slice+1,len(x)):

            hm_x.append( match_histograms(x[i,...],hm_x[i-1]) )
            self.progress_bar(len(hm_x),len(x),15,'{}/{}'.format(len(hm_x),len(x)))

        return np.array(hm_x)

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

                hm_x.append( self._match_histogram(x.data[..., C]) )

            if not inplace:

                return np.array(hm_x).transpose((1,2,3,0))

            x.from_array(np.array(hm_x).transpose((1,2,3,0)))

        else:

            if not inplace:

                return self._match_histogram(x.data)

            x.from_array( self._match_histogram(x.data) )