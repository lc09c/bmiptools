==========================
Contribute or Issue report
==========================


.. role:: raw-html(raw)
   :format: html

The source code of bmiptools and this documentation, and may examples code can be found on the MPIKG GitLab at this
address:

* https://gitlab.mpikg.mpg.de/curcuraci/bmiptools .

For questions about bmiptools not addressed in
this documentation, one can  :raw-html:`<a href= "mailto:Luca.Curcuraci@mpikg.mpg.de">send an email</a>`. An answer
will be delivered maybe time permitting as soon as possilble.


Issue request
=============


To signal bugs, unexpected behavior of bmiptool, or simply ask for a feature request open an `issue request on GitLab
repository <https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/issues/new>`_ of the bmiptools library. As general rule,
for bugs or unexpected behavior it is important to attach a code snapshot able to reproduce the bug, or a detailed
description of all the operations executed with the GUI (possibly with a minimal amount of input data), so that one
can reproduce the issue. If these conditions are not met, it is difficult to have a positive end for the issue request.


Integrate custom plugins
========================


To integrate custom plugins or new functionalities in bmiptools, create a new branch on the MPIKG GitLab and update
the custom features there. For new plugins, it is always a good idea to install them locally and perform all the tests
locally on the developer machine. As series of unit test are available `here <https://gitlab.mpikg.mpg.de/curcuraci/
bmiptools/-/tree/master/test>`_ to test further compatibility. Once a final version of the custom plugin is available,
ask for a merge of the branch to the repository administrator.


To do list
==========


The following list contains possible direction of improvements:

* Implement better optimization strategies. Optimization for all the plugins is done by using simple grid search, and
  this is sufficient ot get nice results in a reasonable amount of time. By the way more clever optimization methods may
  reduce the optimization time. A good and not too complicated idea can be to use bayesian optimization, since it is
  able to deal with continuous, discrete and categorical parameter type during the optimization.

* Multichannel implementation for all the plugins: Registrator, and DenoiseDNN are still single channel. DenoiseDNN can
  be particularly different with respect to the usual bmiptool procedure to implement a multichannel plugin.

* Implement cycle spin for wavelet denoising.

* Add BM3D denoiser algorithm.

* It should be checked if Noise2Same, rather than Noise2Self, gives rise to better self supervised parameter selection
  for a denoiser (see
  `here <https://proceedings.neurips.cc/paper/2020/file/ea6b2efbdd4255a9f1b3bbc6399b58f4-Paper.pdf>`_)