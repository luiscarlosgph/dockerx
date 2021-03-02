#!/usr/bin/env python

import setuptools
import unittest

setuptools.setup(name='dockerl',
    version='0.1.0',
    description='Launcher of Docker containers.',
    author='Luis C. Garcia-Peraza Herrera',
    author_email='luiscarlos.gph@gmail.com',
    license='MIT',
    url='https://github.com/luiscarlosgph/docker-with-graphics',
    packages=['dockerl'],
    package_dir={'dockerl' : 'src/dockerl'}, 
)
