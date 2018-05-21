import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "chemios",
    version = "0.0.1",
    author = "Chemios",
    author_email = "hello@chemios.io",
    description = ("Chemios Framework: Automatically control all your laboratory equipment through one easy-to-use interface"),
    packages = find_packages(exclude=['tests']),
    package_data = {'chemios': ['chemios/data/*.json']},
    install_requires = ['arrow', 'numpy', 'pandas', 'minimalmodbus', 'tinydb'],
    long_description_content_type = ' text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
