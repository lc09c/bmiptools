# Title: '_registration_shared.py'
# Author: Curcuraci L.
# Date: 07/12/21
#
# Scope: Collect core function shared among the restoration plugins.

"""
Collection of core functions/ variables shared among the restoration plugins.
"""

#################
#####   LIBRARIES
#################


import itertools
import pywt
import re


##############
#####   GLOBAL
##############


SUPPORTED_WAVELET = pywt.wavelist(kind='discrete')
SUPPORTED_WAVELET_FAMILIES = list(set(map(lambda x:re.sub('[0-9]','',x).replace('.',''),SUPPORTED_WAVELET)))


###############
##### FUNCTIONS
###############


def generate_parameter_space(params_dict):
    """
    Generate parameter space from a parameter dictionary.

    :param params_dict: (dict) dictionary containing the parameter name as dictionary key and a list of possible
                        parameter's value as dictionary value.
    :return: (list,list) list of parameter combinations (one for each point of the parameter space), list containing
             the parameter dictionary
    """
    parameter_space = params_dict[list(params_dict)[0]]
    if len(params_dict) > 1:

        for n, key in enumerate(list(params_dict)[1:]):

            parameter_space = itertools.product(parameter_space, params_dict[key])
            parameter_space = [list(it) for it in parameter_space]
            if n > 0:

                parameter_space = [it[0] + [it[1]] for it in parameter_space]

    return list(parameter_space),list(params_dict)
