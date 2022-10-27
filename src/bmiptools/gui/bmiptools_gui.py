# Title: 'bmiptools_gui.py'
# Date: 20/12/21
# Author: Curcuraci L.
#
# Scope: Collect the main objects used for gui creation in bmiptools.

"""
Main objectus used to render the bmiptools gui
"""

#################
#####   LIBRARIES
#################


import os
import json
import pathlib
from benedict import benedict
from datetime import datetime

import magicgui
from magicgui.widgets import Container,PushButton,Label,MainWindow,ComboBox,FileEdit,LineEdit,CheckBox,\
    LiteralEvalLineEdit

import bmiptools
import bmiptools.core.utils as ut
from bmiptools.gui.gui_basic import GuizeObject,GuizeObjectFromDict
from bmiptools.stack import Stack
from bmiptools.pipeline import Pipeline,PLUGINS


###############
#####   CLASSES
###############


class PipelineBuilder:
    """
    Graphical interface for the construction of a bmiptools pipeline.
    """
    
    def __init__(self,plugin_options_list):
        """
        Create the graphical interface for the construction of a bmiptools pipeline.

        :param plugin_options_list: (dict) dictionary containing all the plugins (with their corresponding python
                                    object) and eventually the corresponding 'fit_***' fields (associated to a None
                                    value in the dictionary).
        """
        self.pipeline_dictionary = {}
        self.plugin_options_list = plugin_options_list

        self._plugin_widgets = {}

        self._build_gui()
        self._connect_gui_functions()

    def __call__(self,run=True):

        self.gui.show(run)

    def _build_gui(self):

        self.filefield = FileEdit(name='Select a pipeline folder',mode='d')
        plugin_widget = self._add_plugin_widget()
        self.b_add = PushButton(text='add')
        self.b_ok = PushButton(text='ok')
        wdg_list = [self.filefield,plugin_widget,self.b_add,self.b_ok]
        self.gui = Container(widgets=wdg_list)

    def _connect_gui_functions(self):

        # self.b_ok.clicked.connect(self._onclick_b_ok)
        # self.cb_selector.changed.connect(self._update_cb_selector,position='last')
        # self.b_setting.clicked.connect(self._onclick_b_setting,position='last')
        self.b_add.clicked.connect(self._onclick_b_add)

    # def _onclick_b_ok(self,event):
    #
    #     # print(self.filefield.value)
    #     self.gui.close()

    def _add_plugin_widget(self):

        plugin_name = 'sel_{}'.format(datetime.now().strftime('%y%m%d%H%M%S'))
        selector = ComboBox(value=list(self.plugin_options_list.keys())[0],
                            choices=self.plugin_options_list.keys())
        setting = PushButton(text='setting')
        plugin_widget = Container(widgets=[selector,setting],
                                  layout='horizontal',
                                  label=' ',
                                  name=plugin_name)

        self._current_widget = plugin_name
        self.cb_selector = selector
        self.b_setting = setting
        self._update_cb_selector(0)
        self._plugin_widgets.update({plugin_name: plugin_widget})

        # connect with the function updating the selected plugin name
        plugin_widget.changed.connect(self._onchange_plugin_widget)

        return plugin_widget

    def _onchange_plugin_widget(self,event):

        self._current_widget = event.value.name
        self.cb_selector,self.b_setting = event.value
        self.cb_selector.changed.connect(self._update_cb_selector,position='last')
        self.b_setting.clicked.connect(self._onclick_b_setting, position='last')

    def _update_cb_selector(self,event):

        Plugin = self.plugin_options_list[self.cb_selector.value]
        if Plugin != None:

            # if not self._current_widget in self.pipeline_dictionary.keys():
            self.pipeline_dictionary.update({self._current_widget: [self.cb_selector.value,
                                                                            Plugin.empty_transformation_dictionary]})

        else:

            self.pipeline_dictionary.update({self._current_widget: [self.cb_selector.value, None]})

    def _onclick_b_setting(self,event):

        Plugin = self.plugin_options_list[self.cb_selector.value]
        if Plugin != None and Plugin.empty_transformation_dictionary != None:

            self._plugin_gui = GuizeObjectFromDict(Plugin)
            self._plugin_gui()

            # temporary connections
            self._plugin_gui.pbutton.clicked.connect(self._onclick_plugin_gui_pbutton)

        else:

            self.pipeline_dictionary.update({self._current_widget: [self.cb_selector.value, None]})

    def _onclick_plugin_gui_pbutton(self,event):

        self._plugin_gui.gui.close()
        flat_dict = \
            benedict(self.plugin_options_list[self.cb_selector.value].empty_transformation_dictionary).flatten('__')
        guipi_info = list(benedict(self.plugin_options_list[self.cb_selector.value]._guipi_dictionary).flatten('__').values())
        plugin_readers = [guipi.widget()[2] for guipi in guipi_info if guipi.visible]
        for n, true_plugin_pos in enumerate(self._plugin_gui.true_plugin_pos_list):

            val = plugin_readers[n](self._plugin_gui.gui[true_plugin_pos])
            pname = self._plugin_gui.gui[true_plugin_pos].name.replace(' ', '_')
            for key in flat_dict:

                if pname == key.split('__')[-1]:

                    flat_dict[key] =  val

        _tmp_td = {k: v for k,v in flat_dict.unflatten('__').items()}
        self.pipeline_dictionary.update({self._current_widget: [self.cb_selector.value,_tmp_td]})

    def _onclick_b_add(self,event):

        self.gui.close()
        new_plugin_widget = self._add_plugin_widget()
        self.gui.insert(-3,new_plugin_widget)
        self.gui.show(run=True)

class PipelineLoad:
    """
    Graphical interface for the loading of an already existing pipeline.
    """
    
    def __init__(self):

        self.path_to_pipeline_folder = None

        self._build_gui()
        self._connect_gui_functions()

    def __call__(self,run = True):

        self.gui.show(run)

    def _build_gui(self):

        self.path_field = FileEdit(mode='r', name='Pipeline .dill file path',filter='*.dill')
        self.b_ok = PushButton(text='ok')
        self.gui = Container(widgets=[self.path_field,self.b_ok])

    def _connect_gui_functions(self):

        self.b_ok.clicked.connect(self._onclick_b_ok)

    def _onclick_b_ok(self,event):

        self.gui.close()

class PipelineTemplateLoad:
    """
    Graphical interface for the loading of a pipeline template.
    """
    def __init__(self):

        self.path_to_pipeline_folder = None

        self._build_gui()
        self._connect_gui_functions()

    def __call__(self,run = True):

        self.gui.show(run)

    def _build_gui(self):

        self.template_path_field = FileEdit(mode='r', name='Pipeline template json file path',filter='*.json')
        self.pipeline_folder_path_field = FileEdit(mode='d', name='Pipeline folder path')
        self.b_ok = PushButton(text='ok')
        self.gui = Container(widgets=[self.template_path_field,self.pipeline_folder_path_field,self.b_ok])

    def _connect_gui_functions(self):

        self.b_ok.clicked.connect(self._onclick_b_ok)

    def _onclick_b_ok(self,event):

        self.gui.close()

class PreviewSetting:
    """
    Graphical interface for the preview settings.
    """
    
    def __init__(self):

        self.path_to_pipeline_folder = None

        self._build_gui()
        self._connect_gui_functions()

    def __call__(self,run = True):

        self.gui.show(run)

    def _build_gui(self):

        self.checkbox_wdg = CheckBox(name='Save preview ',value=False)
        self.slice_preview_wdg = LineEdit(name='Slice(s) for preview:',
                                          value='0')
        self.plugin_to_exclude_wdg = LiteralEvalLineEdit(name = 'Plugins to exclude from preview:',
                                                         value = ['Standardizer','Registrator'])
        self.b_ok = PushButton(text='ok')
        self.gui = Container(widgets=[self.checkbox_wdg,self.slice_preview_wdg,self.plugin_to_exclude_wdg,self.b_ok])

    def _connect_gui_functions(self):

        self.b_ok.clicked.connect(self._onclick_b_ok)

    def _onclick_b_ok(self,event):

        self.gui.close()

    @staticmethod
    def _read_preview_slice(ipt):
        """
        Get a list out of the input of the 'slice_preview_wdg' widget.

        :param ipt: (str) slice_preview_wdg value
        :return: (list of int) list of slices to be used for the preview.
        """
        preview_slice = []
        for ir in ipt.split(','):

            ir = ir.replace(' ','')
            try:

                if '-' in ir:

                    ir_min,ir_max = ir.split('-')
                    sl = list(range(int(ir_min),int(ir_max)+1))

                else:

                    sl = [int(ir)]

            except:

                continue

            preview_slice += sl

        return preview_slice

class StackSave:
    """
    Graphical interface for the stack saving.
    """
    
    def __init__(self):#,stack_to_save):

        # self.stack_to_save = stack_to_save
        # self.saving_setting = {}

        self._build_gui()
        # self._connect_gui_functions()

    def __call__(self,run=True):

        self.gui.show(run)

    def _build_gui(self):

        saving_path = FileEdit(value='',name='saving path',mode='d')
        saving_name = LineEdit(value='',name='saving name')
        mode = ComboBox(value='slice_by_slice',choices=['slice_by_slice','all_stack'],name='mode')
        data_type = ComboBox(value='uint8', choices=['uint8','float32'],name='data type')
        extension = LineEdit(value='tiff',name='extension')
        standard_saving = CheckBox(value=True,name='standard saving')
        save_metadata = CheckBox(value=True,name='save metadata')
        self.b_ok = PushButton(name='Ok')
        self.gui = Container(widgets=[saving_path,saving_name,mode,data_type,extension,standard_saving,
                                      save_metadata,self.b_ok])

    # def _connect_gui_functions(self):
    #
    #     self.b_ok.clicked.connect(self._onclick_b_ok)
    #
    # def _onclick_b_ok(self,event):
    #
    #     self.gui.close()
    #     for i in range(len(self.gui)-1):
    #
    #         self.saving_setting.update({self.gui[i].name.replace(' ','_'):self.gui[i].value})

class BMIPToolsGUI:
    """
    Main bmiptools GUI.
    """
    def __init__(self):

        self.shared_memory = {}

        self.stack_gui = GuizeObject(Stack)
        self.create_and_init_pipeline_gui = PipelineBuilder(self._add_fit_to_plugin_list(PLUGINS))
        self.pipeline_load_gui = PipelineLoad()
        self.pipeline_template_load_gui = PipelineTemplateLoad()
        self.preview_setting_gui = PreviewSetting()
        self.stack_save_gui = None

        self._build_gui()
        self._connect_gui_functions()

    def __call__(self,run=True):

        return self.main_window.show(run)

    @staticmethod
    def _add_fit_to_plugin_list(plugin_dict):

        plugin_dict_with_fit = {}
        for k, v in plugin_dict.items():

            plugin_dict_with_fit.update({k: v})
            plugin_dict_with_fit.update({'fit_' + k: None})

        return plugin_dict_with_fit

    @staticmethod
    def _create_and_initialize_pipeline(operations_list,pipeline_folder_path,pipeline_setting):

        pipeline = Pipeline(operations_list=operations_list,
                            pipeline_folder_path=pipeline_folder_path,
                            gui_mode=True)
        with open(pipeline.pipeline_json_path, 'r') as jfile:

            pipeline_dict = json.load(jfile)

        pipeline_dict['pipeline_setting'] = pipeline_setting
        with open(pipeline.pipeline_json_path, 'w') as jfile:


            dumped = json.dumps(pipeline_dict, cls=ut.NumpyEncoder)
            dumped = json.loads(dumped)
            json.dump(dumped, jfile, indent=4)

        pipeline.initialize()
        return pipeline

    def _build_gui(self):

        self.title = Label(value=' bmip tool {} graphical user interface\n'.format(bmiptools.__version__))

        # basic buttons
        self.b_load_stack = PushButton(label='Load stack')
        self.b_create_and_init_pipeline = PushButton(label='Create and initialize pipeline')
        self.b_load_pipeline_template = PushButton(label='Load pipeline template')
        self.b_load_pipeline = PushButton(label='Load existing pipeline')

        self.b_preview_setting = PushButton(label='Preview setting')

        self.b_apply_pipeline = PushButton(label='Apply pipeline')
        self.b_open_setting_pipeline = PushButton(label='Open pipeline setting json')
        self.b_save_result = PushButton(label='Save result')
        self.b_save_pipeline = PushButton(label='Save pipeline')
        self.b_close = PushButton(label='Close')

        # group buttons
        pipeline_setting_buttons = Container(widgets=[self.b_create_and_init_pipeline,self.b_load_pipeline_template,
                                                      self.b_load_pipeline],
                                             layout='horizontal')
        apply_pipeline_buttons = Container(widgets=[self.b_preview_setting,self.b_apply_pipeline,
                                                    self.b_open_setting_pipeline],
                                           layout='horizontal')
        save_buttons = Container(widgets=[self.b_save_result,self.b_save_pipeline],
                                 layout='horizontal')

        widget_list = [self.title,self.b_load_stack,pipeline_setting_buttons,apply_pipeline_buttons,save_buttons,
                       self.b_close]
        self.main_window = MainWindow(widgets=widget_list)

    def _connect_gui_functions(self):

        self.b_load_stack.clicked.connect(self._onclick_b_load_stack)
        self.b_create_and_init_pipeline.clicked.connect(self._onclick_b_create_and_init_pipeline)
        self.b_save_result.clicked.connect(self._onclick_b_save_result)
        self.b_load_pipeline_template.clicked.connect(self._onclick_b_load_pipeline_template)
        self.b_load_pipeline.clicked.connect(self._onclick_b_load_existing_pipeline)
        self.b_save_result.clicked.connect(self._onclick_b_save_result)
        self.b_open_setting_pipeline.clicked.connect(self._onclick_b_open_pipeline_setting_json)
        self.b_save_pipeline.clicked.connect(self._onclick_pipeline_save)

        self.b_preview_setting.clicked.connect(self._onclick_preview_setting)

        self.b_apply_pipeline.clicked.connect(self._onclick_apply_pipeline)
        self.b_close.clicked.connect(self._onclick_b_close)

    def _onclick_b_close(self,event):

        self.main_window.close()

    def _onclick_b_load_stack(self,event):

        self.stack_gui()
        self.stack_gui.pbutton.clicked.connect(self._onclick_stack_gui_pbutton)

    def _onclick_stack_gui_pbutton(self,event):

        self.stack_gui.gui.close()
        object_initialization_dict = {}
        for n,p in enumerate(self.stack_gui.visible_input_fields):

            reader = self.stack_gui._object._guipi_dictionary[p].widget()[2]
            object_initialization_dict.update({p: reader(self.stack_gui.gui[n])})

        self.working_stack = self.stack_gui._object(**object_initialization_dict)
        self.shared_memory.update({'stack': self.working_stack})
        print('Stack loaded!')

    def _onclick_b_create_and_init_pipeline(self,event):

        self.create_and_init_pipeline_gui.b_ok.clicked.connect(self._onclick_create_and_init_pipeline_gui_b_ok)
        self.create_and_init_pipeline_gui()

    def _onclick_create_and_init_pipeline_gui_b_ok(self,event):

        self.create_and_init_pipeline_gui.gui.close()
        pipeline_folder_path = str(self.create_and_init_pipeline_gui.filefield.value)
        self.shared_memory.update({'pipeline_folder_path': pipeline_folder_path})

        operations_list = []
        for elem in self.create_and_init_pipeline_gui.pipeline_dictionary.values():

            operations_list.append(elem[0])

        self.shared_memory.update({'operation_list': operations_list})
        numbered_operations_list,_ = Pipeline._read_operations_list(operations_list)
        pipeline_setting = {}
        n = 0
        for v in self.create_and_init_pipeline_gui.pipeline_dictionary.values():

            k = numbered_operations_list[n]
            if not 'fit_' in v[0]:

                k = numbered_operations_list[n]
                pipeline_setting.update({k: v[1]})
                n = n+1

        self.shared_memory.update({'pipeline_setting':pipeline_setting})
        self.working_pipeline = self._create_and_initialize_pipeline(operations_list,pipeline_folder_path,pipeline_setting)
        print('Pipeline created and initialized!')

    def _onclick_b_load_existing_pipeline(self,event):

        self.pipeline_load_gui.b_ok.clicked.connect(self._onclick_pipeline_load_gui_b_ok)
        self.pipeline_load_gui()

    def _onclick_pipeline_load_gui_b_ok(self,event):

        self.pipeline_load_gui.gui.close()
        try:

            self.working_pipeline = Pipeline(gui_mode=True)
            path_to_dill_file = str(self.pipeline_load_gui.path_field.value)
            path_to_undillable_folder = os.path.dirname(path_to_dill_file) + os.sep + 'undillable'
            if not os.path.isdir(path_to_undillable_folder):

                path_to_undillable_folder = None

            self.working_pipeline.load(path_to_dill_file, path_to_undillable_folder)
            print('Pipeline loaded!')

        except:

            print('Unable to load the pipeline.')

    def _onclick_b_load_pipeline_template(self,event):

        self.pipeline_template_load_gui.b_ok.clicked.connect(self._onclick_pipeline_template_load_gui_b_ok)
        self.pipeline_template_load_gui()

    def _onclick_pipeline_template_load_gui_b_ok(self,event):

        self.pipeline_load_gui.gui.close()
        try:

            self.working_pipeline = Pipeline(gui_mode=True)
            template_path = str(self.pipeline_template_load_gui.template_path_field.value)
            pipeline_folder_path = str(self.pipeline_template_load_gui.pipeline_folder_path_field.value)
            self.working_pipeline.load_pipeline_template_from_json(template_path,pipeline_folder_path)
            self.working_pipeline.initialize()
            print('Pipeline template loaded!')

        except:

            print('Unable to load the pipeline template.')

    def _onclick_preview_setting(self,event):

        self.preview_setting_gui.b_ok.clicked.connect(self._onclick_preview_setting_gui_b_ok)
        self.preview_setting_gui()

    def _onclick_preview_setting_gui_b_ok(self,event):

        if not hasattr(self,'working_pipeline'):

            print('No working pipeline found, therefore no preview is possible. Create, load a template or'
                  'load an existing pipeline before to setup the preview!')

        else:

            sl_str = str(self.preview_setting_gui.slice_preview_wdg.value)
            sl_list = self.preview_setting_gui.__read_preview_slice(sl_str)
            plg_to_exclude = self.preview_setting_gui.plugin_to_exclude_wdg.value
            self.working_pipeline.setup_preview(slice_list = sl_list,
                                                plugin_to_exclude = plg_to_exclude)

    def _onclick_apply_pipeline(self,event):

        if hasattr(self,'working_stack'):

            self.working_pipeline.apply(self.working_stack)
            print('Pipeline applied!')

        else:

            print('No stack loaded. Load a stack if you want to apply a pipeline.')

    def _onclick_b_open_pipeline_setting_json(self,event):

        try:

            path_to_json_to_open = self.working_pipeline.pipeline_json_path
            directory_path = os.path.dirname(os.path.abspath(path_to_json_to_open))
            directory_path = os.path.join(*directory_path.split('\\')[5:])          # VERY COMPUTER SPECIFIC!! <-------
            json_filename = os.path.basename(os.path.abspath(path_to_json_to_open))
            # os.system('cd\\ & cd {} & start notepad++.exe {}'.format(directory_path,json_filename))
            os.system('U: & cd {} & start notepad++.exe {}'.format(directory_path,
                                                                   json_filename))  # VERY COMPUTER SPECIFIC!! <-------

        except:

            print('No notepad++ installed on your system or your operating system is not Window.')

    def _onclick_b_save_result(self,event):

        if hasattr(self, 'working_stack'):

            self.stack_save_gui = StackSave()
            self.stack_save_gui.b_ok.clicked.connect(self._onclick_stack_save_gui_b_ok)
            self.stack_save_gui()

        else:

            print('Nothing to save. Load a stack (and apply a pipeline) if you want to save something.')

    def _onclick_stack_save_gui_b_ok(self,event):

        self.stack_save_gui.gui.close()
        saving_setting = {}
        for i in range(len(self.stack_save_gui.gui)-1):

            saving_setting.update({self.stack_save_gui.gui[i].name.replace(' ','_'): self.stack_save_gui.gui[i].value})
            if type(self.stack_save_gui.gui[i].value) == pathlib.WindowsPath or \
                type(self.stack_save_gui.gui[i].value) == pathlib.Path:

                saving_setting[self.stack_save_gui.gui[i].name.replace(' ','_')] = \
                    str(saving_setting[self.stack_save_gui.gui[i].name.replace(' ','_')])

        self.working_stack.save(**saving_setting)
        self.shared_memory.update({'stack_saving_setting': saving_setting})

    def _onclick_pipeline_save(self,event):

        if hasattr(self,'working_pipeline'):

            self.working_pipeline.save()
            self.shared_memory.update({'pipeline_saving_setting': self.working_pipeline.pipeline_folder_path})

        else:

            print('No pipeline crated or loaded. Create or load a pipeline if you want to save something.')

        # to complete
