# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 24-Oct-2021
#
#  @author: tbowers

"""Utility Functions and Variables

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This module contains various utility routines and global variables from across
the package.

.. include common links, assuming primary doc root is up one directory
.. include:: ../include/links.rst
"""

# Built-In Libraries
import pathlib

# 3rd Party Libraries
from pkg_resources import resource_filename

# Lowell Libraries

# Internal Imports


# Classes to hold useful information
class Paths:
    """Class that holds the various paths needed"""

    # Main data & config directories
    config = pathlib.Path(resource_filename("lorax", "config"))
    data = pathlib.Path(resource_filename("lorax", "data"))
    agents = pathlib.Path(resource_filename("lorax", "."))
