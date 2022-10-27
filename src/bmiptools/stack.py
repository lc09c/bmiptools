# Title: 'stack.py'
# Date: 25/01/21
# Author: Curcuraci L.
#
# Scope: This file contains classes useful to open, save and retrive basic information on (stacked) images.
#
# Source: based L. Bertinetti previous I/O scripts.

"""
I/O methods of bmiptools.
"""


#################
#####   LIBRARIES
#################


import numpy as np
import imageio
import re
import itertools
import random
import os
import json
import glob
import exifread
from pathlib import Path
from exifread.utils import Ratio
from PIL.TiffTags import TAGS
from joblib import Parallel,delayed

import bmiptools
import bmiptools.core.utils as ut
from bmiptools.core.base import CoreBasic
from bmiptools.gui.gui_basic import GuiPI


###############
##### FUNCTIONS
###############


# TODO: _LOADING_FORMAT vs _loading_extension...can they be the same variable?


############
##### GLOBAL
############


#############
##### CLASSES
#############


class ExperimentalMetadataInspector():
    """
    Class containing methods useful to read experimental metadata of a tiff image.
    """
    __version__ = '0.1'

    def __init__(self, metadata_tag_list):
        """
        :param metadata_tag_list: path to a txt file containing a list of metadata tag (see also
                                  'load_recognized_metadata_tag_list')
        """
        self.TAGS = self.load_recognized_metadata_tag_list(metadata_tag_list) # TAGS that can be recognized
        self.available_TAGS = []                                              # Actual TAGS found in an image (not None
                                                                              # only if 'read_metadata' was executed at
                                                                              # least one time after the class
                                                                              # initialization).
        self.raw_metadata_dict = {}

    def load_recognized_metadata_tag_list(self, metadata_list_path):
        """
        Load the metadata tags which can be recognized in a given image. The list of recognizable metadata have to be
        placed in a txt file organized as follow:

                            <TAG NAME 1>,

                            <TAG NAME 2>,

                            ....,

                            <TAG NAME N>.

        Note the presence of the comma at the end of each tag and that each tag is in a separated line.

        :param metadata_list_path: path to the txt file containing all the metadata tags which may be recognized in an
                                   image
        :return: a list of recognizable metadata tags.
        """
        recognized_tag_list = []
        with open(metadata_list_path,'r') as file:

            while True:

                actual_line = file.readlines(1)
                if len(actual_line) > 0:

                    recognized_tag_list.append(actual_line[0].replace(',\n', ''))

                if not actual_line:

                    break

        return recognized_tag_list

    @staticmethod
    def clean_line(x):
        """
        Remove specific characters from a string (used to ease decoding).

        :param x: string to clean;
        :return: cleaned string.
        """
        return x.replace('\r', '')

    @staticmethod
    def isnumeric(x):
        """
        Check if a certain string contain only numeric data (i.e. the string can be interpreted without error as int or
        float).

        :param x: string to analyse;
        :return: True if the string is numeric, False otherwise.
        """
        return x.replace('.','',1).replace('+','').replace('-','').replace('e','',1).isdigit()

    def read_metadata(self,raw_experimental_setting):
        """
        Given a list of raw metadata, it produces a dictionary where all the information about the metadata are stored.
        The dictionary produced is organized as follow

                {

                <METADATA_TAG_NAME> : {

                    'name': <METADATA FULL NAME>,

                    'value': <NUMERICAL OR STRING VALUE OF THE METADATA>,

                    'uom': <METADATA UNIT OF MEASURE>

                    },

                ...

                }

        P.A.: This function is very 'machine'-specific. It is designed to work for the kind of metadata produced for
        typical FIB-SEM images. For example, this function assumes that the actual metadata and the metadata TAGs are on
        two consecutive lines, hence if this is not the case the correct reading of the metadata may fail. Similar
        considerations hold for the metadata interpretation. As general rule, if the metadata interpretation fail, the
        whole raw metadata line is saved in the final dictionary, but if reading fail nothing is saved.

        :param raw_experimental_setting: list of raw metadata as obtained by splitting on new line escape character of the exifread library

        :return: The experimental metadata.
        """
        raw_experimental_setting = list(map(self.clean_line, raw_experimental_setting))
        experimental_setting = {}
        for tag in self.TAGS:

            try:

                tag_pos = raw_experimental_setting.index(tag)
                self.available_TAGS.append(tag)
                try:

                    metadata = raw_experimental_setting[tag_pos + 1]

                except:

                    metadata = 'Nothing found'

                if metadata.find(' = ') == -1:

                    name = 'Value interpretation failed: whole content saved in \'value\' field.'
                    value = metadata

                else:

                    name, pre_val = metadata.split(' = ')
                    pre_val = pre_val.lstrip()
                    pre_val = pre_val.rstrip()
                    if np.sum([self.isnumeric(b) for b in pre_val.split(' ')]) > 0:

                        tmp = pre_val.split(' ')
                        value = tmp[0]
                        if self.isnumeric(value):

                            value = float(value)
                            if ut.isfloat(value):

                                value = value

                        rest = None
                        if len(tmp) > 1:

                            rest = tmp[1]
                            for i in range(2, len(tmp)):

                                rest = rest + tmp[i]

                            rest = rest.lstrip()

                        uom = rest

                    else:

                        value = pre_val
                        uom = None

                experimental_setting.update({tag: {'name': name, 'value': value, 'uom': uom}})

            except:

                continue

        return experimental_setting

class Stack(CoreBasic):
    """
    Class that in bmiptools load a stack of TIFF images, keep them in memory during the processing,
    and allow to save them when all the transformations have been applied. Eventually it may contains also the metadata
    of all the TIFF images forming the stack.

    Global attributes:

    - _FILE_FORMAT:  file format used to load a stack.

    - _LOADING_MODE:  loading mode of the imageio library.

    - _CHANNEL_INTERPRETATION:  remainder for the user about the interpretation of the stack shape: ZYX(C) means the
      first dimension is the z axis, the second the y axis the third the x axis, and eventually the last dimension is
      for the color channels.

    - _path_experimental_metadata_list: path to the 'experimental_setting_metadata_tag_list.txt' file, which is the txt
      file containing the list of all metadata tags which are read.

    - _experimental_setting_tag_numbers: list of numbers containing the tag number of a TIFF file where the experimental
      metadata are stored (e.g. see https://www.awaresystems.be/imaging/tiff/tifftags.html).

    """
    __version__ = '0.2'
    _FILE_FORMAT = 'TIF'
    _LOADING_MODE = 'I'
    _CHANNEL_INTERPRETATION = 'ZYX(C)'
    _path_experimental_metadata_list = 'experimental_setting_metadata_tag_list.txt'
    _experimental_setting_tag_numbers = [34118]
    _guipi_dictionary = {'path': GuiPI('path'),
                         'load_stack': GuiPI(bool,visible=False),
                         'from_folder': GuiPI(bool),
                         'load_metadata': GuiPI(bool),
                         'image_type': GuiPI('options',options=['FIB-SEM','others']),
                         'name': GuiPI(str),
                         'loading_extension': GuiPI(str)}
    def __init__(self,path=None,load_stack=True,from_folder=True,load_metadata=True,image_type='FIB-SEM',
                 name=None,loading_extension='tiff'):
        """
        Stack initialization. A stack object can be initialized loading an actual file or left empty.

        :param path: (string) path to the stack to load. If 'None' an empty stack object is created.
        :param load_stack: (boolean) if True the stack at the path specified in the 'path' field will be loaded.
        :param from_folder: (boolean) if True the stack is assumed to be split in its slices in a folder whose path
                            is specified in the 'path' field.
        :param load_metadata: (boolean) if True also the metadata in the file, whose path is specified in the 'path'
                              field, will be loaded.
        :param image_type: NOT USED
        :param name: (string, optional) name of the stack.
        :param loading_extension: (string) extension of the file which are loaded.
        """
        super(Stack,self).__init__()
        self._emi = ExperimentalMetadataInspector(bmiptools.__bmiptools_files_folder_path__+os.sep+Stack._path_experimental_metadata_list)
        self.name = name
        self.path = path
        self._loading_extension = loading_extension
        self.temporary_library_metadata = {}          # used to store useful information during transformation if needed

        # stack main attributes
        self.data = None
        self.metadata = None
        self.n_slices = None
        self.n_channels = None
        self.yx_shape = None
        self.shape = None
        self.data_type = None
        self.image_type = image_type

        # statistics
        self.stack_mean = 0
        self.stack_std = 0
        self.slices_means = 0
        self.slices_stds = 0
        self.min_stack = 0
        self.max_stack = 0
        self.min_slices = 0
        self.max_slices = 0

        # loading (eventually)
        self.load_metadata = load_metadata
        if path is not None:

            if load_stack and not from_folder:

                self.load_stack(path)

            elif load_stack and from_folder:

                self.load_stack_from_folder(path)

            elif load_metadata:

                image_metadata,experimental_metadata = self._load_metadata(path)
                self.metadata = {'image_metadata': image_metadata,
                                 'experimental_metadata': experimental_metadata,
                                 'image_processing_metadata': None}

    def __call__(self, *args, **kwargs):

        if hasattr(self.data,'__getitem__'):

            return self.data[args]

        else:

            return self.data

    def __getitem__(self, item):

        if hasattr(self.data,'__getitem__'):

            return self.data[item]

    def __len__(self):

        if hasattr(self.data,'__getitem__'):

            return len(self.data)

        else:

            return 0

    # utility methods
    @staticmethod
    def _is_grayscale(img):
        """
        Core function. Check if a 2D image is grayscale or not.

        :param img: 2D numpy array to check.
        :return: True if the image is a grayscale image.
        """
        test0 = img[0, 0]
        if type(test0) == int:

            test_result = True

        else:

            n_pixels = img.shape[0] * img.shape[1]
            n_px_to_check = np.minimum(int(n_pixels * 0.1),n_pixels)  # for each test 1% of the image pixels are
                                                                      # randomly selected to verify the color type.
            all_pixels = list(itertools.product(range(0, img.shape[0]), range(0, img.shape[1])))
            random.shuffle(all_pixels)
            pool = all_pixels[:n_px_to_check]
            test_result = True
            for px in pool:

                vals = img[px[0], px[1]]
                test_result = test_result and (vals[0] == vals[1] == vals[2])

        return test_result

    @staticmethod
    def _estimate_n_channels(data):
        """
        Core function. Estimate the number of channels in a given image (not a stack!). This estimation is based on the
        convention that channels are in the last dimension.

        :param data: (ndarray) single slice from which the number of channels is estimated.
        :return: number of channels.
        """
        if len(data.shape) > 2:

            return data.shape[-1]

        else:

            return 1

    # statistics methods
    def _update_statistics(self):
        """
        Core function. Compute basic useful statistics on the stack.
        """
        if self.n_channels > 1:

            stack_mean = []
            stack_std = []
            slices_means = []
            slices_stds = []
            max_stack = []
            min_stack = []
            max_slices = []
            min_slices = []
            for C in range(self.n_channels):

                stack_mean.append( self.data[...,C].mean() )
                stack_std.append( self.data[...,C].std() )
                slices_means.append( np.mean(self.data[...,C],axis=tuple(range(1,len(self.data[...,C].shape[1:])+1))) )
                slices_stds.append( np.std(self.data[...,C],axis=tuple(range(1,len(self.data[...,C].shape[1:])+1))) )
                max_stack.append( np.max(self.data[...,C]) )
                min_stack.append( np.min(self.data[...,C]) )
                max_slices.append( np.max(self.data[...,C],axis=tuple(range(1,len(self.data[...,C].shape[1:])+1))) )
                min_slices.append( np.min(self.data[...,C],axis=tuple(range(1,len(self.data[...,C].shape[1:])+1))) )

            stack_mean = np.array(stack_mean)
            stack_std = np.array(stack_std)
            slices_means = np.array(slices_means)
            slices_stds = np.array(slices_stds)
            max_stack = np.array(max_stack)
            min_stack = np.array(min_stack)
            max_slices = np.array(max_slices)
            min_slices = np.array(min_slices)

        else:

            stack_mean = self.data.mean()
            stack_std = self.data.std()
            slices_means = np.mean(self.data,axis=tuple(range(1,len(self.data.shape[1:])+1)))
            slices_stds = np.std(self.data,axis=tuple(range(1,len(self.data.shape[1:])+1)))
            max_stack = np.max(self.data)
            min_stack = np.min(self.data)
            max_slices = np.max(self.data,axis=tuple(range(1,len(self.data.shape[1:])+1)))
            min_slices = np.min(self.data,axis=tuple(range(1,len(self.data.shape[1:])+1)))

        self.stack_mean = stack_mean
        self.stack_std = stack_std
        self.slices_means = slices_means
        self.slices_stds = slices_stds
        self.max_stack = max_stack
        self.min_stack = min_stack
        self.max_slices = max_slices
        self.min_slices = min_slices

    def statistics(self):
        """
        Return a dictionary containing the basic statistics on the stack. They are:

            * 'stack_mean': mean of the whole stack;
            * 'stack_std': standard deviation of the whole stack;
            * 'slices_means': mean value of each slice;
            * 'slices_stds': standard deviation of each slice;
            * 'min_stack': smallest value of the whole stack;
            * 'max_stack': largest value of the whole stack;
            * 'min_slices': smallest value of each slice;
            * 'max_slices': largest value of each slice.

        :return: dictionary of basic statistics on the stack.
        """
        return {'stack_mean': self.stack_mean,
                'stack_std': self.stack_std,
                'slices_means': self.slices_means,
                'slices_stds': self.slices_stds,
                'min_stack': self.min_stack,
                'max_stack': self.max_stack,
                'min_slices': self.min_slices,
                'max_slices': self.max_slices}

    def get_dimension_in_RAM(self):
        """
        Compute the dimension of the stack data in RAM.

        :return: stack data dimension in RAM
        """
        order_list = np.array([0, 3, 6, 9, 12])
        order_name = ['B', 'kB', 'MB', 'GB', 'TB']

        if self.data is not None:

            size_in_RAM_bytes = self.data.size * self.data.itemsize
            order = np.floor(np.log10(size_in_RAM_bytes))
            pos = np.where(order - order_list > 0)
            pos = pos[0][-1]
            uom = order_name[pos]
            val = np.around(size_in_RAM_bytes /10 ** order_list[pos], 2)
            printable_size_in_RAM = '{} {}'.format(val,uom)
            print(printable_size_in_RAM)

    # input methods
    def _load_metadata(self,path):
        """
        Load metadata of a given TIFF image.

        :param path: (str) path to the TIFF image from which the metadata have to be loaded.
        :return: image metadata dictionary and experimental metadata dictionary.
        """
        with open(path, 'rb') as f:

            tags = exifread.process_file(f)

        experimental_setting_tag_name = ['Image Tag {}'.format(hex(tag_number)) for tag_number in
                                         Stack._experimental_setting_tag_numbers]
        image_metadata = {}
        experimental_metadata = {}
        for key in tags.keys():

            content = tags[key]
            if not key in experimental_setting_tag_name:

                try:

                    callback = lambda pat: pat.group(0).lower()
                    tmp = re.sub(r'([A-Z]){4}', callback, TAGS[content.tag])
                    callback2 = lambda pat: '_' + pat.group(1).lower()
                    key = re.sub(r'([A-Z])', callback2, tmp)

                except:

                    continue

                value = content.values
                if len(value) > 0:
                    value = value[0]
                else:
                    value = None
                if key[0] == '_': key = key[1:]
                image_metadata.update({key: value})

            else:

                raw_experimental_setting = str(content.values, 'ascii', 'ignore').split('\n')
                experimental_metadata = self._emi.read_metadata(raw_experimental_setting)

        return image_metadata, experimental_metadata

    def add_metadata(self,metadata_type,content):
        """
        Add some content to the metadata dictionary of the stack. If the stack has no metadata dictionary it is
        created.

        :param metadata_type: key of the dictionary used to specify the kind of metadata (e.g. 'image_metadata',
                              'experimental_metadata', 'image_processing_metadata',...) added to the metadata
                              dictionary of the stack.
        :param content: data (of any kind, a number, a string, a list, a dictionary,...) associated to the
                        'metadata_type' field specified as argument of the function.
        """
        if not hasattr(self,'metadata') or self.metadata == None:

            self.metadata = {}

        self.metadata.update({metadata_type: content})

    def _load(self,path,slice_list = None):
        """
        Core loading function. This function load a stack or a list of slices of it and compute/produce the first basic
        stack attribute.

        :param path: (string) path to the stack to open.
        :param slice_list: (optional) list of slice of the stack to load. If nothing is specified the whole stack is
                           loaded.
        :return: (ndarray) the data loaded.
        """
        reader = imageio.get_reader(path,
                                    format=Stack._FILE_FORMAT,
                                    mode=Stack._LOADING_MODE)
        if slice_list is None:

            self.n_slices = reader.get_length()
            slice_list = range(self.n_slices)

        else:

            self.n_slices = len(slice_list)

        if (slice_list is not None) and (self.n_slices == 1):

            data = np.array(reader.get_data(0))
            self.n_channels = self._estimate_n_channels(data)
            isgray = False
            if self.n_channels > 1:

                isgray = self._is_grayscale(data)

            if isgray:

                self.n_channels = 1
                data = data[:,:,0]

            data = np.expand_dims(data,axis=-1)

        else:

            data = np.array(reader.get_data(slice_list[0]))
            self.n_channels = self._estimate_n_channels(data)
            isgray = False
            if self.n_channels > 1:

                isgray = self._is_grayscale(data)

            if isgray:

                self.n_channels = 1
                data = data[:,:,0]

            data = np.expand_dims(data,axis=-1)
            for i in slice_list[1:]:

                slice = np.array(reader.get_data(i))
                if isgray:

                    slice = slice[:,:,0]

                slice = np.expand_dims(slice, axis=-1)
                data = np.concatenate([data, slice], axis=-1)

        data = data.transpose(tuple([len(data.shape)-1]+[i for i in range(len(data.shape)-1)]))
        return data

    def load_stack(self,path):
        """
        Load a stack (all), compute/produce basic stack attributes, compute stack statistics and eventually load the
        stack metadata.

        :param path: (string) path to the stack to load.
        """
        self.data = self._load(path)
        self.shape = self.data.shape
        self.yx_shape = self.data.shape[1:3]
        self.data_type = self.data.dtype
        self._update_statistics()
        if self.load_metadata:

            image_metadata, experimental_metadata = self._load_metadata(path)
            self.metadata = {'image_metadata': image_metadata,
                             'experimental_metadata': experimental_metadata,
                             'image_processing_metadata': None}

    def load_slices(self,path,S):
        """
        Load only certain slices from a given stack, and based on what is loaded, it compute/produce basic stack
        attributes, compute stack statistics and eventually load the stack metadata.

        :param path: (str) path to the stack to load;
        :param S: (list of int) list of slices to load.
        """
        self.data = self._load(path,slice_list = S)
        self.shape = self.data.shape
        self.yx_shape = self.data.shape[1:3]
        self.data_type = self.data.dtype
        self._update_statistics()
        if self.load_metadata:

            image_metadata, experimental_metadata = self._load_metadata(path)
            self.metadata = {'image_metadata': image_metadata,
                             'experimental_metadata': experimental_metadata,
                             'image_processing_metadata': None}

    def _sorted_read_path(self,path):
        """
        Sort file paths according to a given order, based on the actual convention adopted for a given image_type.

        :param path: (raw str) path of the folder containing the files written as raw string (i.e. r'YOUR PATH');
        :return: (list of str) sorted path.
        """
        slice_paths = glob.glob(path + os.sep + '*.'+self._loading_extension)
        if self.image_type == 'FIB-SEM':            # FIB-SEM name convention used at mpikg

            slice_numbers = []
            for path in slice_paths:

                idx = path.find('slice')
                sn = path[idx + len('slice_'):-len('.'+self._loading_extension)]
                slice_numbers.append(int(sn))

            sorted_slice_paths = list(zip(*sorted(zip(slice_numbers,slice_paths))))[1]

        else:

            sorted_slice_paths = sorted(slice_paths)

        return sorted_slice_paths

    def load_slices_from_folder(self,path,S):
        """
        Load only certain slices from a folder containing a stack (where slices are split as single 2D images),
        and based on what is loaded, it compute/produce basic stack attributes, compute stack statistics and eventually
        load the stack metadata (if each slice has its own metadata, all this metadata are added in the metadata
        dictionary of the stack). The slices are read in alphabetic order and selected according to that order.

        :param path: (string) path to the folder containing the stack to load;
        :param S: (list of integers) list of slices to load. Alphabetic order is assumed.
        """
        all_slice_paths = self._sorted_read_path(path)
        slice_paths = [all_slice_paths[i] for i in S]
        self.n_slices = len(slice_paths)
        if self._use_multiprocessing:

            self._load_stack_from_folder_parallel(slice_paths)

        else:

            self._load_stack_from_folder_serial(slice_paths)

        self.shape = self.data.shape
        self.n_channels = self._estimate_n_channels(self.data[0,...])
        self.yx_shape = self.data.shape[1:3]
        self.data_type = self.data.dtype
        self._update_statistics()

    def _load_stack_from_folder_serial(self,slice_paths):
        """
        Core function. Load the slices of a stack contained in a folder in serial way, and eventually load the metadata
        of each slice too. This core function is used based and with on the global setting of the 'bmiptools' library.

        :param slice_paths: (list of string) list containing the path to the slices to be loaded.
        """
        self.data = []
        if self.load_metadata:

            self.metadata = {'image_metadata': {},
                             'experimental_metadata': {}}

        for n, slice_path in enumerate(slice_paths):

            slice = self._load(slice_path)
            slice = np.squeeze(slice)
            self.data.append(slice)
            if self.load_metadata:

                slice_img_meta, slice_exp_meta = self._load_metadata(slice_path)
                self.metadata['image_metadata'].update({'slice_{}'.format(n): slice_img_meta})
                self.metadata['experimental_metadata'].update({'slice_{}'.format(n): slice_exp_meta})

        self.data = np.array(self.data)

    def _load_stack_from_folder_parallel(self,slice_paths):
        """
        Core function. Load the slices of a stack contained in a folder in parallel way according to the global setting
        of the library, and eventually load the metadata of each slice too. This core function is used based and with
        on the global setting of the 'bmiptools' library.

        :param slice_paths: (list of string) list containing the path to the slices to be loaded.
        """
        def func_to_par(slice_path):

            slice = self._load(slice_path)
            slice = np.squeeze(slice)
            if self.load_metadata:

                slice_img_meta, slice_exp_meta = self._load_metadata(slice_path)
                slice_metadata_dict = {'image_metadata': slice_img_meta,
                                       'experimental_metadata': slice_exp_meta}
                return [slice, slice_metadata_dict]

            else:

                return slice

        result = Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(path) for path in slice_paths)
        if self.load_metadata:

            self.data = np.array([result_line[0] for result_line in result])
            self.metadata = {'image_metadata': {},
                             'experimental_metadata': {}}
            for n, result_line in enumerate(result):

                self.metadata['image_metadata'].update({'slice_{}'.format(n): result_line[1]['image_metadata']})
                self.metadata['experimental_metadata'].update({'slice_{}'.format(n): result_line[1]['experimental_metadata']})

        else:

            self.data = np.array(result)

    def load_stack_from_folder(self,path):
        """
        Load a stack from a folder (i.e. a folder where slices of the stack are split as single 2D images),
        compute/produce basic stack attributes, compute stack statistics and eventually load the stack metadata
        (if each slice has its own metadata, all this metadata are added in the metadata dictionary of the stack).
        The slices are read according to the image_type convention.

        :param path: (string) path to the folder containing the stack to load;
        """
        slice_paths = self._sorted_read_path(path)
        self.n_slices = len(slice_paths)
        if self._use_multiprocessing:

            self._load_stack_from_folder_parallel(slice_paths)

        else:

            self._load_stack_from_folder_serial(slice_paths)

        self.shape = self.data.shape
        self.n_channels = self._estimate_n_channels(self.data[0,...])
        self.yx_shape = self.data.shape[1:3]
        self.data_type = self.data.dtype
        self._update_statistics()

    def from_array(self,arr,with_channel=False,image_metadata=None,experimental_metadata=None,image_processing_metadata=None):
        """
        Fill a stack with the data coming from a numpy array, compute/produce the basic stack attributes and statistic,
        eventually produce the metadata dictionary of the stack. The array is interpreted according the scheme specified
        in the _CHANNEL_INTERPRETATION global attribute.

        :param arr: (ndarray) numpy array containing the data;
        :param with_channel: (boolean) if True it specify that the last dimension of the array contains the channel's
                             information;
        :param image_metadata: (optional) dictionary containing the image metadata;
        :param experimental_metadata: (optional) dictionary containing the experimental metadata;
        :param image_processing_metadata: (optional) dictionary containing the image processing metadata.
        """
        if (len(arr.shape) < 3 and not with_channel) or (len(arr.shape) == 3 and with_channel):

            arr = np.expand_dims(arr,axis=0)

        self.data = np.array(arr)
        self.n_channels = self._estimate_n_channels(self.data[0,...])
        self.n_slices = self.data.shape[0]
        self.shape = self.data.shape
        self.yx_shape = self.data.shape[1:3]
        self.data_type = self.data.dtype
        self._update_statistics()
        if image_metadata is not None or experimental_metadata is not None or image_processing_metadata is not None:

            self.metadata = {'image_metadata': image_metadata,
                             'experimental_metadata': experimental_metadata,
                             'image_processing_metadata': image_processing_metadata}

    # output methods
    def save(self,saving_path,saving_name,mode='all_stack',data_type=None,extension='tiff',standard_saving=False,
             save_metadata=True):
        """
        Save the stack.

        :param saving_path: (string) path where the stack have to be saved.
        :param saving_name: (string) name of the stack.
        :param mode: (string) it can be 'all_stack' or 'slice_by_slice'. If 'all_stack', the whole stack is saved in a
                     single tiff, if 'slice_by_slice' the stack is saved slice by slice in a folder (eventually created)
                     having the same name of the stack.
        :param data_type: data type in which the data are saved (for good compatibility with generic image reader it is
                          recommended to use 'uint8' or 'float32' depending on the kind of image).
        :param extension: (optional) file extension of the saved image(s).
        :param standard_saving: (boolean) if True the data are suitably scaled in order to be compatible with a generic
                                image reader. When false the data is saved as it is: it can be read with this library
                                recovery the exact content saved, but may not be visible with a generic image reader.
        :param save_metadata: (boolean) if True also the metadata dictionary will be saved in json file.
        """
        # prepare data for saving
        if data_type is None:

            data_to_save = self.data

        elif standard_saving:

            data_type = np.dtype(data_type)
            data_to_save = self._standardize_data_for_saving(data_type)

        else:

            data_type = np.dtype(data_type)
            data_to_save = self.data.astype(data_type)

        # save result
        path_to_saved_file = saving_path+os.sep+saving_name
        if save_metadata and hasattr(self, 'metadata'):

            if self.metadata is not None:

                self._save_metadata(path_to_saved_file)
                self.write('Metadata saved!')

        if mode == 'all_stack':

            self._save_stack_in_single_TIFF(path_to_saved_file+'.'+extension,data_to_save,extension)
            self.write('Stack saved!')

        elif mode == 'slice_by_slice':

            if self._use_multiprocessing:

                self._save_stack_slice_by_slice_parallel(path_to_saved_file,data_to_save,extension)

            else:

                self._save_stack_slice_by_slice_serial(path_to_saved_file,data_to_save,extension)

            self.write('Stack saved!')

        else:

            self.write('Saving mode not supported')

    def save_as_gif(self,saving_path,saving_name,data_type=None,standard_saving=False,save_metadata=True,duration=0.2,loop=0):
        """
        Save the whole stack as GIF animation, to have a rapid 3d view of the stack. It is recommended to use
        'data_type = numpy.uint8' and 'standard_saving = True'.

        :param saving_path: (string) path where the stack have to be saved.
        :param saving_name: (string) name of the stack.
        :param mode: (string) it can be 'all_stack' or 'slice_by_slice'. If 'all_stack', the whole stack is saved in a
                     single tiff, if 'slice_by_slice' the stack is saved slice by slice in a folder (eventually created)
                     having the same name of the stack.
        :param data_type: data type in which the data are saved (for good compatibility with generic image reader it is
                          recommended to use 'uint8' or 'float32' depending on the kind of image).
        :param standard_saving: (boolean) if True the data are suitably scaled in order to be compatible with a generic
                                image reader. When false the data is saved as it is: it can be read with this library
                                recovery the exact content saved, but may not be visible with a generic image reader.
        :param duration: (float) duration of a frame of the animation
        :param loop: (int) The number of iterations of the animation. If 0 the loop will be infinite.
        """
        # prepare data for saving
        if data_type is None:

            data_to_save = self.data

        elif standard_saving:

            data_to_save = self._standardize_data_for_saving(data_type)

        else:

            data_to_save = self.data.astype(data_type)

        # save result
        path_to_saved_file = saving_path+os.sep+saving_name
        if save_metadata and hasattr(self, 'metadata'):

            if self.metadata != {}:

                self._save_metadata(path_to_saved_file)
                self.write('Metadata saved!')

        imageio.mimsave(path_to_saved_file+'.gif',data_to_save,duration=duration,loop=loop)
        self.write('Stack saved as gif!')

    def _standardize_data_for_saving(self,data_type):
        """
        Core function. Standardize a stack according to a given datatype.

        :param data_type: data type.
        :return: standardized data.
        """
        # find scaling factor
        scaling_factor = 1
        if data_type == np.uint8:

            scaling_factor = 256

        elif data_type == np.uint16:

            scaling_factor = 65536

        # standardize
        stand_data = self.data
        stand_data = (stand_data-stand_data.min())/(stand_data.max()-stand_data.min())
        stand_data = stand_data*scaling_factor
        stand_data = stand_data.astype(data_type)
        return stand_data

    def _save_stack_in_single_TIFF(self,path,data_to_save,extension):
        """
        Core function. Save the whole stack as a single tiff.

        :param path: (string) full path of the file in which the stack will be saved.
        :param data_to_save: (ndarray) numpy array containing the data to save.
        :param extension: (optional) file extension of the saved image(s).
        """
        writer = imageio.get_writer(path,format=extension,mode=Stack._LOADING_MODE)
        for i in range(self.n_slices):

            self.progress_bar(i,self.n_slices,15,text_after='slices {}/{} saved'.format(i+1,self.n_slices))
            slice = data_to_save[i,...]
            writer.append_data(slice)

        writer.close()

    def _save_stack_slice_by_slice_serial(self,path,data_to_save,extension):
        """
        Core function. Save the whole stack slice by slice in a folder in serial wat.

        :param path: (string) full path of the file in which the stack will be saved.
        :param data_to_save: (ndarray) numpy array containing the data to save.
        :param extension: (optional) file extension of the saved image(s).
        """
        path_to_stack_folder = ut.manage_path(path)
        for n,slice in enumerate(data_to_save):

            self.progress_bar(n, self.n_slices, 15, text_after='slices {}/{} saved'.format(n+1,self.n_slices))
            slice_path = path_to_stack_folder+os.sep+'name__slice_{}.{}'.format(ut.standard_number(n),extension)
            writer = imageio.get_writer(slice_path, format=extension.upper(), mode='I')
            writer.append_data(slice)
            writer.close()

    def _save_stack_slice_by_slice_parallel(self,path,data_to_save,extension):
        """
        Core function. Save the whole stack slice by slice in a folder in parallel way.

        :param path: (string) full path of the file in which the stack will be saved.
        :param data_to_save: (ndarray) numpy array containing the data to save.
        :param extension: (optional) file extension of the saved image(s).
        """
        path_to_stack_folder = ut.manage_path(path)

        def func_to_par(n,slice):

            slice_path = path_to_stack_folder+os.sep+'name__slice_{}.{}'.format(ut.standard_number(n),extension)
            writer = imageio.get_writer(slice_path, format=extension.upper(), mode='I')
            writer.append_data(slice)
            writer.close()

        self.write('saving the stack in parallel mode...')
        Parallel(n_jobs=self._n_available_cpu)(delayed(func_to_par)(n,slice) for n,slice in enumerate(data_to_save))

    def _save_metadata(self,saving_path):
        """
        Core function. Save the metadata of the stack.

        :param saving_path: (string) full path of the json file in which the stack metadata will be saved.
        """
        with open(saving_path+'__metadata.json','w') as jsonfile:

            dumped = json.dumps(self.metadata, cls=ut.ExifreadEncoder)
            dumped = json.loads(dumped)
            json.dump(dumped,jsonfile,indent=4)
