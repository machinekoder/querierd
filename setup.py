#!/usr/bin/env python

from setuptools import setup

setup(name='querierd',
      version=0.1,
      description='IGMP querier service',
      author='Marc Culler',
      author_email='marc.culler@gmail.com',
      url='http://www.math.uic.edu/~t3m',
      packages=['querier'],
      install_requires=['netifaces>0.7']
     )
