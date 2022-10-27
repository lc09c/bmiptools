# Title: 'gui_basic.py'
# Date: 20/12/21
# Author: Curcuraci L.
#
# Scope: Collect the basic elements which can be useful for the gui creation in bmiptools (and not only...)
#
# Source:
#
# - magicgui reference manual: https://napari.org/magicgui/
#
# Improvements:
#
# - The GuizeObject class can create gui with and without GuiPI. When it create the gui with GuiPI, it can be useful to
#   save as class attribute and in a meaningful way, the 'reader' and 'setter' methods which are returned by the .widget()
#   method of any guipy object.

"""
Collection the basic elements which can be useful for the gui creation in bmiptools. The GUI is created using magicgui as
backend (https://napari.org/magicgui/). In particular, there are:

- custom magicgui widget;

- methods for the creation of gui objects in bmiptools.

"""

#################
#####   LIBRARIES
#################


import numpy as np
import inspect
from benedict import benedict
from magicgui.widgets import create_widget,Container,PushButton,Checkbox,Label,SpinBox,FloatSpinBox,ComboBox,CheckBox,\
    LineEdit,Slider,FloatSlider,FileEdit,RangeEdit,TextEdit,LiteralEvalLineEdit,Table


##################
#####    FUNCTIONS
##################


# make gui out of class objects (general purpose and without GuiPI support)
def _guize_from_pdict(Obj):

    user_initialized_transformation_dict = {}
    flat_dict = benedict(Obj.empty_transformation_dictionary).flatten('__')
    plist = []
    for key in flat_dict.keys():

        keys = key.split('__')
        plist.append([keys, flat_dict[key]])

    max_dept = np.max([len(el[0]) for el in plist])
    l0 = Label(value=2 * max_dept * '#' + '  {}  '.format('Plugin setting') + 2 * max_dept * '#')
    core_wdg_list = []
    added_Label = []
    nested = False
    true_plugin_pos_list = []
    for i in range(len(plist)):

        pname, pval = plist[i]
        if len(pname) > 1:

            for n, pn in enumerate(pname[:-1]):

                if not pn in added_Label:

                    current_dept = max_dept - n - 1
                    text_displayed = (2 * current_dept * '#') + '  {}  '.format(pn.replace('_', ' ')) + (
                            2 * current_dept * '#')
                    li = Label(value=text_displayed)
                    added_Label.append(pn)
                    core_wdg_list.append(li)
                    nested = True

        elif len(pname) == 1 and nested:

            li = Label(value=(len(text_displayed) * '#'))
            core_wdg_list.append(li)
            nested = False

        if 'range' in pname[-1]:

            step = (pval[1] - pval[0]) / pval[2]
            pi = RangeEdit(start=pval[0], stop=step * pval[1], step=step, name=pname[-1].replace('_', ' '))

        else:

            pi = create_widget(name=pname[-1].replace('_', ' '), value=pval)

        core_wdg_list.append(pi)
        true_plugin_pos_list.append(len(core_wdg_list))

    pbutton = PushButton(text='ok')
    wdg_list = [l0] + core_wdg_list + [pbutton]
    cont = Container(widgets=wdg_list)

    @pbutton.clicked.connect
    def close_container(event):

        cont.close()
        for n, true_plugin_pos in enumerate(true_plugin_pos_list):

            val = cont[true_plugin_pos].value
            if type(val) == range:

                val = [val.start, val.stop, val.step]  # FIX IT: only intergers are allowed!!!

            pname = cont[true_plugin_pos].name.replace(' ', '_')
            for key in flat_dict:

                if pname in key.split('__'):

                    flat_dict[key] = val

        user_initialized_transformation_dict.update(dict(flat_dict.unflatten('__')))
        return user_initialized_transformation_dict

    cont.show(run=True)
    return user_initialized_transformation_dict

def _guize_with_pdict(Obj,return_pdict=False):

    initialized_pdict = _guize_from_pdict(Obj)
    if return_pdict:

        return Obj(initialized_pdict), initialized_pdict

    return Obj(initialized_pdict)

def _guize_without_pdict(Obj):

    sgn = inspect.signature(Obj)
    pdict = {}
    for p in sgn.parameters:

        pdict.update({p: sgn.parameters[p]})

    wdg_list = [create_widget(pdict[key].default) for key in pdict]
    for pname, wdg in zip(pdict.keys(), wdg_list):

        wdg.name = pname.replace('_',' ')
        if type(wdg) == type(Checkbox()):

            wdg.text = pname.replace('_',' ')

    pbutton = PushButton(text='ok')
    wdg_list += [pbutton]
    cont = Container(widgets=wdg_list)

    @pbutton.clicked.connect
    def close_container(event):

        cont.close()

    cont.show(run=True)
    print(pdict.keys())
    print({p:cont[n].value for n,p in enumerate(pdict.keys())})
    return Obj(**{p:cont[n].value for n,p in enumerate(pdict.keys())})

def guize(Obj):
    """
    Given a python class with or without GuiPI it returns a gui object.

    :param Obj: (python class) class out of which the gui object is created.
    :return: (python class) the gui object.
    """
    if hasattr(Obj,'empty_transformation_dictionary'):

        return _guize_with_pdict(Obj)

    else:

        return _guize_without_pdict(Obj)


# bmiptools custom widgets
def FloatSpace(start=0, stop=1., nstep=10, min=np.finfo(np.float32).min, max=np.finfo(np.float32).max):

    startSel = FloatSpinBox(min=min, max=max, step=0.0000001, name='Start', value=start)
    stopSel = FloatSpinBox(min=min, max=max, step=0.0000001, name='Stop', value=stop)
    nstepSel = SpinBox(min=min, max=max, step=0.0000001, name='Nstep', value=nstep)
    return Container(widgets=[startSel, stopSel, nstepSel], layout='horizontal')

def FloatSpace_get_value(x):

    start = float(x[0].value)
    stop = float(x[1].value)
    nstep = int(x[2].value)
    return [start, stop, nstep]

def FloatSpace_set_value(wdg,val):

    wdg[0].value = val[0]
    wdg[1].value = val[1]
    wdg[2].value = val[2]
    return wdg

def FloatSpaceText(start=0, stop=1., step=0.1):

    startSel = LineEdit(name='Start', value=start)
    stopSel = LineEdit(name='Stop', value=stop)
    nstepSel = SpinBox(name='Nstep', value=step)
    return Container(widgets=[startSel, stopSel, nstepSel], layout='horizontal')

def FloatSpaceText_get_value(x):

    start = float(x[0].value)
    stop = float(x[1].value)
    nstep = int(x[2].value)
    return [start,stop,nstep]

def FloatSpaceText_set_value(wdg,val):

    wdg[0].value = val[0]
    wdg[1].value = val[1]
    wdg[2].value = val[2]
    return wdg

def FloatRangeText(start=0., stop=1., step=0.1):

    startSel = LineEdit(name='Start', value=start)
    stopSel = LineEdit(name='Stop', value=stop)
    stepSel = LineEdit(name='Step', value=step)
    return Container(widgets=[startSel, stopSel, stepSel], layout='horizontal')

def FloatRangeText_get_value(x):

    start = float(x[0].value)
    stop = float(x[1].value)
    step = float(x[2].value)
    return [start,stop,step]

def FloatRangeText_set_value(wdg,val):

    wdg[0].value = val[0]
    wdg[1].value = val[1]
    wdg[2].value = val[2]
    return wdg

def IntSpace(start=0, stop=100, nstep=10, min=np.iinfo(np.int16).min, max=np.iinfo(np.int16).max):

    startSel = SpinBox(min=min, max=max, step=1, name='Start', value=start)
    stopSel = SpinBox(min=min, max=max, step=1, name='Stop', value=stop)
    nstepSel = SpinBox(min=1, max=max, step=1, name='Nsteps', value=nstep)
    return Container(widgets=[startSel, stopSel, nstepSel], layout='horizontal')

def IntSpace_get_value(x):

    start = int(x[0].value)
    stop = int(x[1].value)
    nstep = int(x[2].value)
    return [start,stop,nstep]

def IntSpace_set_value(wdg,val):

    wdg[0].value = val[0]
    wdg[1].value = val[1]
    wdg[2].value = val[2]
    return wdg


###############
#####   CLASSES
###############


# classes to create gui out of class object and integrate in a main window
class GuizeObject:
    """
    Create gui out of class object.
    """

    def __init__(self,Object):
        """
        Create a gui out of a python class. The gui can be created in two different way:

        - without GuiPI dictionary: the widgets used are determined according to the standard magicgui
        type-widget correspondence. Not always this gives a good result for bmiptools and if th input fields are not
        initialized, the no (useful) widget is assigned for the final gui.

        - with GuiPI dictionary: the widgets are created according to the GuiPI specifications.

        The gui is generated by looking at the input field of the '__init__' method of the class, plus an 'ok' button
        always at the end of the gui. The 'ok' button is reachable via the class attribute '.pbutton'. As such this
        gui have to be understood essentially as a way to initialize the class.

        :param Object: Python class from which the gui is generated.
        """
        self._get_object_input_field(Object)
        self._object = Object
        self._build_gui()

    def __call__(self,run=True):
        """
        Run the gui.
        """

        self.gui.show(run)

    def _get_object_input_field(self,Obj):
        """
        Get the inputs of a python class (i.e. the arguments of the __init__ method)

        :param Obj: Python class to inspect.
        """
        sgn = inspect.signature(Obj)
        self.input_field_dict = {}
        for p in sgn.parameters:

            self.input_field_dict.update({p: sgn.parameters[p]})

        self.visible_input_fields = list(self.input_field_dict.keys())

    def _build_gui(self):
        """
        Build gui according to the object specifications.
        """
        if hasattr(self._object,'_guipi_dictionary'):

            wdg_list = []
            self.visible_input_fields = []
            for d1,d2 in zip(self.input_field_dict.items(),self._object._guipi_dictionary.items()):

                pname = d1[0]
                wdg = d2[1].widget()[0]
                if d2[1].visible:

                    wdg.name = pname
                    if type(wdg) == type(FileEdit()):

                        wdg.mode = 'd'

                    if type(wdg) == type(Checkbox()):

                        wdg.text = pname

                    if type(wdg) == type(FileEdit()) and d1[1].default is None:

                        wdg.value = ''

                    else:

                        wdg.value = d1[1].default

                    wdg_list.append(wdg)
                    self.visible_input_fields.append(pname)

        else:

            wdg_list = [create_widget(self.input_field_dict[key].default) for key in self.input_field_dict]
            for pname, wdg in zip(self.input_field_dict.keys(),wdg_list):

                wdg.name = pname
                if type(wdg) == type(Checkbox()):

                    wdg.text = pname

        self.pbutton = PushButton(text='ok')
        wdg_list += [self.pbutton]
        self.gui = Container(widgets=wdg_list)

class GuizeObjectFromDict:
    """
    Create gui out of class object with or without GuiPI dictionary.
    """

    def __init__(self,Object):
        """
        Create a gui out of a python class when the class inputs is a dictionary (like the transfomation_dictionary in
        all the bmiptools plugin). The python class need to have as global attibute a dictionary called
        'empty_transformation_dictionary', where all the default parameters are stored. The gui can be created in two
        different way:

        - without GuiPI dictionary: the widgets used are determined according to the standard magicgui type-widget
                                    correspondence. Not always this gives a good result for bmiptools and if th input
                                    fields are not initialized, the no (useful) widget is assigned for the final gui.

        - with GuiPI dictionary: the widgets are created according to the GuiPI specifications.

        The gui is generated by looking at the 'empty_transformation_dictionary' attribute of the class, plus an 'ok'
        buttin always at the end of the gui. The 'ok' button is reachable via the class attribute '.pbutton'. As such
        this gui have to be understood essentially as a way to initialize the class via its transformation dictionary.

        :param Object: Python class from which the gui is generated.
        """
        self._object = Object
        self._get_object_params(Object.empty_transformation_dictionary)
        if hasattr(Object,'_guipi_dictionary'):

            self._build_gui_with_guipi()

        else:

            self._build_gui_without_guipi()

    def __call__(self,run=True):
        """
        Run the gui.
        """

        self.gui.show(run)

    def _get_object_params(self,td):
        """
        Utility function which returns from a dictionary (possible nested) a list of paris [key,value], where the keys
        are the one of the corresponding flattened dictionary and the values are the corresponding values in the input
        dictionary.

        :param td: (dict) the transformation dictionary of the object.
        """
        flat_dict = benedict(td).flatten('__')
        self.plist = []
        for key in flat_dict.keys():

            keys = key.split('__')
            self.plist.append([keys, flat_dict[key]])

    def _build_gui_without_guipi(self):
        """
        Build a gui when no GuiPI dictionary is available.
        """
        max_dept = np.max([len(el[0]) for el in self.plist])
        l0 = Label(value=2 * max_dept * '#' + '  {}  '.format('Plugin setting') + 2 * max_dept * '#')
        core_wdg_list = []
        added_Label = []
        nested = False
        self.true_plugin_pos_list = []
        for i in range(len(self.plist)):

            pname, pval = self.plist[i]
            if len(pname) > 1:

                for n, pn in enumerate(pname[:-1]):

                    if not pn in added_Label:

                        current_dept = max_dept - n - 1
                        text_displayed = (2 * current_dept * '#') + '  {}  '.format(pn.replace('_', ' ')) + (
                                2 * current_dept * '#')
                        li = Label(value=text_displayed)
                        added_Label.append(pn)
                        core_wdg_list.append(li)
                        nested = True

            elif len(pname) == 1 and nested:

                li = Label(value=(len(text_displayed) * '#'))
                core_wdg_list.append(li)
                nested = False

            if pval is None:

                pval = ''

            pi = create_widget(name=pname[-1].replace('_', ' '), value=pval)

            core_wdg_list.append(pi)
            self.true_plugin_pos_list.append(len(core_wdg_list))

        self.pbutton = PushButton(text='ok')
        self.wdg_list = [l0] + core_wdg_list + [self.pbutton]
        self.gui = Container(widgets=self.wdg_list)

    def _build_gui_with_guipi(self):
        """
        Build a gui when GuiPI dictionary is available.
        """
        max_dept = np.max([len(el[0]) for el in self.plist])
        l0 = Label(value=2 * max_dept * '#' + '  {}  '.format('Plugin setting') + 2 * max_dept * '#')
        core_wdg_list = []
        added_Label = []
        nested = False
        self.true_plugin_pos_list = []
        for i in range(len(self.plist)):

            pname, pval = self.plist[i]
            guipi_dict_search_key = '.'.join(pname) if len(pname)>1 else pname[0]
            if len(pname) > 1:

                for n, pn in enumerate(pname[:-1]):

                    if not pn in added_Label:
                        current_dept = max_dept - n - 1
                        text_displayed = (2 * current_dept * '#') + '  {}  '.format(pn.replace('_', ' ')) + (
                                2 * current_dept * '#')
                        li = Label(value=text_displayed)
                        added_Label.append(pn)
                        core_wdg_list.append(li)
                        nested = True

            elif len(pname) == 1 and nested:

                li = Label(value=(len(text_displayed) * '#'))
                core_wdg_list.append(li)
                nested = False

            param_guipi = benedict(self._object._guipi_dictionary)[guipi_dict_search_key]
            if param_guipi.visible:

                pi,setter,_ = param_guipi.widget(name = pname[-1].replace('_',' '))
                pi = setter(pi,pval)
                core_wdg_list.append(pi)
                self.true_plugin_pos_list.append(len(core_wdg_list))

            else:

                continue

        self.pbutton = PushButton(text='ok')
        self.wdg_list = [l0] + core_wdg_list + [self.pbutton]
        self.gui = Container(widgets=self.wdg_list)


# basic class for the storage of useful information for the automatic gui creation in bmip_tool
class GuiPI:
    """
    Basic class for the storage of useful information for the automatic GUI creation in bmip_tool
    """

    def __init__(self,p_type=None,min=None,max=None,options=None,description=None,name=None,filemode=None,visible=True):
        """
        GuiPI, i.e. Gui Parameter Information, is an object which store information about the parameters relevant for
        the automatic gui construction.

        * int;
        * bool;
        * float;
        * str;
        * path;
        * list <- a python list
        * options <- list of objects among which the user can choose;
        * range int <- from A to B with a step of C with A,B,C integer;
        * range float <- from A to B with a step of C with A,B,C float;
        * span int <- from A to B in C steps with A,B,C integer;
        * span float <- from A to B in C steps with A,B,C float;
        * math <- mathematical object, e.g. vector,matrix,ecc... + python slicing notation, e.g. [-500,None] to indicate x[-500:];
        * table <- list-of-list expressing tabular data, e.g. [[key1, value1],[key2,value2],...].


        :param p_type: type of parameter. If chosen according to the list above a reasonable behaviour is expected;
        :param min: minimum value for the parameter;
        :param max: maximum value for the parameter;
        :param options: list containing the possible options among which the user can choose;
        :param description: text containing a brief description of the parameter;
        :param name: name of the parameter.
        :param filemode: mode for the FileDialogMode used when p_type = 'path', otherwise is ignored. It can be:

                                    * 'r' returns one existing file.
                                    * 'rm' return one or more existing files.
                                    * 'w' return one file name that does not have to exist.
                                    * 'd' returns one existing directory.

        :param visible: if the widget will be visible or not in the final gui.
        """
        self.p_type = p_type
        self.min = min
        self.max = max
        self.options = options
        self.description = description
        self.name = name
        self.filemode = filemode
        self.visible = visible

        self._check()

    def _check(self):
        """
        Check, initialize with standard values, and (eventually) correct the GuiPI object when created.
        """
        if self.p_type == int:

            self._max_is_none = self.max is None
            if self.max is None:

                self.max = np.iinfo(np.uint16).max

            self._min_is_none = self.min is None
            if self.min is None:

                self.min = np.iinfo(np.uint16).min

        if self.p_type is float:

            self._max_is_none = self.max is None
            if self.max is None:

                self.max = np.finfo(np.float32).max

            self._min_is_none = self.min is None
            if self.min is None:

                self.min = np.finfo(np.float32).min

        if self.options != None:

            self.p_type = 'options'

        if self.p_type == 'path' and not self.filemode in ['r','rm','w','d']:

            self.filemode = 'r'

    @staticmethod
    def _standard_set_value(wdg, val):
        """
        Default method to initialize the state of a widget

        :param wdg: widget to initialize;
        :param val: value to set.
        """
        wdg.value = val
        return wdg

    @staticmethod
    def _standard_get_value(wdg):
        """
        Default method to read the state of a widget

        :param wdg: widget to read.
        """
        return wdg.value

    def widget(self,name=None):
        """
        Methods returning the widget, setter and reader method according to the convention chosen by GuiPI.

        :param name: (str) optional, the name of the plugin (also the text typically displayed in the widget);
        :return: the widget, the corresponding setter and reader methods.
        """
        plugin_name = name
        if plugin_name is None:

            plugin_name = self.name

        if self.p_type == int:

            if not self._min_is_none and not self._max_is_none:

                widget = Slider(min=self.min, max=self.max, tracking=True, readout=True,
                                name=plugin_name, tooltip=self.description)
                setter = self._standard_set_value
                reader = self._standard_get_value

            else:

                widget = SpinBox(value=self.min, min=self.min, max=self.max, name=plugin_name,
                                 tooltip=self.description)
                setter = self._standard_set_value
                reader = self._standard_get_value

        elif self.p_type == bool:

            widget = CheckBox(text=plugin_name,tooltip=self.description,name=plugin_name)
            setter = self._standard_set_value
            reader = self._standard_get_value

        elif self.p_type == float:

            if not self._min_is_none and not self._max_is_none:

                widget = FloatSlider(min=self.min, max=self.max, tracking=True, readout=True, step=0.0000001,
                                     name=plugin_name, tooltip=self.description)
                setter = self._standard_set_value
                reader = self._standard_get_value

            else:

                widget = FloatSpinBox(value=self.min, min=self.min, max=self.max,step=0.0000001, name=plugin_name,
                                      tooltip=self.description)
                setter = self._standard_set_value
                reader = self._standard_get_value

        elif self.p_type == str:

            widget = LineEdit(name=plugin_name, tooltip=self.description)
            setter = self._standard_set_value
            reader = self._standard_get_value

        elif self.p_type == 'path':

            widget = FileEdit(name=plugin_name, tooltip=self.description, mode=self.filemode)
            setter = lambda wdg, val: wdg
            reader = lambda wdg: str(wdg.value)

        elif self.p_type == list:

            widget = LiteralEvalLineEdit(value=[],name=plugin_name, tooltip=self.description)
            setter = self._standard_set_value
            reader = self._standard_get_value

        elif self.p_type == 'options':

            widget = ComboBox(value=self.options[0], choices=self.options, name=plugin_name,
                              tooltip=self.description)
            setter = self._standard_set_value
            reader = self._standard_get_value

        elif self.p_type == 'range int':

            widget = RangeEdit(name=plugin_name, tooltip=self.description)
            setter = lambda wdg, val: self._standard_set_value(wdg,range(val[0],val[1],val[2]))
            reader = lambda wdg: [self._standard_get_value(wdg).start,
                                  self._standard_get_value(wdg).stop,
                                  self._standard_get_value(wdg).step]

        elif self.p_type == 'range float':

            widget = FloatRangeText()
            widget.name = plugin_name
            widget.tooltip = self.description
            setter = FloatRangeText_set_value
            reader = FloatRangeText_get_value

        elif self.p_type == 'span int':

            widget = IntSpace()
            widget.name = plugin_name
            widget.tooltip = self.description
            setter = IntSpace_set_value
            reader = IntSpace_get_value

        elif self.p_type == 'span float':

            widget = FloatSpaceText()
            widget.name = plugin_name
            widget.tooltip = self.description
            setter = FloatSpaceText_set_value
            reader = FloatSpaceText_get_value

        elif self.p_type == 'math':

            def _custom_set_value(wdg,val):

                if type(val) == str:

                    good_val = '\'{}\''.format(val)
                    return self._standard_set_value(wdg,good_val)

                else:

                    return self._standard_set_value(wdg,val)

            widget = LiteralEvalLineEdit(value=[],name=plugin_name, tooltip=self.description)
            setter = _custom_set_value
            reader = self._standard_get_value

        elif self.p_type == 'table':

            widget = Table(name=plugin_name, tooltip=self.description)
            setter = self._standard_set_value
            reader = self._standard_get_value

        else:

            widget = create_widget(self.p_type)
            widget.name = plugin_name
            widget.tooltip = self.description
            setter = self._standard_set_value
            reader = self._standard_get_value

        return widget,setter,reader




