# Title: 'basic_graphic_tools.py'
# Author: Curcuraci L.
# Date: 01/02/2021
#
# Scope: Basic visualization tools for a stack object or slices of it.
#
# Upgrade
#
# 3D: https://stackoverflow.com/questions/56035562/3d-dicom-visualisation-in-python
#     https://vedo.embl.es

"""
Basic visualization tools for a stack object or slices of it.
"""

#################
#####   LIBRARIES
#################


import numpy as np
import napari
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import cm
from skimage.filters import gaussian


#################
#####   FUNCTIONS
#################

class Basic2D:
    """
    Collection of 2D basic visualization methods
    """

    @staticmethod
    def show_image(image, title=None, cmap='Greys_r', show_colorbar=False, legend=None, ticks=None):
        """
        Plot a 2d image.

        :param image: 2d numpy array containing the image.
        :param title: (optional) the title of the image.
        :param cmap: (optional) colormap name.
        :param show_colorbar: (boolean) if True the colorbar will be shown.
        :param legend: (dictionary) dictionary with two keys: 'colors' and 'labels'. In 'colors' one should write a
                       list of RGB value for the various marked present in the legend, while in 'labels' one should
                       write a list of the string associated to a give marker. As reference, consider the example
                       below

                                legend = {'colors': [(0.1,0.9,0.7),(0.5,0.8,0.1)]
                                          'labels': ['sample 1', 'sample_2']}

                       If nothing is given, no legend is plotted.
        :param ticks: (dictionary) dictionary with at most two keys (one for axis). In each keys there should be a list
                      containing the name of each thinks in the corresponding axis. The axis are labeled as usual with
                      natural numbers. As reference consider the example below, for a 3x3 image one may have  a ticks
                      dictionary of this kind

                                ticks = {0: ['A','B','C'],
                                         1: [1,'D',3]}

                      which would place the labels 'A','B' and 'C' along the 0 axis, replaing the number present there
                      by default, and similaru for the 1 axis.
        """
        fig, ax = plt.subplots()
        ax.set_title(title)
        plotted = ax.imshow(image, cmap=cmap)
        if show_colorbar:
            fig.colorbar(plotted, ax=ax)

        if legend is not None:
            legend_elements = [Line2D([0], [0], marker='o', label=lab, color=col, markersize=5, linewidth=0)
                               for lab, col in zip(legend['labels'], legend['colors'])]
            ax.legend(handles=legend_elements, loc='upper right')

        if ticks is not None:

            if 0 in ticks.keys():
                assert len(ticks[0]) == image.shape[
                    0], 'The number of ticks labels in {} axis have to be compatible with ' \
                        'the image shape: {} != {}'.format(0, len(ticks[0]), image.shape[0])

                ax.set_xticks(np.arange(image.shape[0]))
                ax.set_xticklabels(ticks[0])
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

            if 1 in ticks.keys():
                assert len(ticks[1]) == image.shape[
                    1], 'The number of ticks labels in {} axis have to be compatible with ' \
                        'the image shape: {} != {}'.format(1, len(ticks[1]), image.shape[1])
                ax.set_yticks(np.arange(image.shape[1]))
                ax.set_yticklabels(ticks[1])

        plt.show()

    @staticmethod
    def compare_images(A, B, title_A=None, title_B=None,colormap='viridis'):
        """
        Compare two images plotting them one next to the other.

        :param A: numpy array containing the first image.
        :param B: numpy array containing the second image.
        :param title_A: (optional) title of the first image.
        :param title_B: (optional) title of the second image.
        :param colormap: (optional) colormap used in both images.
        """
        f, axarr = plt.subplots(ncols=2)
        axarr[0].set_title(title_A)
        axarr[0].imshow(A,colormap)
        axarr[1].set_title(title_B)
        axarr[1].imshow(B,colormap)
        plt.show()

    @staticmethod
    def plot_image_as_surface(image,colormap='viridis',smooth_surface=0.0,colormask = None):
        """
        Plot a 2D image as a surface in a 3D space.

        :param image: numpy array containing the 2D image.
        :param colormap: name of the colormap (according to the matplotlib convention).
        :param smooth_surface: variance of the gaussian filter used to smooth the image (if 0 no smoothing is done).
        :param colormask: (optional) 2D numpy array (having the same shape of 'image') containing the value of the color to
                          be used.
        """

        xx = range(image.shape[0])
        yy = range(image.shape[1])
        if colormask is not None:

            assert colormask.shape == image.shape, 'Only grayscale colormask are supported'
            hf = plt.figure()
            ha = hf.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(xx,yy)  # `plot_surface` expects `x` and `y` data to be 2D
            std_colormask = (colormask-np.min(colormask))/(np.max(colormask)-np.min(colormask))
            ha.plot_surface(X.T,Y.T,gaussian(image,smooth_surface,preserve_range=True),facecolors=cm.get_cmap(colormap)(std_colormask))
            plt.show()

        else:

            hf = plt.figure()
            ha = hf.add_subplot(111, projection='3d')
            X, Y = np.meshgrid(xx,yy)  # `plot_surface` expects `x` and `y` data to be 2D
            ha.plot_surface(X.T,Y.T,gaussian(image,smooth_surface,preserve_range=True),cmap=cm.get_cmap(colormap))
            plt.show()

    @staticmethod
    def show_threshold_on_image(image, mask, title=None, alpha=0.4, cmap_img='Greys',
                                cmap_condition='Oranges'):
        """
        Plot an image with a mask superimposed on it.

        :param image: numpy array containing the image.
        :param mask: numpy array containing the mask to be superimposed on the image.
        :param title: (optional) title of the graph.
        :param alpha: (optional) parameter regulating the degree of superposition between the image an the mask
                      (0 = only image, 1 = only mask).
        :param cmap_img: (optional) colormap name of the image.
        :param cmap_condition: (optional) colormap name of the mask.
        """
        plt.figure()
        plt.title(title)
        plt.imshow(image, cmap_img)
        plt.imshow(mask, cmap_condition, alpha=alpha)
        plt.show()

class Basic3D:
    """
    Collection of 3D basic visualization methods
    """

    @staticmethod
    def plot_3d_binary_mask(mask,title='',alpha=0.5,size=50,limits=None,legend=None):
        """
        Plot a 3d binary mask in a scatter plot.

        :param mask: (ndarray) 3D numpy array containing a 0-1 mask.
        :param title: (optional) graph title.
        :param alpha: (optional) point color saturation.
        :param size: (optional) point size.
        :param limits: (optional) extrema of the axis of the plot, with format ((zmin,zmax),(ymin,ymax),(xmin,xmax)).
        """
        if limits is None:

            mask_shape = mask.shape
            limits = ((0,mask_shape[0]),(0,mask_shape[1]),(0,mask_shape[2]))

        cp = np.vstack(np.where(mask == 1)).T
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        ax.set_title('{}'.format(title))
        ax.scatter(cp[:,0],cp[:,1],cp[:,2],alpha=alpha,s=size,linewidth=0)
        ax.set_xlim(*limits[2])
        ax.set_ylim(*limits[1])
        ax.set_zlim(*limits[0])
        if legend is not None:

            legend_elements = [Line2D([0], [0], marker='o', label=lab, color=col, markersize=5, linewidth=0)
                               for lab, col in zip(legend['labels'], legend['colors'])]
            ax.legend(handles=legend_elements, loc='upper right')

        plt.show()

    @staticmethod
    def plot_3d_points(x,title='',colors=None,alpha=0.5,size=50,limits=((None,None),(None,None),(None,None)),legend=None):
        """
        Plot a 3d points in a scatter plot.

        :param x: (ndarray) numpy array with a collection of 3d coordinates to plot.
        :param title: (optional) graph title.
        :param colors: (optional) color of the point (single graylevel/rgb value or list of graylevel/rgb values for
                       each point in x).
        :param alpha: (optional) point color saturation.
        :param size: (optional) point size.
        :param limits: (optional) extrema of the axis of the plot, with format ((zmin,zmax),(ymin,ymax),(xmin,xmax));
        :param legend: (dictionary) dictionary with two keys: 'colors' and 'labels'. In 'colors' one should write a
                       list of RGB value for the various marked present in the legend, while in 'labels' one should
                       write a list of the string associated to a give marker. As reference, consider the example
                       below

                                legend = {'colors': [(0.1,0.9,0.7),(0.5,0.8,0.1)]
                                          'labels': ['sample 1', 'sample_2']}

                       If nothing is given, no legend is plotted.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('{}'.format(title))
        ax.scatter(x[:,0], x[:,1], x[:,2],c=colors,alpha=alpha,s=size,linewidth=0)
        ax.set_zlim(*limits[2])
        ax.set_ylim(*limits[1])
        ax.set_xlim(*limits[0])
        if legend is not None:

            legend_elements = [Line2D([0], [0], marker='o', label=lab, color=col, markersize=5, linewidth=0)
                               for lab, col in zip(legend['labels'], legend['colors'])]
            ax.legend(handles=legend_elements, loc='upper right')

        plt.show()

    @staticmethod
    def show_stack(x,channels_as_rgb=False,channel_to_plot= None):
        """
        3d plot of a stack via Napari. Consider possible RAM issue for very large stacks.

        :param x: (Stack or numpy array) Object to be plotted.
        :param channels_as_rgb: (bool) If True the channels of the image will be interpreted as RGB channels provided
                                they are 3 (otherwise all channes are summed and the resulting Gray-level image is
                                plotted).
        :param channel_to_plot: (int) If not None, this is che channel of the image which is plotted.
        """
        to_plot = x
        if hasattr(x,'data'):

            to_plot = x.data

        if channel_to_plot != None:

            to_plot = to_plot[...,channel_to_plot]

        rgb = False
        if channels_as_rgb:

            if hasattr(x,'n_channes'):

                if x.n_channes == 3:

                    rgb = True

                else:

                    to_plot = to_plot.sum(-1)

            else:

                if x.shape[-1] == 3:

                    rgb = True

                else:

                    to_plot = to_plot.sum(-1)

        viewer = napari.view_image(to_plot,rgb = rgb)
        viewer.run()