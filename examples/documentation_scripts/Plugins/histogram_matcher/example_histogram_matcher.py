# Title: 'example_histogram_matcher.py'
# Author: Curcuraci L.
# Date: 29/06/2022
#
# Scope: Script used to produce the images in the histogram matcher page of the documentation

import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import data_manager as dm

from bmiptools.stack import Stack
from bmiptools.transformation.dynamics.histogram_matcher import HistogramMatcher


if __name__ == '__main__':

    # setup
    pdata,rdata = dm.get_paths_from_args()
    path_to_stack,_ = dm.dataIn_manager('stack1',pdata)
    path_to_results,_ = dm.dataOut_manager('histogram_matcher',rdata)

    # load stack
    s = Stack()
    s.load_slices(path=path_to_stack,S = list(range(25,45)))

    # save result before histogram matching
    s.save_as_gif(saving_path=path_to_results,
                  saving_name='pre_histogram_matcher',
                  data_type=np.uint8,
                  standard_saving=True,
                  save_metadata=False)

    # initialize histogram matcher
    td = HistogramMatcher.empty_transformation_dictionary
    hm = HistogramMatcher(td)

    # apply histogram matching
    hm.transform(s)

    # save result after histogram matching
    s.save_as_gif(saving_path=path_to_results,
                  saving_name='post_histogram_matcher',
                  data_type=np.uint8,
                  standard_saving=True,
                  save_metadata=False)