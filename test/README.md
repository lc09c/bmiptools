## bmiptools unit tests

The main functionalities of bmiptools can be tested using the `bmiptools_test.py` script togher with the reference results contained in `test_data`. To run these test one can simply follow the steps below.

1. Download the folder by clinking on the download icon near the clone button above (and later unzip its conent). 

2. Open the Anaconda proprt and navigate till the downloaded folder. 

    ```
    (base)> cd [PATH TO THE UNZIPPED DOWNLOADED FOLDER]
    ```

3. Activate the python enviroment in which bmiptools is installed (below is assumed it is called `bmiptools_env`) and run the `bmiptools_test.py` script.

    ```
    (base) [PATH TO THE UNZIPPED DOWNLOADED FOLDER]> conda activate bmiptools_env
    (bmiptools_env) [PATH TO THE UNZIPPED DOWNLOADED FOLDER]> python bmiptools_test.py
    ```

If all the test are succeffully passed, an `OK` will appear at the end.
