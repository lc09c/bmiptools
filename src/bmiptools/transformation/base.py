# Title: 'base.py'
# Author: Curcuraci L.
# Date: 16/02/2021
#
# Scope: Define the prototype class for a generic transformation.


"""
Base class for all the transfomation plugins.

All the transformations of 'bmiptools' need to have at least the structure described here. In particular:

    - all the parameters of the transformation have to be declared in the class initialization: no parameter have to
      be passed to any class method in other way;

    - all the setup operations preparing the transformation for the correct execution, have to be specified in the
      '_setup' method, which should be called during the class initialization;

    - all the transformations need to have a 'transform' method which apply the transformation, with the parameters
      specified/computed during the class initialization, to the input of this method;

    - optimization procedures, which may be used to compute the optimal parameters of the transformation, have to be
      specified in the 'fit' method of the class. If fit class is used, one should avoid to overwrite the initialization
      but, in order to already have the fit_enable variable (True, as default).

    - a custom 'save' method need to be implemented in case the plugins uses non dill-compatible objects. In this case
      a dictionary called 'undillable_path_attributes'...[TO FIX THIS POINT...AT THE MOMENT IS SIMPLY THE PATH].

As general rules, all the additional method of a transformation class should be protected (i.e. the name should start
with '_'). These rules ensures that the transformation can be executed, saved and loaded correctly by the Pipeline
class.
"""


#################
#####   LIBRARIES
#################


from copy import copy
import bmiptools.core.utils as ut
from bmiptools.core.base import CoreBasic


###############
#####   CLASSES
###############


class TransformationBasic(CoreBasic):

    empty_transformation_dictionary = {}
    _guipi_dictionary = {}
    # _undillable_attribute_path = ....
    #
    # P.A. : A global attribute of the class, named '_undillable_attribute_path' need to be created specifying the name
    #        of the class attribute used to specify the loading link. See DenoiseDNN for an example.
    #
    def __init__(self,*args,**kwargs):
        """
        Initialize here all the parameters of the transformation and execute all the setup operations.
        """
        super(TransformationBasic,self).__init__()
        self.fit_enable = True
        pass

    def _setup(self,*args,**kwargs):
        """
        Execute all the setup operations of the transformation. All the operations which have to be executed before
        to apply the transformation and does not depend on the Stack object on which they are applied, should be placed
        here.
        """
        return None

    def fit(self,x,*args,**kwargs):
        """
        Fit the transformation to the stack on which is applied.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        """
        return None

    def transform(self,x,inplace=True,*args,**kwargs):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        return None

    def inverse_transform(self,x,inplace=True,*args,**kwargs):
        """
        Apply the inverse transformation (if possible) on the stack

        :param x: (bmiptools.stack.Stack) stack object on which the inverse transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        return None

    def save(self,*args,**kwargs):
        """
        Save the plugin state (or all the necessary information to recover a functional plugin state). This method need
        to be implemented ONLY if the plugin contain some "non-pickable"/"non-dillable" object. In this case the default
        saving methods of the saving class will not be able to save the plugin state. A simple way to check the
        "pickability/dillability" of an object, the code below can be used to check if the object f is dillable:

        >>> import dill
        >>> dill.pickles(f)

        It is recommended to make this test with a plugin that has already been initialized, (eventually) fitted and
        applied to some stack, so that all the attributes of the plugin has been initialized.

        P.A. : In case of undillable plugin, a global attribute of the plugin class, named 'undillable_path_attributes'
        need to be created specifying the name of the class attribute used to specify the loading link of the undillable
        objects.
        See DenoiseDNN for an example.

        """
        return None

    def get_transformation_dictionary(self,*args,**kwargs):
        """
        Return the transformation dictionary of the plugin filled with the current values of the variables of the
        plugin class at the time at which this method is called. The transformation dictionary of the plugin has the
        same organization of the 'empty_transformation_dictionary', a (global) attribute of the plugin class.
        """
        if hasattr(self.__class__, 'empty_transformation_dictionary'):

            if not self.__class__.empty_transformation_dictionary is None:

                transformation_dictionary = copy(self.__class__.empty_transformation_dictionary)
                key_branches_list = ut.get_branch_of_key_tree(transformation_dictionary)
                for element in key_branches_list:

                    if element[-1] in self.__dict__.keys():

                        ut.set_by_path(transformation_dictionary, element, eval('self.{}'.format(element[-1])))

                return transformation_dictionary

            return None

        else:

            return None