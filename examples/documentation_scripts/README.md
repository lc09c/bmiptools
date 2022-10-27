## Documentation scripts

All the scripts here has been used to produces the images and animations used in the bmiptools documentation.
The input data are all contained in the `Data.zip` file available at https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/tree/master/examples/documentation_scripts.

#### Hot to run these example scripts

The example scripts are designed to reproduce the images used in the bmiptools documentation simply by running them with a python interpreter. More precisely, the procedure below should be followed in order to execute them without issues.

1. Download this repositoy by clicking on the download icon near the 'Clone' button.

2. Unzip the downloaded folder and then unzip the Data.zip file. The final organization of the downloaded folder should look like below

   ```
   documentation_scripts
            |
            +----README.md
            |
            +----Data.zip
            |
            +----Miscellanemous
            |          |
            |          +----[...]
            |
            +----Plugins
            |       |
            |       +----[...]
            |
            +----Data
                   |
                   +----credits.txt
                   |
                   +----stack1
                   |       |
                   |       +----[...]
                  ...
                   |
                   +----stack5
                           |
                           +----[...]

   ```
3. In the python environment where bmiptool is installed (here is assumed it is called `bmiptools_env`) run the desired python script from the    
   `documentation_scripts` folder. For example, in the example below is shown how to run the example script for the standardizer.

   ```
   > conda activate bmiptools_env
   > cd [PATH TO THE 'documentation_scripts' FOLDER]\documentation_scripts
   [PATH TO THE 'documentation_scripts' FOLDER]\documentation_scripts> python Plugins\standardizer\example_standardizer.py
   ```

> Note:
> One may experience import error if the scripts are not executed from the right folder, since functions contained in the `data_manager.py` file are imported in the various example scripts, in order to standardize the I/O operations.  
