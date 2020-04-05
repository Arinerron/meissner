#!/usr/bin/env python

import setuptools
from setuptools import find_namespace_packages
from distutils.core import setup

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(name = 'meissner',
      version = '1.0.2',
      description = 'a dictionary-based XSS mutation fuzzer',
      long_description = readme(),
      long_description_content_type="text/markdown",
      author = 'Aaron Esau',
      author_email = 'python@aaronesau.com',
      url = 'https://github.com/Arinerron/meissner',
      keywords = 'ctf xss hacking mutation fuzzer fuzzing fuzz dictionary attack attacking injection scripting',
      packages = ['meissner'] + find_namespace_packages(include=['meissner.*']),
      scripts = [
        'scripts/meissner'
      ],
      install_requires=open('requirements.txt', 'r').read().strip().split('\n'),
      package_data={'meissner': ['dictionary/*.txt']},
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.6'),
