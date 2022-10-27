"""
General plugin information. Remember to update this file once the plugin is modified.
"""


import bmiptools


__version__ = 'v0.1'

__name__ = 'restoration'

__author__ = 'Curcuraci Luca'

__affiliation__ = 'MPIKG - Potsdam'

__scope__ = 'Apply restoration methods on a stack.'

__desc__ = '* flatter -> remove low (spatial) frequency variations in an image.\n' \
           '* destriper -> remove vertical stripes artifacts in an image.\n' \
           '* decharger -> remove charging artifacts in an image.\n' \
           '* denoiser -> remove noise in an image.\n' \
           '* standardizer -> standardize the stack\n' \
           '* historgam_matcher -> match the histogram among consecutive slices in as tack.'

__manual__ = ''


__source__ = '* destriper :\n' \
             '- articles\n' \
             '\thttps://doi.org/10.1364/OE.17.008567\n' \
             '* denoiser :\n' \
             '- articles\n' \
             '\thttps://arxiv.org/abs/1811.10980\n' \
             '\thttps://arxiv.org/abs/1901.11365'



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