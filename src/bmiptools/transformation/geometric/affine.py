# Title: 'affine.py'
# Author: Curcuraci L.
# Date: 17/02/2021
#
# Scope: Class used to apply affine transformations on a stack object.
#
# Source:
#
# - transformation matrices in projective geometry: https://www.tutorialspoint.com/computer_graphics/3d_transformation.html
# - rotation matrix along an axis: https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle

"""
Plugin used to apply affine transformations on a stack object.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import scipy.ndimage as spnd

from bmiptools.core import math_utils as mut
from bmiptools.transformation.base import TransformationBasic
from bmiptools.gui.gui_basic import GuiPI


###############
#####   CLASSES
###############

# TODO fast_rotation for rotation of 90' with respect the cartesian axis.
# TODO deal with the multi-channel case (assume channel-last)

class Affine(TransformationBasic):
    """
    Class used to geometric apply an affine transformation (translation, rotation, scaling,...) to the stack.
    """
    empty_transformation_dictionary = {'apply': 'translation',
                                       'reference_frame_origin': 'center-yx',
                                       'translation': {'translation_vector': [0,0,0]
                                                       },
                                       'rotation': {'rotation_angle': 0,
                                                    'rotation_axis': [0,0,1]
                                                    },
                                       'scaling': {'scaling_factors': 1
                                                   },
                                       'shear': {'shear_factors': [0,0,0]
                                                 },
                                       'custom': {'affine_transformation_matrix': None
                                                  }
                                       }
    _guipi_dictionary = {'apply': GuiPI('options',options=['translation','rotation','scaling','shear','custom']),
                         'reference_frame_origin': GuiPI('options',
                                                         options=['center','center-zy','center-zx','center-yx']),
                         'translation': {'translation_vector': GuiPI('math')},
                         'rotation': {'rotation_angle': GuiPI(float),
                                      'rotation_axis': GuiPI('math')},
                         'scaling': {'scaling_factors': GuiPI(float)},
                         'shear': {'shear_factors': GuiPI('math')},
                         'custom': {'affine_transformation_matrix': GuiPI('math')}
                         }
    def __init__(self,transformation_dictionary):
        """
        The setting of this class happens via dictionary (a transformation dictionary). Below the field that this
        dictionary need to have and their content is explained.

            {'apply': (str) Name of the type of transformation to apply. The parameters of these transformation have to
            be specified in the other fields of this dictionary (see below). Possible options are:

                * 'translation': translation in 3D space;
                * 'rotation': rotation in 3D space (specified using the angle-axis notation);
                * 'scaling': scaling transformation in 3D space;
                * 'shear': shear transformation in 3D space;
                * 'custom': custom affine transformation, which as to be specified as 4x4 matrix representing the
                  transformation in a projective 3D space.

            'reference_frame_origin': (str of tuple/list/numpy array) This field specify the origin of the reference
            frame. A point in a 3D space can be directly specified with an array/list/tuple (the default origin is in
            the (0,0,0) - i.e. the top-left corner - entry of the array containing the stack), otherwise one can use
            one of the four options below, by specifying its name. The possible options are:

                * 'center': the origin of the reference frame is placed in the exact center of the stack;
                * 'center-zy': the origin of the reference frame is placed in the exact center of the yz-plane and
                  with x=0;
                * 'center-zx': the origin of the reference frame is placed in the exact center of the xz-plane and
                  with y=0;
                * 'center-yx': the origin of the reference frame is placed in the exact center of the yx-plane and
                  with z=0;

            'translation': (dict) Dictionary containing the parameters of the translation transformation. This field has
            to be specified only if 'translation' is chosen in the 'apply' field of this dictionary. The dictionary has
            to be specified as below:

                {'translation_vector': (tuple/list/numpy array) translation vector in a 3D space.

                }

            'rotation': Dictionary containing the parameters of the rotation transformation. This field has to be
            specified only if 'rotation' is chosen in the 'apply' field of this dictionary. The dictionary has to be
            specified as below:

                {'rotation_angle':(float) rotation angle expressed in grad.

                'rotation_axis':(list/numpy array) vector representing the rotation axis around which the rotation
                takes place.

                }

            'scaling': (dict) Dictionary containing the parameters of the scaling transformation. This field has to be
            specified only if 'scaling' is chosen in the 'apply' field of this dictionary. The dictionary has to be
            specified as below:

                {'scaling_factors': <- (float/list/numpy array) scaling factor of the transformation. If a single number
                is given, it is assumed the same scaling transformation for each axis.

                }

            'shear': (dict) Dictionary containing the parameters of the shear transformation. This field has to be
            specified only if 'shear' is chosen in the 'apply' field of this dictionary. The dictionary has to be
            specified as below:

                {'shear_factors': (list/numpy array) containing the three parameters of a sher transformation in 3D
                ordered as (h_x,h_y,h_z).

                }

            'custom': (dict) Dictionary containing the parameters of a custom affine transformation. This field has to
            be specified only if 'custom' is chosen in the 'apply' field of this dictionary. The dictionary has to be
            specified as below:

                {'affine_transformation_matrix': (numpy array) 4x4 matrix representing a generic affine transformation.
                In principle any linear and invertible transformation can be used.

                }

            }

        :param transformation_dictionary: dictionary containing all the transformation options.
        """
        self.transformation_dictionary = transformation_dictionary
        self.reference_frame_origin = transformation_dictionary['reference_frame_origin']
        if transformation_dictionary['apply'] == 'translation':

            self.translation_vector = transformation_dictionary['translation']['translation_vector']
            self._setup('translation')

        elif transformation_dictionary['apply'] == 'rotation':

            self.rotation_angle = transformation_dictionary['rotation']['rotation_angle']
            self.rotation_axis = transformation_dictionary['rotation']['rotation_axis']
            self._setup('rotation')

        elif transformation_dictionary['apply'] == 'scaling':

            self.scaling_factors = transformation_dictionary['scaling']['scaling_factors']
            self._setup('scaling')

        elif transformation_dictionary['apply'] == 'shear':

            self.shear_factors = transformation_dictionary['shear']['shear_factors']
            self._setup('shear')

        elif transformation_dictionary['apply'] == 'custom':

            self._setup('custom')

        else:

            raise NotImplementedError('Chosen transformation currently not implemented.'
                                      '\n Available transformations: \'translation\',\'rotation\',\'scaling\','
                                      '\'shear\',\'custom\'.')

    def _setup(self,setup_type):

        # compute the origin translation if possible
        if self.reference_frame_origin not in ['center','center-zy','center-zx','center-yx'] \
            and len(self.reference_frame_origin) != 3:

            raise AssertionError('Unrecognized \'reference_frame_origin\'. \'reference_frame_origin\' can be chosen '
                                 'among one of the default options \'center\',\'center-zy\',\'center-zx\','
                                 '\'center-yx\', or be a point in a 3D space (expressed with tuple,list or '
                                 'numpy array). ')

        if self.reference_frame_origin not in ['center','center-zy','center-zx','center-yx']:

            self.To = self._translation_matrix(-self.reference_frame_origin)
            self.To_inv = self._translation_matrix(self.reference_frame_origin)

        # transformation specific setup
        if setup_type == 'translation':

            self._translation_setup()

        if setup_type == 'rotation':

            self._rotation_setup()

        if setup_type == 'scaling':

            self._scaling_setup()

        if setup_type == 'shear':

            self._shear_setup()

        if setup_type == 'custom':

            self._custom_setup()

    # translation
    def _translation_setup(self):
        """
        Compute the (inverse) transformation matrix representing a translation in a projective 3D space.
        """
        self.translation_vector = np.array(self.translation_vector)
        self.inv_affine_transformation_matrix = self._translation_matrix(-self.translation_vector)

    @staticmethod
    def _translation_matrix(v):
        """
        Matrix representation of a translation by a vector v=(v1,v2,v3) in a projective 3D space.

        :param v: (numpy array) 3D translation vector.
        :return: (numpy array) 4x4 matrix representing a translation by v in a projective 3D space.
        """
        t_v = np.eye(4)
        t_v[:-1, -1] = v
        return t_v

    # rotation
    def _rotation_setup(self):
        """
        Compute the (inverse) transformation matrix representing a rotation in a projective 3D space.
        """
        self.inv_affine_transformation_matrix = self._rotation_matrix(-self.rotation_angle,self.rotation_axis)

    @staticmethod
    def _rotation_matrix(theta, u):
        """
        Matrix representation of a rotation of an angle theta around a axis having the direction of the vector u in
        projective 3D space.

        P.A.: Rotation matrix around an axis in ordinary euclidean space [https://en.wikipedia.org/wiki/Rotation_matrix]

        :param theta: (float) rotation angle in degree.
        :param u: (numpy array) 3D rotation axis.
        :return: (numpy array) 4x4 matrix representing a rotation in projective 3D space.
        """
        u = u / np.linalg.norm(u)
        theta = theta / 180 * np.pi
        r = np.eye(4)
        r[0, 0] = np.cos(theta) + (u[0] ** 2) * (1 - np.cos(theta))
        r[1, 0] = u[0] * u[1] * (1 - np.cos(theta)) + u[2] * np.sin(theta)
        r[2, 0] = u[2] * u[0] * (1 - np.cos(theta)) - u[1] * np.sin(theta)
        r[0, 1] = u[0] * u[1] * (1 - np.cos(theta)) - u[2] * np.sin(theta)
        r[1, 1] = np.cos(theta) + (u[1] ** 2) * (1 - np.cos(theta))
        r[2, 1] = u[2] * u[1] * (1 - np.cos(theta)) + u[0] * np.sin(theta)
        r[0, 2] = u[0] * u[2] * (1 - np.cos(theta)) + u[1] * np.sin(theta)
        r[1, 2] = u[1] * u[2] * (1 - np.cos(theta)) - u[0] * np.sin(theta)
        r[2, 2] = np.cos(theta) + (u[2] ** 2) * (1 - np.cos(theta))
        return r

    # scaling
    def _scaling_setup(self):
        """
        Compute the (inverse) transformation matrix representing a scaling in a projective 3D space.
        """
        if type(self.scaling_factors) is list:

            s = list(map(lambda x:1/x,self.scaling_factors))

        elif type(self.scaling_factors) is np.ndarray:

            s = 1/self.scaling_factors

        else:

            s = 3 * [1/self.scaling_factors]

        self.inv_affine_transformation_matrix = self._scale_matrix(s)

    @staticmethod
    def _scale_matrix(s):
        """
        Matrix associated to a generic scale transformation in a projective 3D space.

        :param s: (float or list of 3 elements) scaling factor - global or one for each dimension.
        :return: (numpy array) 4x4 matrix representing scaling in a projective 3D space.
        """
        S = np.eye(4)
        np.fill_diagonal(S, s)
        S[3, 3] = 1.
        return S

    # shear
    def _shear_setup(self):
        """
        Compute the (inverse) transformation matrix representing a shear transformation in a projective 3D space.
        """
        direct_transformation = self._shear_matrix(self.shear_factors)
        try:

            self.inv_affine_transformation_matrix = np.linalg.inv(direct_transformation)

        except:

            raise ValueError('The inversion of shear transformation matrix was not possible. Try a shear transformation '
                             'with slightly different parameters.')

    @staticmethod
    def _shear_matrix(h):
        """
        Matrix associated to a shear transformation in an projective 3D space (Galilean boost).

        :param h: (list numpy array) shear parameter for the x,y and z axis.
        :return: (numpy array) 4x4 matrix representing a shear transformation in a projective 3D space.
        """
        H = np.eye(4)
        H[1, 0] = H[2, 1] = h[0]
        H[0, 1] = H[1, 2] = h[1]
        H[0, 1] = H[1, 0] = h[2]
        return H

    # custom affine transformation
    def _custom_setup(self):
        """
        Compute the inverse of the custom transformation matrix.
        """
        direct_transformation = self.transformation_dictionary['custom']['affine_transformation_matrix']
        try:

            self.inv_affine_transformation_matrix = np.linalg.inv(direct_transformation)

        except:

            raise ValueError('Singular or ill conditioned custom transformation matrix.')

    # general methods
    def _compute_origin_translation(self,volume_shape):
        """
        Compute the translation matrix (in a projective 3D space) linking the chosen position of the origin with respect
        to the (0,0,0) point of stack according to the following convention:

            - 'center': the reference frame respect to which the transformation take place is centred in the middle of
                        the stack;

            - 'center-zy': the reference frame respect to which the transformation take place is centred in the center
                           of the zy-plane and on the first x-slice (i.e. x_origin = 0);

            - 'center-zx': the reference frame respect to which the transformation take place is centred in the center
                           of the zx-plane and on the first x-slice (i.e. y_origin = 0);

            - 'center-yx': the reference frame respect to which the transformation take place is centred in the center
                           of the yx-plane and on the first z-slice (i.e. z_origin = 0);


        :param volume_shape: tuple containing the shape of the volume to transform (in the xyz-convention), from which
                             the origin will be computed.
        """
        if self.reference_frame_origin == 'center':

            t0 = np.array(volume_shape)/2

        elif self.reference_frame_origin == 'center-zy':

            t0 = np.array([0,volume_shape[1],volume_shape[2]])/2

        elif self.reference_frame_origin == 'center-zx':

            t0 = np.array([volume_shape[0],0,volume_shape[2]])/2

        else:

            t0 = np.array([volume_shape[0],volume_shape[1],0])/2

        self.To = self._translation_matrix(-t0)
        self.To_inv = self._translation_matrix(t0)

    def _infer_final_shape(self,volume,transformation_matrix):
        """
        Infer the shape of the volume after the application of the affine transformation.

        :param volume: (numpy array) initial volume(/stack) to transform.
        :param transformation_matrix: (numpy array) 4x4 matrix representing the transformation in a projective 3D space.
        :return: the shape of the transformed volume.
        """
        # get the vertex coordinates of the initial volume
        x_max = volume.shape[0]
        y_max = volume.shape[1]
        z_max = volume.shape[2]
        volume_vertex = np.array([[0, 0, 0, 1], [0, 0, z_max, 1], [0, y_max, 0, 1], [x_max, 0, 0, 1],
                                  [0, y_max, z_max, 1], [x_max, y_max, 0, 1], [x_max, 0, z_max, 1],
                                  [x_max, y_max, z_max, 1]])                                    # in projective space!

        # compute the new vertex position after the transformation
        transformed_volume_vertex = np.dot(transformation_matrix, volume_vertex.T).T.astype(int)

        # infer the post-transformation volume shape from the position of the transformed vertex
        maxs, mins = mut.max_and_min(transformed_volume_vertex, axis=0)
        transformed_x_max, transformed_y_max, transformed_z_max, _ = maxs
        transformed_x_min, transformed_y_min, transformed_z_min, _ = mins
        new_shape = (transformed_x_max-transformed_x_min,
                     transformed_y_max-transformed_y_min,
                     transformed_z_max-transformed_z_min)
        return new_shape

    # apply transformation
    def transform(self,x,inplace=True):
        """
        Apply the initialized transformation.

        :param x: (bmiptools.stack.Stack) stack object on which the transformation is applied.
        :param inplace: (bool) if True the result of the transformation substitute the content of the input Stack. When
                        False, the transformation result is returned in the for of numpy array and the content of the
                        input Stack is left unchanged.
        """
        # get data from the stack
        volume = x.data

        # put the stack in the xyz-basis
        volume = volume.transpose(2,1,0)    # TODO: How to deal with grayscale image with images with 3 channels?

        # compute the final shape
        try:

            dir_affine_transformation_matrix = np.linalg.inv(self.inv_affine_transformation_matrix)

        except:

            raise ValueError('Singular or ill conditioned transformation matrix (in 3D projective space).')

        inferred_final_shape = self._infer_final_shape(volume,dir_affine_transformation_matrix)
        final_shape = tuple(np.max([list(volume.shape),list(inferred_final_shape)],axis=0))            # The final shape can only increase

        # initialize the volume_to_transform
        if inferred_final_shape == volume.shape:

            to_transform = volume

        else:

            to_transform = np.zeros(final_shape)
            delta_x, delta_y, delta_z = np.abs(np.array(final_shape) - np.array(volume.shape)) // 2
            to_transform[delta_x:delta_x + volume.shape[0],
                         delta_y:delta_y + volume.shape[1],
                         delta_z:delta_z + volume.shape[2]] = volume
            volume = None                           # free RAM (together with the next instruction)

        x.data = None                               # free RAM and empty the stack

        # compute the full transformation matrix
        if not hasattr(self,'To'):

            self._compute_origin_translation(final_shape)

        M = np.dot(self.To_inv,np.dot(self.inv_affine_transformation_matrix,self.To))

        # get the mesh of coordinates to transform
        Xs, Ys, Zs = np.meshgrid(np.arange(final_shape[0]),
                                 np.arange(final_shape[1]),
                                 np.arange(final_shape[2]), indexing='ij')

        Xs, Ys, Zs = Xs.reshape(-1), Ys.reshape(-1), Zs.reshape(-1)
        hom_coords = np.vstack((Xs, Ys, Zs, np.ones(len(Xs))))

        # compute the transformed coordinates (with respect to the coordinates of the input)
        transformed_hom_coords = np.dot(M, hom_coords)
        transformed_coords = transformed_hom_coords[:3, :]

        # compute the transformed volume
        transformed_volume = spnd.map_coordinates(to_transform, transformed_coords)
        transformed_volume = np.reshape(transformed_volume, final_shape)

        if not inplace:

            return transformed_volume.transpose(2,1,0)

        x.from_array( transformed_volume.transpose(2,1,0) )