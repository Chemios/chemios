import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "chemiosbrain",
    version = "0.0.1",
    author = "Chemios",
    author_email = "hello@chemios.io",
    description = ("The Chemios Brain is a raspberry pi running python code that controls our reactors."),
    packages = find_packages(exclude=['manuals', 'prototype', 'startup-scripts', 'tests', 'microcontroller']),
    install_requires = ['arrow', 'numpy', 'pandas', 'minimalmodbus'],
    long_description_content_type = ' text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
