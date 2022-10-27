"""
General plugin information. Remember to update this file once the plugin is modified.
"""


import bmiptools


__version__ = 'v0.0'

__name__ = 'geometric'

__author__ = 'Curcuraci Luca'

__affiliation__ = 'MPIKG - Potsdam'

__scope__ = 'Apply geometric transformations on a stack.'

__desc__ = '* affine -> apply affine transformation to a stack (e.g. translations, rotations, scaling, ecc..).'

__manual__ = ''

__source__ = '* https://scipy.github.io/devdocs/tutorial/ndimage.html \n' \
             '* https://docs.scipy.org/doc/scipy/reference/ndimage.html'



def info():

    print(bmiptools.__name__,' - ',bmiptools.__version__)
    print('\nPlugin developed by ', __author__, ' @ ', __affiliation__)
    print('Plugin name: ', __name__)
    print('Plugin version: ', __version__)
    print('Plugin scope: ',__scope__)
    print('Plugin description: ')
    print(__desc__)
    print('Further info:')
    if len(__manual__)>0:

        print(__manual__)

    if len(__source__)>0:

        print(__source__)

    else:

        print('Not available.')