# Title: 'bmiptools_test.py'
# Author: Curcuraci L.
# Date: 25/07/2022
#
# Scope: Unit test for bmiptools.

#################
#####   LIBRARIES
#################


import unittest
import warnings
import copy
import os
import json
import sys
import pickle
import numpy as np

# random seed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'    # suppress INFO messages from tensorflow
np.random.seed(42)
# import tensorflow as tf
# tf.random.set_seed(42)



#######################
#####   READ INPUT ARGS
#######################


arguments = sys.argv
if '--data_path' in arguments:

    idx_dp = arguments.index('--data_path') + 1

elif '-dp' in arguments:

    idx_dp = arguments.index('-dp') + 1

else:

    idx_dp = -1

if idx_dp > 0:

    test_data_path = arguments[idx_dp]

else:

    test_data_path = os.path.dirname(os.path.abspath(__file__))


###############
#####   CLASSES
###############


class BmiptoolsTest(unittest.TestCase):

    def setUp(self):

        warnings.simplefilter('ignore', category=ImportWarning)
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=RuntimeWarning)

    def test_imports(self):

        print('\nRunning imports test...')

        import_list = ['import bmiptools',
                       'from bmiptools.stack import Stack',
                       'from bmiptools.pipeline import Pipeline',
                       'from bmiptools.setting.installed_plugins import PLUGINS',
                       'from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic2D',
                       'from bmiptools.visualization.graphic_tools.basic_graphic_tools import Basic3D',
                       'from bmiptools.visualization.geometric.change_coordinate_system import ChangeCoordinateSystem']
        import_failure = []
        for elem in import_list:

            try:

                exec(elem)
                import_failure.append(False)

            except:

                import_failure.append(True)

        failure = sum(import_failure) > 0
        idx = -1
        if failure:

            idx = import_failure.index(True)

        self.assertEqual(failure,False,'Import command \'{}\' failed!'.format(import_list[idx]))

        print('...DONE!')

    def test_stack(self):

        print('\nRunning stack test...')

        # import necessary modules
        from bmiptools.stack import Stack

        # load stack
        stack = Stack(path=test_data_path+os.sep+r'test_data/test_stack/stack',
                      from_folder=True,
                      load_metadata=False, )

        # get stack statistics
        stats = stack.statistics()
        for k in stats.keys():                  # mimic numpy json serialization for computed stats statistics

            if isinstance(stats[k], np.floating):
                stats[k] = float(stats[k])

            if isinstance(stats[k], np.integer):
                stats[k] = int(stats[k])

            if isinstance(stats[k], np.ndarray):

                tmp = []
                for elem in stats[k]:

                    if isinstance(elem, np.integer):

                        tmp.append(int(elem))

                    elif isinstance(elem, np.floating):

                        tmp.append(float(elem))

                    else:

                        tmp.append(elem)

                stats[k] = tmp

        # load stack reference
        stack_reference = np.load(test_data_path+os.sep+r'test_data/test_stack/data.npy')
        elementwise_comparison_result = np.all(stack.data == stack_reference)
        self.assertEqual(elementwise_comparison_result,True,'Stack loading failed!')

        # load stack statistics reference
        with open(test_data_path+os.sep+r'test_data/test_stack/stats.json', 'r') as file:

            stats_reference = json.load(file)

        self.assertEqual(stats_reference,stats,'Stack statistics computation failed!')

        print('...DONE!')

    def test_pipeline_create_initialize_save_load_compare(self):

        print('\nRunning pipeline test...')

        # import necessary modules
        from bmiptools.pipeline import Pipeline
        from bmiptools.pipeline import PLUGINS

        # create initialize and save a pipeline
        op_list = list(PLUGINS.keys())
        pip = Pipeline(operations_list=op_list,
                       pipeline_folder_path=test_data_path+os.sep+r'test_data/test_pipeline',
                       pipeline_name='test',
                       gui_mode=True)
        pip.initialize()
        pip.save()

        # load the saved pipeline
        pip2 = Pipeline(gui_mode=True)
        pip2.load(pipeline_object_path=test_data_path+os.sep+r'test_data/test_pipeline/test/pipeline__test.dill')

        # tests
        self.assertEqual(pip.pipeline_name,pip2.pipeline_name,'Pipeline test failed: \'pipeline_name\' changes before '
                                                              'and after saving!')
        self.assertEqual(pip.pipeline_folder_path,pip2.pipeline_folder_path,'Pipeline test failed: '
                                                                            '\'pipeline_folder_path\' changes before '
                                                                            'and after saving!')
        self.assertEqual(pip.plugins_list,pip2.plugins_list,'Pipeline test failed: \'plugins_list\' changes before '
                                                            'and after saving!')
        self.assertEqual(pip.pipeline.keys(), pip2.pipeline.keys(),'Pipeline test failed: \'pipeline\' dictionary '
                                                                   'changes before and after saving!')
        plugins_comparison = []
        for k in pip.pipeline.keys():

            r = (pickle.dumps(pip.pipeline[k]) != pickle.dumps(pip2.pipeline[k]))
            plugins_comparison.append(r)

        result_plugins_comparison = (np.sum(plugins_comparison) == 0)
        if not result_plugins_comparison:

            idx = plugins_comparison.index(True)

        else:

            idx = -1

        self.assertEqual(result_plugins_comparison,True,'Pipeline test failed: operation \'{}\' changes before and '
                                                        'after saving!'.format(list(pip.pipeline.keys())[idx]))

        # remove files created for the test
        os.remove(test_data_path+os.sep+r'test_data/test_pipeline/test/pipeline__test.dill')
        os.remove(test_data_path+os.sep+r'test_data/test_pipeline/test/pipeline__test.json')
        os.rmdir(test_data_path+os.sep+r'test_data/test_pipeline/test')

        print('...DONE!')

    def test_plugins_get_dictionary(self):

        print('\nRunning plugins dictionaries tests...')

        # import necessary modules
        from bmiptools.setting.installed_plugins import PLUGINS

        for k in PLUGINS.keys():

            # initialize a plugin
            Plugin = PLUGINS[k]
            initialized_plugin = Plugin(Plugin.empty_transformation_dictionary)

            # modify plugins parameters after initialization
            possible_keys = list(Plugin.empty_transformation_dictionary.keys())
            for k in possible_keys:

                if hasattr(initialized_plugin, k):

                    modified_key = k

            initialized_plugin.__setattr__(modified_key,7)
            # exec('initialized_plugin.{} = {}'.format(modified_key, 7))

            # define the reference dictionary
            reference_dict = copy.copy(Plugin.empty_transformation_dictionary)
            reference_dict[modified_key] = 7

            # test
            self.assertEqual(initialized_plugin.get_transformation_dictionary(),reference_dict,'Plugin dictionary test '
                                'failed: getting the modified transformation dictionary in plugin {} failed!'.format(k))
            reference_dict = None
            modified_key = None

        print('...DONE!')

    def test_cropper(self):

        # on the reference stack and save expected result as npy
        print('\nRunning cropper test...')

        # import necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.geometric.cropper import Cropper

        # load stack
        stack = Stack(path=test_data_path+os.sep+r'test_data/test_stack/stack',
                      from_folder=True,
                      load_metadata=False)

        # initialize and apply cropper
        td = Cropper.empty_transformation_dictionary
        td['y_range'] = [20,40]
        td['x_range'] = [20,40]
        cropper = Cropper(td)
        cropper.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep+r'test_data/test_cropper/cropper_result.npy'))
        self.assertEqual(test_result,True,'Cropper plugin test failed!')

        print('...DONE!')

    def test_standardizer(self):

        print('\nRunning standardizer test...')

        # import necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.dynamics.standardizer import Standardizer

        # load stack
        stack = Stack(path=test_data_path+os.sep+r'test_data/test_stack/stack',
                      from_folder=True,
                      load_metadata=False)

        # initialize and apply standardizer
        td = Standardizer.empty_transformation_dictionary
        standardizer = Standardizer(td)
        standardizer.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep+
                                                   r'test_data/test_standardizer/standardizer_result.npy'))
        self.assertEqual(test_result,True,'Standardizer plugin test failed!')

        print('...DONE!')

    def test_histogram_matcher(self):

        print('\nRunning Histogram matcher test...')

        # import necessary files
        from bmiptools.stack import Stack
        from bmiptools.transformation.dynamics.histogram_matcher import HistogramMatcher

        # load some slice of the test stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path+os.sep+r'test_data/test_stack/stack', S=[0,1,2])

        # initialize and apply histogram matcher
        td = HistogramMatcher.empty_transformation_dictionary
        histmatch = HistogramMatcher(td)
        histmatch.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep+
                                                   r'test_data/test_histogram_matcher/histogram_matcher_result.npy'))
        self.assertEqual(test_result,True,'Histogram Matcher plugin test failed!')
        print('...DONE!')

    def test_denoiser(self):

        print('\nRunning Denoiser test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.restoration.denoiser import Denoiser

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path+os.sep+r'test_data/test_stack/stack', S=[0])

        # initialize and apply denoiser
        td = Denoiser.empty_transformation_dictionary
        td['optimization_setting']['tested_filters_list'] = ['tv_chambolle']
        td['optimization_setting']['tv_chambolle']['tv_chambolle'] = {'weights_tvch_range': [1e-01, 1, 1]}
        td['optimization_setting']['opt_bounding_box']['use_bounding_box'] = False
        denoiser = Denoiser(td)
        denoiser.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep+
                                                   r'test_data/test_denoiser/denoiser_result.npy'))
        self.assertEqual(test_result,True,'Denoiser plugin test failed!')
        print('...DONE!')

    @unittest.skip('n2v does not allow to set a random seed easily: no exact reproducibly can be guaranteed')
    def test_denoiserdnn(self):

        print('\nRunning DenoiserDNN test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.restoration.denoiser import DenoiserDNN

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0,1])

        # initialize and apply denoiserDNN
        td = DenoiserDNN.empty_transformation_dictionary
        td['optimization_setting']['n2v_2d']['unet_kern_size_2d_list'] = [3]
        td['optimization_setting']['n2v_2d']['train_batch_size_2d_list'] = [1]
        td['optimization_setting']['n2v_2d']['n2v_patch_shape_2d_list'] = [32]
        td['optimization_setting']['n2v_2d']['train_epochs_2d_list'] = [1]
        td['optimization_setting']['n2v_2d']['train_loss_2d_list'] = ['mse']
        td['optimization_setting']['n2v_2d']['n2v_manipulator_2d_list'] = ['identity']
        td['optimization_setting']['n2v_2d']['n2v_neighborhood_radius_2d_list'] = [5]
        td['optimization_setting']['opt_bounding_box']['use_bounding_box'] = False
        td['optimization_setting']['fit_step'] = 1
        denoiserDNN = DenoiserDNN(td)
        denoiserDNN.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep +
                                                   r'test_data/test_denoiserdnn/denoiserdnn_result.npy'))
        self.assertEqual(test_result, True, 'DenoiserDNN plugin test failed!')
        print('...DONE!')

    def test_destriper(self):

        print('\nRunning Destriper test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.restoration.destriper import Destriper,SUPPORTED_WAVELET

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0,1])

        # initialize and apply destriper
        td = Destriper.empty_transformation_dictionary
        td['optimization_setting']['wavelet']['use_wavelet'] = SUPPORTED_WAVELET[0]
        td['optimization_setting']['sigma']['sigma_min'] = 49
        td['optimization_setting']['opt_bounding_box']['use_bounding_box'] = False
        td['optimization_setting']['fit_step'] = 1
        destriper = Destriper(td)
        destriper.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep +
                                                   r'test_data/test_destriper/destriper_result.npy'))
        self.assertEqual(test_result, True, 'Destriper plugin test failed!')
        print('...DONE!')

    def test_flatter(self):

        print('\nRunning Flatter test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.restoration.flatter import Flatter

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0,1])

        # initialize and apply flatter
        td = Flatter.empty_transformation_dictionary
        td['optimization_setting']['sigma_max'] = 6
        td['optimization_setting']['fit_step'] = 1
        flatter = Flatter(td)
        flatter.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep +
                                                   r'test_data/test_flatter/flatter_result.npy'))
        self.assertEqual(test_result, True, 'Flatter plugin test failed!')
        print('...DONE!')

    def test_decharger(self):

        print('\nRunning Decharger test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.restoration.decharger import Decharger

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0,1])

        # initialize and apply flatter
        td = Decharger.empty_transformation_dictionary
        td['auto_optimize'] = False
        td['decharger_type'] = 'global_GF2RBGF'
        decharger = Decharger(td)
        decharger.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path+os.sep +
                                                   r'test_data/test_decharger/decharger_result.npy'))
        self.assertEqual(test_result, True, 'Decharger plugin test failed!')
        print('...DONE!')

    def test_registrator(self):

        print('\nRunning Registrator test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.alignment.registrator import Registrator

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0, 1])

        # initialize and apply flatter
        td = Registrator.empty_transformation_dictionary
        td['opt_bounding_box']['use_bounding_box'] = False
        registrator = Registrator(td)
        registrator.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path + os.sep +
                                                   r'test_data/test_registrator/registrator_result.npy'))
        self.assertEqual(test_result, True, 'Registrator plugin test failed!')
        print('...DONE!')

    def test_affine(self):

        print('\nRunning Affine test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.geometric.affine import Affine

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0, 1])

        # initialize and apply flatter
        td = Affine.empty_transformation_dictionary
        td['translation']['translation_vector'] = [10, 10, 0]
        affine = Affine(td)
        affine.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path + os.sep +
                                                   r'test_data/test_affine/affine_result.npy'))
        self.assertEqual(test_result, True, 'Affine plugin test failed!')
        print('...DONE!')

    def test_equalizer(self):

        print('\nRunning Equalizer test...')

        # import the necessary modules
        from bmiptools.stack import Stack
        from bmiptools.transformation.dynamics.equalizer import Equalizer

        # load stack
        stack = Stack()
        stack.load_slices_from_folder(path=test_data_path + os.sep + r'test_data/test_stack/stack', S=[0, 1])

        # initialize and apply flatter
        td = Equalizer.empty_transformation_dictionary
        equalizer = Equalizer(td)
        equalizer.transform(stack)

        # test
        test_result = np.all(stack.data == np.load(test_data_path + os.sep +
                                                   r'test_data/test_equalizer/equalizer_result.npy'))
        self.assertEqual(test_result, True, 'Affine plugin test failed!')
        print('...DONE!')


############
#####   MAIN
############


if __name__ == '__main__':

    unittest.main()