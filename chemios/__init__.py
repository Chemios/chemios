
#Import components subpackage
from .components import *

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


# def get_classes(filename):
#     mod = importlib.import_module(filename)
#     classes = []
#     for name, obj in inspect.getmembers(mod):
#         if inspect.isclass(obj):
#             classes.append(name)



# #Import modules to the package level
# #i.e., I want able to import components as such: from chemios.components.pumps import HaPhdUltra
# directories = ['_components', '_devices']
# for directory in directories:
#     os.chdir(directory)
#     subdirectories = os.listdir()
#     #Look through subdirectory
#     for subdirectory in subdirectories:
#         output = re.search(r'^[^_]*_[^_]*$', subdirectory, re.M)
#         #only look at the component subdirectories starting with underscores
#         if output:
#             os.chdir(subdirectory)
#             filenames = os.listdir()
#             for filename in filenames:
#                 #Get only filenames that start with an underscore
#                 output = re.search(r'^[^_]*_[^_]*$', filename, re.M)
#                 if output:
#                     #Import classes
#                     filename = __import__(filename)
#             os.chdir('../')

    