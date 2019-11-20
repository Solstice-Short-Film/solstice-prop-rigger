#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class to create prop rigs
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Enrique Velasco"
__email__ = "enriquevelmai@hotmail.com"

from . import rig


class PropRig(rig.AssetRig):
    """
    Class to create prop/background elements rigs
    """

    def __init__(self,
                 asset_name,
                 import_scenes=True,
                 model_grp=None,
                 proxy_grp=None,
                 builder_grp=None
                 ):
        super(PropRig, self).__init__(asset_name=asset_name, import_scenes=import_scenes, model_grp=model_grp, proxy_grp=proxy_grp, builder_grp=builder_grp)
