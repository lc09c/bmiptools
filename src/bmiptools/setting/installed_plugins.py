# Title: 'installed_plugins.py'
# Date: 02/03/2021
# Author: Curcuraci L.
#
# Scope: List the available plugins for the pipeline creation.

"""
List of the available installed plugins organized in two dictionaries:

* ``PLUGINS``, where the default bmiptools plugin *plus* the user installed plugins can be found;

* ``LOCAL_PLUGINS``, where the plugins installed by the user are listed.

"""

#################
#####   LIBRARIES
#################


import os
import sys
import bmiptools


################################
#####   STANDARD PLUGINS IMPORTS
################################


from bmiptools.transformation.geometric.affine import *
from bmiptools.transformation.geometric.cropper import *

from bmiptools.transformation.alignment.registrator import *

from bmiptools.transformation.restoration.flatter import *
from bmiptools.transformation.restoration.destriper import *
from bmiptools.transformation.restoration.denoiser import *
from bmiptools.transformation.restoration.decharger import *

from bmiptools.transformation.dynamics.standardizer import *
from bmiptools.transformation.dynamics.histogram_matcher import *
from bmiptools.transformation.dynamics.equalizer import *


#################
#####   FUNCTIONS
#################


def _add_locally_installed_plugin():
    """
    By checking the content of the file 'local_plugin.txt' saved in './setting/file', the plugins installed by the user
    locally are added to the dictionary of the standard plugins and to the local plugin dictionary too.
    """
    if os.path.exists(bmiptools.__bmiptools_files_folder_path__+os.sep+'local_plugins.txt'):

        with open(bmiptools.__bmiptools_files_folder_path__+os.sep+'local_plugins.txt','r') as plgn_file:

            for line in plgn_file:

                try:

                    plugin_name,plugin_absolute_path = line.split(',')
                    sys.path.append( os.path.abspath(plugin_absolute_path) )
                    file_name = plugin_absolute_path.split(os.sep)[-1].replace('.py','')
                    exec('from {} import {}'.format(file_name,plugin_name))
                    PLUGINS.update({plugin_name: eval(plugin_name)})
                    LOCAL_PLUGINS.update({plugin_name: eval(plugin_name)})

                except:

                    Warning('Local plugins may be not available: the \'local_plugins.txt\' file or the local '
                            'plugin files specified there.')


########################
#####   GLOBAL VARIABLES
########################


# standard installed plugins
PLUGINS = {
    'Standardizer': Standardizer,
    'HistogramMatcher': HistogramMatcher,
    'Registrator': Registrator,
    'Flatter': Flatter,
    'Destriper': Destriper,
    'Denoiser': Denoiser,
    'DenoiserDNN': DenoiserDNN,
    'Affine': Affine,
    'Decharger': Decharger,
    'Cropper': Cropper,
    'Equalizer': Equalizer
    }

# local installed plugins
LOCAL_PLUGINS = {}

# add locally installed plugin if any
_add_locally_installed_plugin()