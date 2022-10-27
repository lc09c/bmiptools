==============
API References
==============


The full bmitools repository is available at

* https://gitlab.mpikg.mpg.de/curcuraci/bmiptools

Here below, most of the bmiptools objects are listed.

.. autosummary::

    :toctree: generated
    :template: module.rst
    :recursive:


    bmiptools.stack
    bmiptools.pipeline

    bmiptools.setting.installed_plugins
    bmiptools.setting.configure

    bmiptools.core.base
    bmiptools.core.gpu_utils
    bmiptools.core.ip_utils
    bmiptools.core.math_utils
    bmiptools.core.utils

    bmiptools.gui.bmiptools_gui
    bmiptools.gui.gui_basic

    bmiptools.transformation.base

    bmiptools.transformation.alignment.registrator

    bmiptools.transformation.basic.filters

    bmiptools.transformation.dynamics.standardizer
    bmiptools.transformation.dynamics.histogram_matcher
    bmiptools.transformation.dynamics.equalizer

    bmiptools.transformation.geometric.cropper
    bmiptools.transformation.geometric.geometric_tools
    bmiptools.transformation.geometric.affine

    bmiptools.transformation.restoration._restoration_shared
    bmiptools.transformation.restoration.decharger
    bmiptools.transformation.restoration.denoiser
    bmiptools.transformation.restoration.destriper
    bmiptools.transformation.restoration.flatter

    bmiptools.visualization.geometric.change_coordinate_system

    bmiptools.visualization.graphic_tools.basic_graphic_tools
