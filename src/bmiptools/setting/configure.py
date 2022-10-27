#
#
#
#
#

"""
Collect functions for the bmiptools configuration.
"""

#################
#####   LIBRARIES
#################


import os
import bmiptools
import bmiptools.core.utils as ut


##############################
#####   GLOBAL SETTING METHODS
##############################


def set_verbosity(verbosity_level,path=bmiptools.__global_setting_path__):
    """
    Set verbosity level in 'global_setting.txt'.

    :param verbosity_level: (int) 0 for no messages printed or 1 printing allowed.
    :param path: path to the 'global_setting.txt' file.
    """
    ut.set_option_in_global_setting('verbosity',verbosity_level,path=path)

def set_cpu_buffer(n_cpu_buffer, path=bmiptools.__global_setting_path__):
    """
    Set number of cpu buffer 'global_setting.txt'.

    :param n_cpu_buffer: (int) number of cpu that are not used during multiprocessing.
    :param path: path to the 'global_setting.txt' file.
    """
    ut.set_option_in_global_setting('cpu_buffer',n_cpu_buffer, path=path)

def set_use_multiprocessing(multiprocessing, path=bmiptools.__global_setting_path__):
    """
    Set multiprocessing flag in 'global_setting.txt'.

    :param multiprocessing: (int) 0 to not use multiprocessing, 1 to use multiprocessing.
    :param path: path to the 'global_setting.txt' file.
    """
    ut.set_option_in_global_setting('use_multiprocessing',multiprocessing, path=path)

def set_multiprocessing_type(multiprocessing_type, path=bmiptools.__global_setting_path__):
    """
    Set multiprocessing type in 'global_setting.txt'.

    :param multiprocessing_type: (int) set it 0 to use multiprocessing for pipeline parallelization, set it 1 to use
                                  multiprocessing for internal parallelization in the plugin.
    :param path: path to the 'global_setting.txt' file.
    """
    ut.set_option_in_global_setting('multiprocessing_type',multiprocessing_type, path=path)

def set_use_gpu(gpu, path=bmiptools.__global_setting_path__):
    """
    Set multiprocessing flag in 'global_setting.txt'.

    :param gpu: (int) 0 to not use gpu parallelization, 1 to use gpu parallelization.
    :param path: path to the 'global_setting.txt' file.
    """
    ut.set_option_in_global_setting('use_gpu',gpu, path=path)


#################################
#####   LOCAL PLUGIN INSTALLATION
#################################


def install_plugin(plugin_absolute_path,plugin_name):
    """
    Install locally a plugin, i.e. add a user made plugin to the list of the available plugin of bmiptools.

    :param plugin_absolute_path: (raw str) path to the python script containing the plugin class.
    :param plugin_name: (str) plugin class name. This is also plugin name.
    """

    if plugin_absolute_path.endswith('.py'):

        with open(bmiptools.__bmiptools_files_folder_path__+os.sep+'local_plugins.txt','a') as plgn_file:

            tmp = plugin_name+','+plugin_absolute_path
            plgn_file.write(tmp)

        print('Plugin \'{}\' installed!'.format(plugin_name))

    else:

        AssertionError('Wrong file extension in \'plugin_absolute_path\': the specified file has to be a '
                       'python script.')

def uninstall_plugin(plugin_name):
    """
    Uninstall a local plugin. Only local plugin can be uninstalled.

    :param plugin_name: (str) name of the local plugin to uninstall.
    """

    if os.path.exists(bmiptools.__bmiptools_files_folder_path__ + os.sep + 'local_plugins.txt'):

        tmp = []
        plugin_found = False
        with open(bmiptools.__bmiptools_files_folder_path__ + os.sep + 'local_plugins.txt', 'r') as plgn_file:

            for line in plgn_file:

                if not (plugin_name in line):

                    tmp.append(line)

                else:

                    plugin_found = True

        if plugin_found:

            with open(bmiptools.__bmiptools_files_folder_path__ + os.sep + 'local_plugins.txt', 'w') as plgn_file:

                for line in tmp:

                    plgn_file.write(line)

            print('Plugin \'{}\' installed!'.format(plugin_name))

        else:

            Warning('Plugin \'{}\' not found in the local installed plugin.'.format(plugin_name))