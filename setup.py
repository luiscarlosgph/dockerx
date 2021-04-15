#!/usr/bin/env python

import setuptools
import unittest

setuptools.setup(name='dockerx',
    version='0.3.0',
    description='Launcher of Docker containers.',
    author='Luis C. Garcia-Peraza Herrera',
    author_email='luiscarlos.gph@gmail.com',
    license='MIT',
    url='https://github.com/luiscarlosgph/docker-with-graphics',
    packages=['dockerx'],
    package_dir={'dockerx' : 'src/dockerx'}, 
    install_requires=[
        'argparse',
        'docker',
    ],
)
