"""
General plugin information. Remember to update this file once the plugin is modified.
"""


import bmiptools


__version__ = 'v0.1'

__name__ = 'alignment'

__author__ = 'Curcuraci Luca'

__affiliation__ = 'MPIKG - Potsdam'

__scope__ = 'Apply intra-stack alignment transformations on a stack.'

__desc__ = '* recorder [DEPRECATED] -> apply registration algorithms to a stack (currently implemented : \'ECC\').\n' \
           '* registrator.rst -> apply registration algorithms to a stack. Parameter estimation and application of the ' \
                            'transformation can be done in different times. For usefull pre-registration ' \
                            'transformation use \'bmiptools.transfomation.restoration.standardizer.Standardizer\' ' \
                            'and \'bmiptools.transfomation.restoration.histogram_matcher.HistogramMatcher\'.'

__manual__ = ''

__source__ = ''



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