============
Introduction
============


bmiptools is a Python library equipped with a basic graphical interface useful for the processing of images, typically
produced in some biological context (FIB-SEM and cryo FIB-SEM in particular).


Scope
=====


The goals of this library are the following:


1. **Open code implementation of various image processing transformations**. Ideally the user should have access to the
   actual implementation of any tool is using, so that everything can be checked at low level if needed.

2. **Open documentation of various image processing transformations**. The user should have access to a documentation
   explaining the rationale behind the method implemented and how this was implemented in the code.

3. **User friendly interfaces**. The user should be able to use this Python library even with minimal experience
   with Python. Alternatively, non expert users should be able to use the majority of the library functionalities with a
   simple GUI.

4. **Objective parameter selection to reduce human bias in the pre-processing**. The user should specify just the
   parameters ranges rather than the parameters values. The best parameters are later selected, in automatic manner,
   according to reasonable objective criteria.

5. **Parameter tracking in a human understandable manner**. The user should be able to collect all the parameters describing
   a series of transformations, and they need to be stored in an ordered and a human understandable way.

6. **Easy result reproducibility**. Anyone should be able to reproduce the result of some post-processing pipeline on its
   computer with minimal efforts.

7. **Metadata management**. Metadata do not have to get lost during the post-processing.

8. **Open to external contribution**. The user with a minimum of coding experience should be able to implement their own
   custom extension integrable in bmiptools with minimal efforts.


Repository
==========


The bmitools repository is available on the mpikg gitlab, in particular at

* https://gitlab.mpikg.mpg.de/curcuraci/bmiptools


How to cite this tool?
======================


Bmiptools is released under the Apache 2.0 License. It can be freely used by anyone for whatever scope, provided that
credits are recognized somewhere. Bmiptools can be cited as reported below...


    "bmiptools - BioMaterials Image Processing TOOLS" - The monochromatic bmiptools team - Patagonian temple for the
    Russell's teapot of the Flying Spaghetti Monster on Ceres, Asteroids belt, June 2022.


..but, those how do not have enough sense of humor and take themself too seriously can alternatively use


    "bmiptools - BioMaterials Image Processing TOOLS" -  - June 2022.