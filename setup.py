#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
import unittest

# Read the contents of the README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='dockerx',
    version='0.7.0',
    description='Launcher of Docker containers.',
    author='Luis C. Garcia-Peraza Herrera',
    author_email='luiscarlos.gph@gmail.com',
    license='MIT',
    url='https://github.com/luiscarlosgph/docker-with-graphics',
    packages=['dockerx'],
    package_dir={'dockerx' : 'src'}, 
    install_requires=[
        'argparse',
        'docker',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
