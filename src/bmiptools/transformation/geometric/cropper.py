# Title: 'cropper.py'
# Date: 07/03/2022
# Author: Curcuraci L.
#
# Scope: Class performing the cropping of a stack.

"""
Plugin performing the cropping of a stack.
"""

#################
#####   LIBRARIES
#################


import numpy as np

from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI


#############
#####   CLASS
#############


class Cropper(TransformationBasic):
    """
    Class used to crop a stack.
    """

    __version__ = '0.1'
    empty_transformation_dictionary = {'z_range': [None,None],
                                       'y_range': [None,None],
                                       'x_range': [None,None]}
    _guipi_dictionary = {'z_range': GuiPI('math'),
                         'y_range': GuiPI('math'),
                         'x_range': GuiPI('math')}
    def __init__(self,transfomation_dictionary):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'z_range': (list of two int) list specifying the extrema along the Z-direction (i.e. axis 0). This list
            can contain numpy-like instruction for the definition of the range.

            'y_range': (list of two int) list specifying the extrema along the Y-direction (i.e. axis 1). This list can
            contain numpy-like instruction for the definition of the range.

            'x_range': (list of two int) list specifying the extrema along the X-direction (i.e. axis 2). This list can
            contain numpy-like instruction for the definition of the range.

            }

        By numpy-like instruction the following is meant. Given a numpy array Arr with shape (100,100,100), then

            {'z_range': [20,50], 'y_range': [-30,None], 'x_range': [None,20]}

        implies the following

            Arr[20:50,-30:,:20]

        which as shape (30,30,80).

        :param transformation_dictionary: dictionary containing all the transformation options.
        """
        super(Cropper,self).__init__()
        self.z_range = transfomation_dictionary['z_range']
        self.y_range = transfomation_dictionary['y_range']
        self.x_range = transfomation_dictionary['x_range']

    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if x.n_channels > 1:

            cropped_x = []
            for C in range(x.n_channels):

                cropped_x.append( x.data[self.z_range[0]:self.z_range[1],
                                         self.y_range[0]:self.y_range[1],
                                         self.x_range[0]:self.x_range[1],C] )

            if not inplace:

                return np.array(cropped_x).transpose((1,2,3,0))

            x.from_array( np.array(cropped_x).transpose((1,2,3,0)) )

        else:

            if not inplace:

                return x.data[self.z_range[0]:self.z_range[1],
                              self.y_range[0]:self.y_range[1],
                              self.x_range[0]:self.x_range[1]]

            x.from_array(x.data[self.z_range[0]:self.z_range[1],
                                self.y_range[0]:self.y_range[1],
                                self.x_range[0]:self.x_range[1]])