import setuptools
import os

with open('README.md','r') as readme:

    long_description = readme.read()

with open(os.path.dirname(os.path.abspath(__file__))+os.sep+'requirements.txt') as reqfile:

    requirements = reqfile.read().splitlines()

setuptools.setup(
    name='bmiptools',
    version='1.0.1',
    author='Luca Curcuraci',
    author_email='Luca.Curcuraci@mpikg.mpg.de',
    description = 'BioMaterial Image Processing tools (bmiptools) is a python library of functions for image '
                  'processing of certain type of biological images (e.g. FIB-SEM, Back-scattering, ecc... ). '
                  'The library is equipped with a minimal GUI thought for non-expert users.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url='https://gitlab.mpikg.mpg.de/curcuraci/bmiptools',
    project_urls={'Bug tracker': 'https://gitlab.mpikg.mpg.de/curcuraci/bmiptools/-/issues/new',
                  'Documentation': 'https://bmiptools.readthedocs.io/en/latest/'},
    classifiers=['Programming Language :: Python :: 3.8',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: OS Independent',
                 'Topic :: Scientific/Engineering :: Image Processing',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Software Development :: User Interfaces',
                 'Intended Audience :: Science/Research'],
    package_dir={'': 'src'},
    package_data={'':['*.txt']},
    packages=setuptools.find_packages(where='src'),
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.8',
)
