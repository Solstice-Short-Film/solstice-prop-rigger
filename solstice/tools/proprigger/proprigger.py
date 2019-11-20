#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allows to import/export XGen data
"""

from __future__ import print_function, division, absolute_import

# from artellapipe.shadermanager.widgets import shaderexporter

__author__ = "Enrique Velasco"
__license__ = "MIT"
__maintainer__ = "Enrique Velasco"
__email__ = "enriquevelmai@hotmail.com"

import os
import json
import stat
import shutil
import logging
from functools import partial

from Qt.QtWidgets import *

import tpDccLib as tp

import artellapipe
from artellapipe.libs import artella
from artellapipe.utils import resource

if tp.is_maya():
    import maya.cmds as mc
    import xgenm as xg
    import xgenm.XgExternalAPI as xge
    import xgenm.xgGlobal as xgg

LOGGER = logging.getLogger()


########################################################################################################################
# class definition
########################################################################################################################
class ControlXgenUi(QWidget, object):

    ####################################################################################################################
    # class constructor
    ####################################################################################################################
    def __init__(self, project, parent=None):
        self.shaders_dict = dict()
        self.scalps_list = list()
        self.collection_name = None
        self._project = project
        super(ControlXgenUi, self).__init__(parent=parent)

        self.ui()

    ####################################################################################################################
    # ui definitions
    ####################################################################################################################
    def ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.ui = resource.ResourceManager().gui('proprigger')
        if not self.ui:
            LOGGER.error('Error while loading Prop Rigger UI ...')
            return

        self.main_layout.addWidget(self.ui)

        self._populate_data()
        self._connect_componets_to_actions()

    def _populate_data(self):
        pass

    def _connect_componets_to_actions(self):
        pass


class PropRigger(artellapipe.Tool, object):
    def __init__(self, project, config):
        super(PropRigger, self).__init__(project=project, config=config)

    def ui(self):
        super(PropRigger, self).ui()

        self._xgen_ui = ControlXgenUi(project=self._project)
        self.main_layout.addWidget(self._xgen_ui)
