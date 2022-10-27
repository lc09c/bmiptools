# BioMaterial Image Processing TOOLS

> Copied from https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/

Current version: 1.0.1

Last update: 26/09/2022

PyPI: https://pypi.org/project/bmiptools/

Documentation: https://bmiptools.readthedocs.io/en/latest/

Author: Curcuraci L.

Contacts: Luca.Curcuraci@mpikg.mpg.de


This is a python library for image processing developed at Max-Plank-Institute fuer Kolloid-und Grenzflaechenforschung. This library contains a series of plugins designed to correct or reduce some typical artifacts present on the typical FIB-SEM images.

> __Note__: This a short guide of bmiptools, and there is no guarantee it will be keep updated. The bmiptools documentation is the correct reference for that.

## How to install it.

To create and setup the python environment, one needs to install Python 3.8 and Anaconda on the computer.

##### CPU

To install bmiptools and use it on CPU only open the Anaconda prompt and write the instruction below.

```
$ conda create -n bmiptools_env python=3.8
$ conda activate bmiptools_env
$ (bmitools_env) pip install bmiptools

```
##### GPU

To run bmiptools with GPU acceleration you need a CUDA-compatible GPU having compute capability of 3.5 or higher. To install bmiptools open the Anaconda prompt and write the instruction below.

```
$ conda create -n bmiptools_env python=3.8
$ conda activate bmiptools_env
$ (bmitools_env) conda install cudatoolkit==10.1.243
$ (bmitools_env) conda install cudnn==7.6.5
$ (bmitools_env) pip install bmiptools

```

## How to configure global variables: verbosity level and multiprocessing.

The `bmiptools` library has a series of global variables which determine the overall behavior of the whole library. In particular, one can set the overall verbosity level of the library and configure the multiprocessing setting of the library. **The setting of this global variable have to be done right after the loading of the import of the library, otherwise unexpected behavior may happens.**

##### Verbosity level.
The verbosity level determines the message displayed by the library to the user and can be regulated. Disabling verbosity, only 
essential messages are printed on the terminal. The code below show how to set the verbosity level:

```
import  bmiptools

bmiptools.set_verbosity(0)               # disable verbosity
bmiptools.set_verbosity(1)               # enable verbosity 
```

##### Multiprocessing.
Multiprocessing can be enabled or disabled. In principle two possible parallelization are available: parallelization of the plugins' internal operations or parallelization over pipeline application. Currently, only the first is available. To set these setting the code below can be used:

```
import  bmiptools

bmiptools.set_use_multiprocessing(1)     # enable  multiprocessing (0 = disable multiprocessing)
bmiptools.set_multiprocessing_type(1)    # choose plugins' parallelization (0 = pipeline parallelization)
bmiptools.set_cpu_buffer(2)              # number of cpus which are not used for the parallelization (i.e. only 
                                          # total_number_of_cpu-2 cpus are used for parallelization). To not use
                                          # 3 cpus, replace 2 with 3, and so on.
```

## Use the bmiptools python API

### How to load a stack and how to save it.

One of the two basic objects of the library is the `Stack` object. A stack can be loaded from a multitiff image or from a folder containing a collection of tiff images, and saved in the same way. In addition, a stack can also be saved as gif file, to have a rapid 3D preview of the content.

#### Loading
A single multitiff, or a collection of tiff images in a folder can be loaded in stack object. For a multitiff one can use the code below

```
from bmiptools.stack import Stack

path_to_multitiff_image = r'PATH_TO_MULTITIFF'

stack = Stack(path = path_to_tiff_image)
```

In case the stack is contained in a folder (as collection of tiff) images, the code below show how to load it. Note that this time you have to specify the path of the folder containing the images.

```
from bmiptools.stack import Stack

path_to_tiff_folder = r'PATH_TO_FOLDER'

stack = Stack(path = path_to_tiff_image,from_folder = True)
```

The stack is reconstructed assuming that the alphabetic order of the single tiff images is equal to the ordering along the z-axis.
Finally, a stack can be initialized empty, and filled later using a numpy array. 

```
import numpy as np
from bmiptools.stack import Stack

# empty stack
stack = Stack(load_stack = False)

# generate some random content
x = np.random.uniform(0,1,size=(30,200,200))

# fill the stack
stack.from_array(x)
```

> **How to specify the file extension.**
>
> Sometimes one need to specify the file extension in order to correctly load the stack (both from a folder or from a multitiff). This can be done by specifying it in the variable `loading_extension` of a `Stack` when you initialize it (it is set equal to 'tiff' as default.)

#### Saving

The content of stack can be saved using the code below:

```
import numpy as np

saving_path = 'PATH_TO_THE_FOLDER_WHERE THE_STACK_IS_SAVED'
saving_name = 'STACK_NAME'
stack.save(saving_path,saving_name,standardized_saving=True,data_type=np.uint8,mode='all_stack')
```

This code will save the stack as a single multitiff image. To save the stack as a folder containing a tiff image for each slice, one have to set `mode='slice_by_slice'`. To save the stack as an animated gif, the code below can be used

```
import numpy as np

saving_path = 'PATH_TO_THE_FOLDER_WHERE THE_STACK_IS_SAVED'
saving_name = 'STACK_NAME'
stack.save_as_gif(saving_path,saving_name,standardized_saving=True,data_type=np.uint8)
```

### Plugins: what they are and what they do.

Plugins are the basic building blocks of the library. They can be used to apply specific transformations on a stack. The currently available plugins are:

- `Standardizer`: which can be used to standardize the pixel value in a stack;
- `HistogramMatcher`: which can be used to match the histograms among the various slices of a stack.
- `Denoiser`: which can be used to reduce the noise level of the slices using classical denoising techniques;
- `DenoiserDNN`: which can be used to reduce the noise leve of the slices using the Noise2Void approach;
- `Destriper`: which can be used to eliminate the curtaining artifacts, typical of Cryo FIB-SEM images;
- `Flatter`: which can be used to remove in the slice a slowly varying brightness variation;
- `Decharger`: which can be used to reduce the charging artifact, typical of Cryo FIB-SEM images;
- `Registrator`: which can be used to align the stack;
- `Affine`: which can be used to apply a generic affine transformation (e.g a rotation) on a stack;
- `Cropper`: which can be used to crop a specific region of a stack;
- `Equalizer`: which can be used to enhance the contrast in an image using CLAHE algorithm.

How these plugin works and which parameters they have, will be explained in future when notes for each plugin will be available. 

### How to create, apply, save and load a pipeline.

The second basic object of the library is the `Pipeline` object.

After the import of the pipeline module, the list of the currently available plugin is contained in the `PLUGINS` dictionary of the module. This list of installed plugins can be obtained as follows:

```
from bmiptools.setting.installed_plugin import PLUGINS

print(PLUGINS.keys())
```
To use a pipeline of transformation on a stack one have to create, initialize, and apply a `Pipeline` object. After that, the pipeline can be saved. 

#### pipeline creation.

The first operation to do to work with pipelines in `bmiptools` is to create them. In order to do that, one have to

1. specify a list of plugins writing the name of the plugins, and their order of application in the list (plugins can be repeated multiple times);
2. specify a folder used to save all the pipeline information;
3. (optional) specify a pipeline name.

once that this is done, the creation of the te pipeline can be done. The code below is an example of how to do that

```
from bmiptools.pipeline import Pipeline

operation_lists = ['Standardizer','Flatter','Decharger']
pipeline_path = r'PATH_TO_PIPELINE_FOLDER'
name = 'NAME'

pipeline = Pipeline(operation_lists = operation_lists,
                    pipeline_folder_path = pipeline_path,
                    pipeline_name = name)
```

> **fit order**
>
> By default, a plugin is fitted (if possible) just before the application of it on the stack. On the other hand the fit and application of the plugin may be done in different time. This can be done by specifying when the fit have to be done in the
`operation_lists` by writing 'fit_' before the name of the plugin. In the example below, the fit of the `Flatter` plugin happens
before the application of the `Decharger` plugin, and only then the `Flatter` plugin is applied.
>
>```
>operation_lists = ['Standardizer','fit_Flatter','Decharger','Flatter']
>```
>

#### pipeline initialization.

Once that the pipeline is created, a json file is created in the pipeline folder. This json file contains in the field `pipeline_setting` a series of dictionary (one for each plugin) containing all the parameters of the plugins. The user have to set these parameters manually and once that this is done, the pipeline can be initialized using the code below

```
pipeline.initialize()
```

#### pipeline application.

The application of the pipeline (with eventual fitting according to the order specified during the creation) on a previously loaded (or created) stack `stack_1`, can be done simply as follows:

```
pipeline.apply(stack_1)
```

#### pipeline saving and loading.

To save a pipeline just use:

```
pipeline.save()
```

To load a previously saved pipeline, one can use:

```
path_to_pipeline_file = r'PATH_TO_DILL_FILE'
pipeline.load(path_to_pipeline_file)
```

After the loading the pipeline, it can be applied using the code explained before. In case the pipeline was saved after a fit, the application of the loaded pipeline does not execute a new fit, but uses the parameters found previously. 

### Basic visualization tools.

The `bmiptools` library have also basic visualization tools based on matplotlib. For the moment only 2D tools are implemented. The code below show how to use some of them to visualize the slice of the stack `stack_1`

```
from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2D as b2d

# plot the slice 0
b2d.show_image(stack_1[0])

# plot the 2d image of slice 0 as 3d surface
b2d.plot_image_as_surface(stack_1[0])

# plot a mask on the slice 0
mask = ....                                     # numpy array containig the mask
b2d.show_threshold_on_image(stack_1[0],mark)
```

### bmiptools as low level API: working at plugin level.

The `Pipeline` method is the most automatized way to apply a series of a plugins to a stack. By the way it does not allow to have a low level interaction with the individual plugins. This can be important for example to control the result of a certain transformation
on a stack, without applying a full pipeline of transformation. The `bmiptools` library allows easily a more 'low-level' interaction with the plugins. 

Any plugin can be imported individually. All the plugins have the method `.fit` to automatically estimate the plugin parameters (if possible) for a certain stack. To apply the plugin on a stack, the `.transform` method must be called. It is not necessary to call the `.fit` method before the call of the `.trasform` methods, since if the plugin auto-optimization is enabled the `.fit` is called automatically. An example of application of a plugin to a stack object contained in the  `stack_1` variable can be found below:

```
# import a plugin
from bmiptools.transformation.restoration.standrdized import Standardizer

# get a sample transformation dictionary of the plugin
transformation_dictionary = Standardizer.empty_transfortmation_dictionary

# set the parameters in the transformation dictionary
transformation_dictionary['standardizer_type'] = '0/1' 

# initialize the plugin with the selected parameters
stand_plug = Standardizer(transformation_dictionary)

# apply the plugin on a stack
stand_plug.transform(stack_1)
```

The plugin will (eventually) fit and apply the transformation on the stack contained in the `stack_1` variable. Note that the in this way the content of the `stack_1` is overwritten with the result of the plugin application. To avoid that one can proceed as indicated below:

```
# apply the plugin on a stack BUT save the result in the variable transformation_result
transformation_result = stand_plug.transform(stack_1,inplace=False)
```

in this case, `stack_1` is not overwritten, and the result is saved as numpy array in `transformation_result`.

### What about metadata?

Sometimes tiff images contains relevant metadata. To load them when also the images are loaded just use the code below:

```
from bmiptools.stack import Stack

path_to_stack = r'PATH_TO_STACK'

stack = Stack(path_to_stack,load_metadata=True)
```

At the moment this functionality may work only for a restricted number of metadata formats, due to the lack of standardization in the metadata organization.

## Use the bmiptools gui

bmiptools is also equipped with a basic graphical interface, which allow to do all the operations explained above, like loading and saving a stack or creating, initializing, applying and saving a pipeline. To do that, one just need to run the script `run_gui.py` as module with the python interpreter.

```
>>> (bmiptools_env) python -m bmiptools.run_gui
```

where it is assumed that bmiptools is installed in the python environment called `bmiptools_env`.
