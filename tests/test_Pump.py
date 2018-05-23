from chemios.pumps import Chemyx, HarvardApparatus, NewEra
import time
import json
import pytest
import re
import collections



def import_module(name):
    '''Import a module from a string'''
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod 

def compare(s, t):
    '''Compare two lists that are unorderable and unhasable
    Yields True if the lists are the same
    '''
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t
    


  
