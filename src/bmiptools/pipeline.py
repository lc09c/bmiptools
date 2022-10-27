# Title: 'pipeline.py'
# Author: Curcuraci L.
# Date: 03/03/2021
#
# Scope: Define the Pipeline class, which is the class that manage the creation/initialization/application on a stack of
# pipeline of plugins (i.e. transformation tools). This is done in a way that all the operations executed on a stack can
# be tracked, saved, and reloaded (in exactly the same state) in later time.
#
# Updates:
#
# - 26/05/21: * the plugin in the pipeline can now be fitted not necessarily directly before the plugin application;
#             * the pipeline dictionary is now saved directly in the dill file.
#
# - 06/01/22: * fixed a bug in '_read_operations_list' method: now the enumeration is correct in both the outputs when
#               when a fit method is applied 2 or more steps before the corresponding application point AND other
#               plugins are applied after the application point.

"""
A pipeline object manage the creation/initialization/application on a stack of sequence of transformation tools (i.e.
plugins). This is done in a way that all the operations executed on a stack can be tracked, saved, and when reloaded in
a later time, they reproduce exactly the same result.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import warnings
import json
import os
import datetime
import dill
import glob
import copy
import imageio

import bmiptools
import bmiptools.core.utils as ut
from bmiptools.setting.installed_plugins import PLUGINS    # Import the installed plugins
from bmiptools.core.base import CoreBasic
from bmiptools.stack import Stack


###############
#####   CLASSES
###############


class Pipeline(CoreBasic):
    """
    Class used to track, save and load all the transformations applied to a given stack.
    """

    __version__ = '0.3'
    def __init__(self,operations_list=None,pipeline_folder_path=None,pipeline_name=None,gui_mode=False):
        """
        Setting all the inputs of the initialization equal to None, allow to create an empty Pipeline class, which can
        be used to load an already existing pipeline.

        :param operations_list: (list or None) list of string containing the operations to be done the pipeline that
                                will be created. To apply a plugin, simply write the name. To fit a plugin write 'fit_'
                                before the plugin name. The name have to be specified according to the name given to the
                                plugins specified in 'setting/installed_plugins.py'. The plugin fit must always precede
                                the plugin application. If None an empty pipeline is created. An example of operation list 
                                can be the following:

                                                ['PluginA','fit_PluginB','PluginC','PluginB']

                                This operation list corresponds to: 'PluginA' is (eventually) fitted and then applied, 
                                then 'PluginB' is fitted (but not applied), then 'PluginC' is fitted and applied, and 
                                finally 'PluginB' is applied. If a plugin is listed two or more times in the list, two
                                or more independent plugins of the same type will be (eventually) fitted and applied.
                                

        :param pipeline_folder_path: (str or None) name of the folder in which all the pipeline folder will be created.
                                     The pipeline folder is where all the files describing the pipeline are stored. If
                                     None, the pipeline folder will be created in the current working directory of the
                                     python project.
        :param pipeline_name: (str or None) Name of the pipeline. If None a default name specifying the creation time
                              is used.
        :param gui_mode: (bool) if True changes the verbosity behaviour of the pipeline class in order to be compatible
                         with the bmiptools gui.
        """
        super(Pipeline,self).__init__()

        self.save_preview = False
        self.gui_mode = gui_mode
        if operations_list is not None:

            self.plugins_list,self.true_operations_list = self._read_operations_list(operations_list)
            self.pipeline_name = pipeline_name
            if pipeline_name is None:

                self.pipeline_name = 'pipeline__' + datetime.datetime.now().strftime('%d%m%Y_%H%M')

            self.pipeline_folder_path = pipeline_folder_path
            if pipeline_folder_path is None:

                self.pipeline_folder_path = ''

            self.create()

    @staticmethod
    def _read_operations_list(ops_list):
        """
        From the pipeline operations list, create the list of plugins that need to be initialized, a list
        of operations to be done with this plugin (basically this list tells you when to fit the plugins).

        :param ops_list: operations list to read.
        :return: a plugin list and an operation list.
        """
        plugs_to_apply = []
        plugs_to_fit = []
        plugins_to_fit_earlier = []
        dn = 0
        for n, plug in enumerate(ops_list):

            plug = plug + '_{}'.format(n - dn)
            plugs_to_apply.append(plug)
            plugs_to_fit.append(plug)
            if 'fit_' in plug:

                plugs_to_apply = plugs_to_apply[:-1]
                plugs_to_fit = plugs_to_fit[:-1]
                plug_to_fit_earlier = plug[4:]
                plugs_to_fit.append(plug_to_fit_earlier)
                plugins_to_fit_earlier.append([n - dn, plug_to_fit_earlier.split('_')[0]])

            for n_to_fit, plug_to_fit in plugins_to_fit_earlier:

                if plug_to_fit == plug.split('_')[0] and not 'fit_' in plug:

                    dn = dn + 1
                    plugs_to_apply[-1] = plugs_to_apply[-1].split('_')[0] + '_{}'.format(n_to_fit)
                    plugs_to_fit = plugs_to_fit[:-1]
                    idx = plugins_to_fit_earlier.index([n_to_fit, plug_to_fit])
                    del plugins_to_fit_earlier[idx]
                    break

        for plug_to_fit_earlier in plugins_to_fit_earlier:

            num, name = plug_to_fit_earlier
            idx_to_del = plugs_to_fit.index(name + '_{}'.format(num))
            del plugs_to_fit[idx_to_del]
            print('\nApparently plugin \'{}\' should be fitted but not applied later in the pipeline. To '
                  'optimize the pipeline fitting process, this fit has been skipped.'.format(name))

        true_operation_list = []
        waiting_list = []
        waiting_list_number = []
        dn = 0
        for n, op in enumerate(ops_list):

            if not 'fit_' in op:

                if not op in waiting_list:

                    true_operation_list.append('fit_' + op + '_{}'.format(n-dn))
                    true_operation_list.append(op + '_{}'.format(n-dn))

                else:

                    idx_to_del = waiting_list.index(op)
                    true_operation_list.append(op + '_{}'.format(waiting_list_number[idx_to_del]))
                    del waiting_list_number[idx_to_del]
                    del waiting_list[idx_to_del]
                    dn = dn+1

            else:

                true_operation_list.append(op + '_{}'.format(n-dn))
                waiting_list.append(op[4:])
                waiting_list_number.append(n-dn)

        return plugs_to_apply, true_operation_list

    def create(self):
        """
        Create a pipeline given an operation list. This method will create a folder at the path specified by the
        'pipeline_folder_path' and a json file in that folder. The json file created contains all the information
        needed to specify a pipeline (written in a human readable manner) and represent a way in which the user can
        interact with the 'bmiptools' at API level.
        """
        self.pipeline_folder_path = ut.manage_path(self.pipeline_folder_path+os.sep+self.pipeline_name)
        self.pipeline_plugins = []
        valid_operations = []
        invalid_operations = []
        empty_operations_dict = {}
        for plugin in self.plugins_list:

            plugin_name,_ = plugin.split('_')
            try:

                self.pipeline_plugins.append(PLUGINS[plugin_name])
                valid_operations.append(plugin)
                empty_operations_dict.update({plugin:PLUGINS[plugin_name].empty_transformation_dictionary})


            except:

                invalid_operations.append(plugin)
                warnings.warn('\nPlugin \'{}\' skipped in the pipeline creation because currently not available. To use '
                              'it, install the plugin in \'bmiptools/installed_plugins.py\' and create the desired '
                              'pipeline again.'.format(plugin_name))

        self.plugins_list = valid_operations
        for invalid_name in invalid_operations:

            idx_to_del1 = self.true_operations_list.index(invalid_name)
            idx_to_del2 = self.true_operations_list.index('fit_'+invalid_name)
            del self.true_operations_list[idx_to_del1]
            del self.true_operations_list[idx_to_del2]

        empty_pipeline_dict = {'pipeline_name': self.pipeline_name,
                               'pipeline_creation_date': datetime.datetime.now().strftime('%d/%m/%Y at %H:%M'),
                               'bmiptools_version': bmiptools.__version__,
                               'plugins_list': self.plugins_list,
                               'true_operations_list': self.true_operations_list,
                               'pipeline_setting': empty_operations_dict}
        self.pipeline_json_path = self.pipeline_folder_path+os.sep+'pipeline__{}.json'.format(self.pipeline_name)
        with open(self.pipeline_json_path, 'w') as jfile:

            dumped = json.dumps(empty_pipeline_dict, cls=ut.NumpyEncoder)
            dumped = json.loads(dumped)
            json.dump(dumped, jfile, indent=4)

        if not self.gui_mode:

            print('Pipeline dictionary created at {}.\n\nSpecify the plugin parameters there, save the json file, '
                  'and then initialize the pipeline by calling \nthe \'initialize\' method of the Pipeline '
                  'class.'.format(self.pipeline_json_path))

    def load_pipeline_template_from_json(self,pipeline_template_path, new_pipeline_folder_path):
        """
        Load a pipeline template.

        :param pipeline_template_path: (raw str) path to the pipeline template.
        :param new_pipeline_folder_path: (raw str) path to the new pipeline folder.
        """

        with open(pipeline_template_path, 'r') as jfile:

            content = json.load(jfile)

        self.pipeline_folder_path = ut.manage_path(new_pipeline_folder_path)
        self.pipeline_name = content['pipeline_name']
        self.plugins_list = content['plugins_list']
        self.true_operations_list = content['true_operations_list']
        self.pipeline_plugins = []
        for plg_name in self.plugins_list:

            self.pipeline_plugins.append(PLUGINS[plg_name.split('_')[0]])

        content['pipeline_creation_date'] = datetime.datetime.now().strftime('%d/%m/%Y at %H:%M')
        content['bmiptools_version'] = bmiptools.__version__
        self.pipeline_json_path = self.pipeline_folder_path+os.sep+'pipeline__{}.json'.format(self.pipeline_name)
        with open(self.pipeline_json_path, 'w') as jfile:

            dumped = json.dumps(content, cls=ut.NumpyEncoder)
            dumped = json.loads(dumped)
            json.dump(dumped, jfile, indent=4)

    def initialize(self):
        """
        Initialize the all the plugins in the pipeline with the parameters specified in the 'pipeline__***.json' file
        created during the class initialization.
        """
        if not self.gui_mode:

            input('Press enter when all the parameters has been specified in the pipeline dictionary.')

        with open(self.pipeline_json_path, 'r') as jfile:

            self.pipeline_dict = json.load(jfile)

        self.pipeline = {}
        for n, plugin_name in enumerate(self.pipeline_dict['plugins_list']):

            plugin_n_transformation_dict = self.pipeline_dict['pipeline_setting'][plugin_name]
            if 'Registrator' in plugin_name:

                if plugin_n_transformation_dict['OF_setting']['save_mod_OF']:

                    plugin_n_transformation_dict['OF_setting']['mod_OF_saving_path'] = \
                        ut.manage_path(self.pipeline_folder_path+os.sep+'mod_OF_registrator')

            self.pipeline.update({plugin_name: self.pipeline_plugins[n](plugin_n_transformation_dict)})

        self.write('Pipeline initialized according to specifications in {}.'.format(self.pipeline_json_path))

    def setup_preview(self,slice_list=None,plugin_to_exclude=['Standardizer','Registator']):
        """
        Save preview images of the plugin application for each step of the pipeline, except the excluded plugin.

        :param slice_list: (list of int) list with the slices from which the preview is applied.
        :param plugin_to_exclude: (list of str) list of plugins to exclude from the preview. The name of the plugin
                                  have to be chosen according to PLUGIN dictionary (i.e. the current name of the
                                  installed plugins).
        """
        if not slice_list is None:

            self.save_preview = True
            self._preview_slice_list = slice_list
            self._preview_plugin_to_exclude = plugin_to_exclude
            self._preview_saving_folder = ut.manage_path(self.pipeline_folder_path+os.sep+'preview')

        else:

            self.save_preview = False

    def _preview_save(self,stack,step_name):

        plugin_preview_folder = ut.manage_path(self._preview_saving_folder + os.sep + step_name)
        for slice in self._preview_slice_list:

            preview_slice_path = plugin_preview_folder + os.sep + 'slice_{}'.format(slice) + '.tiff'
            img = stack[slice,...]
            img = (256*(img-np.min(img))/(np.max(img)-np.min(img))).astype(np.uint8)
            imageio.imsave(uri=preview_slice_path, im=img)

    def apply(self,stack,fit_enable_list=None):
        """
        Apply the pipeline to a given stack. The stack is transformed inplace.

        :param stack: (Stack) stack to transform.
        :param fit_enable_list: (list of boolean) list of boolean variables of the same length of the plugin
                                list specified during the initialization of the class. Each boolean variable will set the
                                'fit_enable' attribute of each plugin, controlling if a plugin is fitted or not during
                                pipeline application to a stack. If None the pipeline is fitted according to the current
                                'fit_enable' variables of the plugins.
        """
        if self.save_preview:

            self._preview_save(stack,'original')

        for n,operation_name in enumerate(self.true_operations_list):

            if 'fit_' in operation_name:

                self.write('{}/{} | fitting {}\n'.format(n+1,len(self.true_operations_list),operation_name[4:]),end='\r')
                plugin = self.pipeline[operation_name[4:]]
                if fit_enable_list is not None:

                    plugin.fit_enable = fit_enable_list[n]

                if hasattr(plugin,'auto_optimize') and plugin.auto_optimize:

                    plugin.fit(stack)
                    plugin.fit_enable = False

                # update the pipeline dictionary with the parameters found during fit
                self.pipeline_dict['pipeline_setting'][operation_name[4:]] = plugin.get_transformation_dictionary()

            else:

                self.write('{}/{} | applying {}\n'.format(n+1,len(self.true_operations_list),operation_name),end='\r')
                plugin = self.pipeline[operation_name]
                plugin.transform(stack)
                if self.save_preview:

                    if operation_name.split('_')[0] not in self._preview_plugin_to_exclude:

                        self._preview_save(stack,'post__'+operation_name)

        stack.add_metadata('image_processing_metadata',{'tool': 'bmiptools _{}'.format(bmiptools.__version__),
                                                        'info': self.pipeline_dict})

    def _make_pipeline_dillable(self,pipeline):
        """
        Check if the plugins in the pipeline can be serialized via dill. If this is not the case the
        'save' methods of the the plugin is called, and a new plugin of the same type is reinitialized with
        the transformation_dictionary of the initial plugin (after saving).

        :param pipeline:
        :return:
        """
        checked_pipeline = {}
        for plugin in pipeline:

            if dill.pickles(pipeline[plugin]):

                checked_pipeline.update({plugin: pipeline[plugin]})

            else:

                if hasattr(pipeline[plugin],'save'):

                    pipeline[plugin].save(path = self.pipeline_folder_path+os.sep+'undillable'+os.sep+plugin)
                    transformation_dictionary = pipeline[plugin].get_transformation_dictionary()

                else:

                    transformation_dictionary = pipeline[plugin].get_transformation_dictionary()

                checked_pipeline.update({plugin: [PLUGINS[plugin.split('_')[0]],transformation_dictionary]})

        return checked_pipeline

    def save(self):
        """
        Save the pipeline in the pipeline folder specified in the 'pipeline_folder_path' of this class.
        """
        pipeline_object_path = self.pipeline_folder_path+os.sep+'pipeline__{}.dill'.format(self.pipeline_name)
        dillable_pipeline = self._make_pipeline_dillable(self.pipeline)
        to_save = {'bmiptools_version': bmiptools.__version__,
                   'pipeline': dillable_pipeline,
                   'true_operations_list': self.true_operations_list,
                   'pipeline_dict': self.pipeline_dict}

        with open(pipeline_object_path, 'wb') as dfile:

            dill.dump(to_save, dfile)

        with open(self.pipeline_json_path,'w') as jfile:

            dumped = json.dumps(self.pipeline_dict, cls=ut.NumpyEncoder)
            dumped = json.loads(dumped)
            json.dump(dumped, jfile, indent=4)

        self.write('Pipeline saved at {}!'.format(pipeline_object_path))

    def _unpack_pipeline(self,pipeline,path_to_undillable_folder=None):
        """

        :param pipeline:
        :param path_to_undillable_folder:
        :return:
        """
        unpacked_pipeline = {}
        for plugin in pipeline:

            if type(pipeline[plugin]) == list:

                plg_obj,plg_dict = pipeline[plugin]
                if path_to_undillable_folder is not None:

                    new_path = os.path.normpath(glob.glob(path_to_undillable_folder+os.sep+plugin+os.sep+'*')[0])
                    plg_dict = ut.set_in_a_nested_dict(adict = plg_dict,
                                                       key = plg_obj._undillable_path_attributes,
                                                       value = new_path)

                unpacked_pipeline.update({plugin: plg_obj(plg_dict)})

            else:

                unpacked_pipeline.update({plugin: pipeline[plugin]})

        return unpacked_pipeline

    def load(self,pipeline_object_path,undillable_folder_path = None):
        """
        Load an already existing pipeline.

        :param pipeline_object_path: (str) path to the pipeline object.
        :param undillable_folder_path: (str) path to the 'undillable' folder, if any.
        """
        with open(pipeline_object_path, 'rb') as dfile:

            loaded = dill.load(dfile)

        self.pipeline = self._unpack_pipeline(loaded['pipeline'],undillable_folder_path)
        self.true_operations_list = [el for el in loaded['true_operations_list'] if el.find('fit_') < 0]
        self.pipeline_dict = loaded['pipeline_dict']
        if not loaded['bmiptools_version'] == bmiptools.__version__:

            warnings.warn('Pipeline generated with \'bmiptools\' {}, while you are using \'bmiptools\' {}. '
                          'Possible compatibility issues due to the version mismatch can be found in the '
                          '\'bmiptools\' manual '.format(loaded['version'],bmiptools.__version__))

        self.plugins_list = self.pipeline_dict['plugins_list']
        self.pipeline_name = self.pipeline_dict['pipeline_name']
        self.pipeline_folder_path = os.path.normpath(os.path.dirname(pipeline_object_path))