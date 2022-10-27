# Title: 'gpu_utils.py'
# Author: Curcuraci Luca
# Date:
#
# Scope: utility function for operations on gpu

"""
Work in progress...
"""

# #################
# #####   LIBRARIES
# #################
#
#
# import numpy as np
# import cupy as cp
#
#
# # TODO: Comment these functions!!!!
#
#
# #################
# #####   FUNCTIONS
# #################
#
#
# def memory_conversion_factor(data):
#     """
#
#     :param data:
#     :return:
#     """
#     if data.dtype==np.uint8:
#
#         return 64//8
#
#     elif data.dtype==np.uint16:
#
#         return 64//16
#
#     elif data.dtype == np.uint32:
#
#         return 64//32
#
#     elif data.dtype == np.float32:
#
#         return 64//32
#
#     else:
#
#         return 1
#
# def compute_n_gpu_batches(data, gpu_device=cp.cuda.Device(), buffer_fraction=0.3333):
#     """
#
#     :param data:
#     :param gpu_device:
#     :param buffer_fraction:
#     :return:
#     """
#     cf = memory_conversion_factor(data)
#     gpu_memory = int(gpu_device.mem_info[0] * buffer_fraction)
#     n_batches = int(np.ceil(data.nbytes*cf / gpu_memory))
#     batch_size = len(data) // n_batches
#     if n_batches * batch_size != data.shape[0]:
#
#         return n_batches + 1, batch_size
#
#     return n_batches, batch_size
#
# def gpu_batcher(data, gpu_device=cp.cuda.Device()):
#     """
#
#     :param data:
#     :param gpu_device:
#     :return:
#     """
#     n_batch, batch_size = compute_n_gpu_batches(data, gpu_device)
#     batch_num = 0
#     while True:
#
#         yield cp.array(data[batch_num*batch_size:(batch_num+1)*batch_size,...])
#         batch_num += 1
#         if batch_num == n_batch:
#
#             break
#
# def remove_from_gpu(variable, mempool=None, pinned_mempool=None):
#     """
#
#     :param variable:
#     :param mempool:
#     :param pinned_mempool:
#     :return:
#     """
#     if mempool == None:
#
#         mempool = cp.get_default_memory_pool()
#
#     if pinned_mempool == None:
#
#         pinned_mempool = cp.get_default_pinned_memory_pool()
#
#     variable = None
#     mempool.free_all_blocks()
#     pinned_mempool.free_all_blocks()
#
# def vectorize_on_gpu(data, function, gpu_device=cp.cuda.Device()):
#     """
#
#     :param data:
#     :param function:
#     :param gpu_device:
#     :return:
#     """
#     res = []
#     for gpu_batch in gpu_batcher(data,gpu_device):
#
#         res.append(function(gpu_batch))
#         remove_from_gpu(gpu_batch)
#
#     return np.vstack(res)




