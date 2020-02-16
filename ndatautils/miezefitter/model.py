# -*- coding: utf-8 -*-
"""
The model module for fitting MIEZE-S(q,t) data sets

Model class defines a structure to implement different physical 
models to fit (MIEZE) datasets.
Various functionality to save and load previous models will be included
"""

class Model:
    """
    The `Model´ class is the core structure to build fit models
    """

    def init(self, name, func=None, mparams=None, shape=None, *args, **kwargs):
        """
        
        """
        self.name = name
        self.func = func
        self.shape = shape
        self.mparams = mparams
        self.args = args
        self.kwargs = kwargs
#-----------------------------------------------------------------------

if __name__ == "__main__":
    print("Model was loaded as script")
else:
    print("Model was loaded as module")