# Title: 'example_basic_stack-pipeline.py'
# Author: Curcuraci L.
# Date: 20/07/2022
#
# Scope: Example of pipeline application to a stack via the bmiptools python API.


#################
#####   LIBRARIES
#################


import os
import sys

sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.pipeline import Pipeline

############
#####   MAIN
############


if __name__ == '__main__':
    ### Inputs

    # setup
    pdata, rdata = dm.get_paths_from_args()
    path_to_stack, from_folder = dm.dataIn_manager('stack2', pdata)
    path_to_results, _ = dm.dataOut_manager('basic_stack_pipeline', rdata)

    # stack related
    final_stack_path = path_to_results + os.sep + 'result'  # saving path of the final stack
    final_stack_name = 'processed_stack'  # saving name of the final stack

    # pipeline related
    pipeline_folder_path = path_to_results + os.sep + 'pipeline_folder'  # path to the pipeline working folder
    pipeline_name = None  # name of the pipeline (optional)
    pipeline_op_list = ['Cropper', 'Standardizer', 'HistogramMatcher', 'fit_Registrator', 'Destriper',
                        'Decharger', 'DenoiseDNN', 'Standardizer', 'Registrator']

    ### Correct stack using a pippeline

    # load a sample stack
    sample = Stack(path=path_to_stack,
                   load_metadata=True,
                   from_folder=from_folder)

    # create a pipeline
    pip = Pipeline(operation_list=pipeline_op_list,
                   pipeline_folder_path=pipeline_folder_path,
                   pipeline_name=pipeline_name)

    # initialize the pipeline AFTER specification of the parameters in json of the pipeline
    pip.initialize()

    # apply the pipeline
    pip.apply(sample)

    # save the pipeline
    pip.save()

    # save the final stack
    sample.save(saving_path=final_stack_path,
                saving_name=final_stack_name,
                standardized_saving=True,
                save_metadata=True,
                data_type=np.uint8,
                mode='slice_by_slice')