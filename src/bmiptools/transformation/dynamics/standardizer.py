# Title: 'standardizer.py'
# Date: 21/05/2021
# Author: Curcuraci L.
#
# Scope: Class performing the standardization of a stack.

"""
Plugin performing the standardization of a stack.
"""

#################
#####   LIBRARIES
#################


import numpy as np

import bmiptools.core.ip_utils as iput
import bmiptools.core.utils as ut
from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI


#############
#####   CLASS
#############


class Standardizer(TransformationBasic):
    """
    Class used to standardize a stack.
    """

    __version__ = '0.1'
    empty_transformation_dictionary = {'standardization_type': '0/1',
                                       'standardization_mode': 'stack'}
    _guipi_dictionary = {'standardization_type': GuiPI(options=['mean/std','-1/1','0/1']),
                         'standardization_mode': GuiPI(options=['slice-by-slice','stack'])}
    def __init__(self,transformation_dictionary):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'standardization_type': (str) standardization methods used by the class. Currently implemented methods are:

                * '-1/1': all the values in the image are suitably rescaled between -1 and 1.
                * '0/1': all the values of the image are suitably rescaled between 0 and 1.
                * 'mean/std': the image will have zero mean and standard deviation 1.

            'standardization_mode': (str) determine how the standardization parameters are computed. Two are the
            possible modes:

                * 'slice-by-slice': the standardization parameters are computed independently for each slices.
                * 'stack': the standardization parameters are computed for the whole stack (i.e considering the stack as
                  a whole).

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        """
        super(Standardizer,self).__init__()

        self.standardization_type = transformation_dictionary['standardization_type']
        self.standardization_mode = transformation_dictionary['standardization_mode']
        self._supported_standardization_type = ['-1/1','0/1','mean/std']
        self._supported_standardization_mode = ['slice-by-slice','stack']

        self._setup()

    def _setup(self):

        assert self.standardization_type in self._supported_standardization_type, '{} is not recognized as ' \
               'standardization type. Supported standardizations types are {}'.format(
               self.standardization_type,ut.list_to_string(self._supported_standardization_type))

        assert self.standardization_mode in self._supported_standardization_mode, '{} is not recognized as ' \
               'standardization mode. Supported standardizations modes are {}'.format(
               self.standardization_mode,ut.list_to_string(self._supported_standardization_mode))

        if self.standardization_mode == 'slice-by-slice':

            self._mode = 'yx'

        if self.standardization_mode == 'stack':

            self._mode = 'z'


    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        if x.n_channels > 1:

            standardized_x = []
            for C in range(x.n_channels):

                standardized_x.append( iput.standardizer(x.data[...,C],
                                                         type=self.standardization_type,
                                                         mode=self._mode) )

            if not inplace:

                return np.array(standardized_x).transpose((1,2,3,0))

            x.temporary_library_metadata.update({'Standardizer':{'standardization_type': self.standardization_type,
                                                                 'standardization_mode': self.standardization_mode,
                                                                 'pre_standardization_statistics': x.statistics()}})
            x.from_array( np.array(standardized_x).transpose((1,2,3,0)) )

        else:

            if not inplace:

                return iput.standardizer(x.data,
                                         type=self.standardization_type,
                                         mode=self._mode)

            x.temporary_library_metadata.update({'Standardizer':{'standardization_type': self.standardization_type,
                                                                 'standardization_mode': self.standardization_mode,
                                                                 'pre_standardization_statistics': x.statistics()}})
            x.from_array( iput.standardizer(x,type=self.standardization_type) )