# -*- coding: utf-8 -*-
# *****************************************************************************
# Copyright (c) 2017 by the ndatautils contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Lukas Beddrich <lukas.beddrich@frm2.tum.de>
#
# *****************************************************************************
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