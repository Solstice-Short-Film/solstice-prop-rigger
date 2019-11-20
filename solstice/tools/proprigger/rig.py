#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base class to create prop rigs
"""

from __future__ import print_function, division, absolute_import


__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import json
import math

from . import control
from . import utils

import maya.cmds as mc
import tpDccLib as tp
from tpMayaLib.core import scene
from artellapipe.core import asset

class AssetRig(object):
    """
    Base class to create asset rigs
    """

    def __init__(self,
                 asset_name,
                 import_scenes=True,
                 model_grp=None,
                 proxy_grp=None,
                 builder_grp=None
                 ):
        super(AssetRig, self).__init__()

        self._main_grp = None
        self._rig_grp = None
        self._proxy_grp = None
        self._hires_grp = None
        self._ctrl_grp = None
        self._extra_grp = None
        self._joint_proxy_grp = None
        self._mesh_proxy_grp = None
        self._proxy_asset_grp = None
        self._joint_hires_grp = None
        self._mesh_hires_grp = None
        self._hires_asset_grp = None

        self._root_ctrl = None
        self._main_ctrl = None

        self._geo = dict()
        self._builder_grp = None
        self._builder_locators = list()
        self._main_constraints = list()

        # map in utilities
        self._asset_name = asset_name
        self._import_scenes = import_scenes
        self._in_model_grp = model_grp
        self._in_proxy_grp = proxy_grp
        self._in_builder_grp = builder_grp

    def build(self, force_new=True):
        """
        Main function to build the rig
        """

        if self._import_scenes:
            mc.file(force=force_new, new=True)

        print('Building rig for asset {}'.format(self._asset_name))

        self.create_main_groups()

        if self._import_scenes:
            self.import_model()
            self.import_proxy()
            self.import_builder()
        else:
            self._generate_input_data_structure()

        self.create_main_controls()
        self.create_main_attributes()
        self.connect_main_controls()

        self.clean_model_group()
        self.clean_proxy_group()

        self.setup()

        self.finish()

        mc.select(mc.ls())
        mc.viewFit(animate=True)
        mc.select(clear=True)

    def create_main_groups(self):
        """
        Function that creates main rig groups
        """

        self._main_grp = mc.group(name=self._asset_name, empty=True, world=True)
        self._rig_grp = mc.group(name='rig', empty=True, parent=self._main_grp)
        self._proxy_grp = mc.group(name='proxy', empty=True, parent=self._main_grp)
        self._hires_grp = mc.group(name='hires', empty=True, parent=self._main_grp)
        self._ctrl_grp = mc.group(name='control_grp', empty=True, parent=self._rig_grp)
        self._extra_grp = mc.group(name='extra_grp', empty=True, parent=self._rig_grp)
        self._joint_proxy_grp = mc.group(name='joint_proxy', empty=True, parent=self._proxy_grp)
        self._mesh_proxy_grp = mc.group(name='mesh_proxy', empty=True, parent=self._proxy_grp)
        self._proxy_asset_grp = mc.group(name='{}_proxy_grp'.format(self._main_grp), empty=True,
                                         parent=self._mesh_proxy_grp)
        self._joint_hires_grp = mc.group(name='joint_hires', empty=True, parent=self._hires_grp)
        self._mesh_hires_grp = mc.group(name='mesh_hires', empty=True, parent=self._hires_grp)
        self._hires_asset_grp = mc.group(name='{}_hires_grp'.format(self._main_grp), empty=True,
                                         parent=self._mesh_hires_grp)

    def create_main_controls(self):
        """
        Function that creates main rig controls
        """

        xmin, ymin, zmin, xmax, ymax, zmax = mc.exactWorldBoundingBox(self._geo['model'])
        a = [xmin, 0, 0]
        b = [xmax, 0, 0]
        radius = (math.sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2) + pow(a[2] - b[2], 2)))

        self._root_ctrl = control.Circle('root', normal=[0, 1, 0], radius=radius, color_index=29)
        self._main_ctrl = control.Circle('main', normal=[0, 1, 0], radius=radius - 6, color_index=16)
        self._main_ctrl.translate_control_shapes(0, 1, 0)

        mc.addAttr(self._main_grp, ln='root_ctrl', at='message')
        mc.addAttr(self._main_grp, ln='main_ctrl', at='message')
        mc.setAttr(self._main_grp + '.root_ctrl', lock=False)
        mc.setAttr(self._main_grp + '.main_ctrl', lock=False)
        mc.connectAttr(self._root_ctrl.node + '.message', self._main_grp + '.root_ctrl')
        mc.connectAttr(self._main_ctrl.node + '.message', self._main_grp + '.main_ctrl')

    def create_main_attributes(self):
        """
        Function that create main rig attributes
        """

        assert self._main_grp and mc.objExists(self._main_grp)

        mc.addAttr(self._main_grp, ln='type', at='enum', en='proxy:hires:both')
        mc.setAttr('{}.type'.format(self._main_grp), edit=True, keyable=False)
        mc.setAttr('{}.type'.format(self._main_grp), edit=True, channelBox=False)
        mc.setAttr('{}.type'.format(self._main_grp), 0)
        mc.setAttr('{}.visibility'.format(self._proxy_grp), True)
        mc.setAttr('{}.visibility'.format(self._hires_grp), False)
        mc.setDrivenKeyframe(self._proxy_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        mc.setDrivenKeyframe(self._hires_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        mc.setAttr('{}.type'.format(self._main_grp), 1)
        mc.setAttr('{}.visibility'.format(self._proxy_grp), False)
        mc.setAttr('{}.visibility'.format(self._hires_grp), True)
        mc.setDrivenKeyframe(self._proxy_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        mc.setDrivenKeyframe(self._hires_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        mc.setAttr('{}.type'.format(self._main_grp), 2)
        mc.setAttr('{}.visibility'.format(self._proxy_grp), True)
        mc.setAttr('{}.visibility'.format(self._hires_grp), True)
        mc.setDrivenKeyframe(self._proxy_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        mc.setDrivenKeyframe(self._hires_grp + '.visibility', currentDriver='{}.type'.format(self._main_grp))
        mc.setAttr('{}.type'.format(self._main_grp), 0)

    def connect_main_controls(self):
        """
        Function that connects main controls
        """

        assert self._main_ctrl and mc.objExists(self._main_ctrl.node)
        assert self._root_ctrl and mc.objExists(self._root_ctrl.node)
        assert self._proxy_asset_grp and mc.objExists(self._proxy_asset_grp)
        assert self._hires_asset_grp and mc.objExists(self._hires_asset_grp)

        mc.parent(self._main_ctrl.offset, self._root_ctrl.node)
        mc.parent(self._root_ctrl.offset, self._ctrl_grp)

        self._main_constraints.append(mc.parentConstraint(self._main_ctrl.node, self._proxy_asset_grp, mo=False))
        self._main_constraints.append(mc.scaleConstraint(self._main_ctrl.node, self._proxy_asset_grp, mo=False))
        self._main_constraints.append(mc.parentConstraint(self._main_ctrl.node, self._hires_asset_grp, mo=False))
        self._main_constraints.append(mc.scaleConstraint(self._main_ctrl.node, self._hires_asset_grp, mo=False))

    def import_model(self):
        """
        Function that import latest working file of the asset model
        """
        if not tp.is_maya():
            tp.logger.warning('Import model functionality is only available in Maya')
            return

        assert self._asset

        track = scene.TrackNodes()
        track.load('transform')
        self._asset.import_model_file(status='working')
        mc.refresh()
        imported_objs = track.get_delta()
        self._geo['model'] = imported_objs
        mc.select(imported_objs)
        mc.viewFit(animate=True)
        mc.select(clear=True)

    def import_proxy(self):
        """
        Function that imports latest working file of the asset proxy model
        """

        if not tp.is_maya():
            tp.logger.warning('Import model functionality is only available in Maya')
            return

        assert self._asset

        track = scene.TrackNodes()
        track.load('transform')
        self._asset.import_proxy_file()
        mc.refresh()
        imported_objs = track.get_delta()
        self._geo['proxy'] = imported_objs
        mc.select(imported_objs)
        mc.viewFit(animate=True)
        mc.select(clear=True)

    def import_builder(self):
        """
        Function that imports in the scene the builder file
        """

        if not tp.is_maya():
            tp.logger.warning('Import model functionality is only available in Maya')
            return

        assert self._asset

        track = scene.TrackNodes()
        track.load('transform')
        self._asset.import_builder_file()
        mc.refresh()
        imported_objs = track.get_delta()
        mc.select(imported_objs)
        mc.viewFit(animate=True)
        mc.select(clear=True)

    def clean_model_group(self):
        """
        Function that clean model group contents
        """

        assert self._hires_asset_grp and tp.Dcc.object_exists(self._hires_asset_grp)

        model_grp = '{}_MODEL'.format(self._asset.name)
        if not tp.Dcc.object_exists(model_grp):
            tp.logger.warning('Model Group with name {} does not exists!'.format(model_grp))
            return

        children = tp.Dcc.list_children(model_grp, full_path=True, all_hierarchy=False, children_type='transform')
        for child in children:
            tp.Dcc.set_parent(child, self._hires_asset_grp)

        tp.Dcc.delete_object(model_grp)

    def clean_proxy_group(self):
        """
        Function that clean proxy model group contents
        """

        assert self._proxy_asset_grp and tp.Dcc.object_exists(self._proxy_asset_grp)

        proxy_grp = '{}_PROXY'.format(self._asset.name)
        if not tp.Dcc.object_exists(proxy_grp):
            tp.logger.warning('Proxy Model Group with name {} does not exists!'.format(proxy_grp))
            return

        children = tp.Dcc.list_children(proxy_grp, full_path=True, all_hierarchy=False, children_type='transform')
        for child in children:
            tp.Dcc.set_parent(child, self._proxy_asset_grp)

        tp.Dcc.delete_object(proxy_grp)

    def setup(self):
        """
        This function MUST be override in specific rigs
        Use this function to create custom rig code
        """

        builder_grp = '{}_BUILDER'.format(self._asset.name)
        if not tp.Dcc.object_exists(builder_grp):
            tp.logger.warning('Builder Group with name {} does not exists!'.format(builder_grp))
            return

        self._builder_grp = builder_grp
        self._builder_locators = tp.Dcc.list_children(builder_grp, full_path=False, children_type='transform')

    def finish(self):
        """
        Function that is called before ending rig setup
        """

        if self._builder_grp and mc.objExists(self._builder_grp):
            mc.delete(self._builder_grp)

        utils.lock_all_transforms(self._rig_grp)
        utils.lock_all_transforms(self._proxy_grp)
        utils.lock_all_transforms(self._hires_grp)
        utils.lock_all_transforms(self._ctrl_grp)
        utils.lock_all_transforms(self._extra_grp)
        utils.lock_all_transforms(self._joint_proxy_grp, lock_visibility=True)
        utils.lock_all_transforms(self._mesh_proxy_grp)
        utils.lock_all_transforms(self._proxy_asset_grp)
        utils.lock_all_transforms(self._joint_hires_grp, lock_visibility=True)
        utils.lock_all_transforms(self._mesh_hires_grp)
        utils.lock_all_transforms(self._hires_asset_grp)
        utils.lock_all_transforms(self._main_grp)

        self._setup_tag()

    def _setup_tag(self):
        """
        Internal function used to setup tag attribute in the rig
        """
        pass
        valid_obj = None
        if mc.objExists(self._asset_name):
            objs = tp.Dcc.list_nodes(node_name=self._asset.name)
            for obj in objs:
                parent = tp.Dcc.node_parent(obj)
                if parent is None:
                    valid_obj = obj
            if not valid_obj:
                mc.error(
                    'Main group is not valid. Please change it manually to {}'.format(self._asset.name))
                return False

        # Check if main group has a valid tag node connected
        valid_tag_data = False
        main_group_connections = tp.Dcc.list_source_destination_connections(valid_obj)
        for connection in main_group_connections:
            attrs = tp.Dcc.list_user_attributes(connection)
            if attrs and type(attrs) == list:
                for attr in attrs:
                    if attr == 'tag_type':
                        valid_tag_data = True
                        break

        if not valid_tag_data:
            mc.warning('Main group has not a valid tag data node connected to it. Creating it ...')
            try:
                tp.Dcc.select_object(valid_obj)
                tagger.SolsticeTagger.create_new_tag_data_node_for_current_selection(self._asset.category)
                tp.Dcc.clear_selection()
                valid_tag_data = False
                main_group_connections = tp.Dcc.list_source_destination_connections(valid_obj)
                for connection in main_group_connections:
                    attrs = tp.Dcc.list_user_attributes(connection)
                    if attrs and type(attrs) == list:
                        for attr in attrs:
                            if attr == 'tag_type':
                                valid_tag_data = True
                if not valid_tag_data:
                    mc.error(
                        'Impossible to create tag data node. Please contact TD team to fix this ...')
                    return False
            except Exception as e:
                mc.error('Impossible to create tag data node. Please contact TD team to fix this ...')
                mc.error(str(e))
                return False

        tag_data_node = tagger.SolsticeTagger.get_tag_data_node_from_curr_sel(new_selection=valid_obj)
        if not tag_data_node or not mc.objExists(tag_data_node):
            mc.error('Impossible to get tag data of current selection: {}!'.format(tag_data_node))
            return False

        # Connect proxy group to tag data node
        valid_connection = tagger.HighProxyEditor.update_proxy_group(tag_data=tag_data_node)
        if not valid_connection:
            mc.error(
                'Error while connecting Proxy Group to tag data node!  Check Maya editor for more info about the error!')
            return False

        # Connect hires group to tag data node
        valid_connection = tagger.HighProxyEditor.update_hires_group(tag_data=tag_data_node)
        if not valid_connection:
            mc.error(
                'Error while connecting hires group to tag data node! Check Maya editor for more info about the error!')
            return False

        # Getting shaders info data
        shaders_file = shaderlibrary.ShaderLibrary.get_asset_shader_file_path(asset=self._asset)
        if not os.path.exists(shaders_file):
            mc.error(
                'Shaders JSON file for asset {0} does not exists: {1}'.format(self._asset.name, shaders_file))
            return False

        with open(shaders_file) as f:
            shader_data = json.load(f)
        if shader_data is None:
            mc.error(
                'Shaders JSON file for asset {0} is not valid: {1}'.format(self._asset.name, shaders_file))
            return False

        hires_grp = None
        hires_grp_name = '{}_hires_grp'.format(self._asset.name)
        children = tp.Dcc.list_relatives(node=valid_obj, all_hierarchy=True, full_path=True,
                                         relative_type='transform')
        if children:
            for child in children:
                child_name = child.split('|')[-1]
                if child_name == hires_grp_name:
                    hires_children = tp.Dcc.list_relatives(node=child_name, all_hierarchy=True,
                                                           relative_type='transform')
                    if len(hires_children) > 0:
                        if hires_grp is None:
                            hires_grp = child
                        else:
                            mc.error('Multiple Hires groups in the file. Please check it!')
                            return False
        if not hires_grp:
            mc.error('No hires group found ...')
            return False
        hires_meshes = tp.Dcc.list_relatives(node=hires_grp, all_hierarchy=True, full_path=True,
                                             relative_type='transform')

        # Checking if shader data is valid
        check_meshes = dict()
        for shading_mesh, shading_group in shader_data.items():
            shading_name = shading_mesh.split('|')[-1]
            check_meshes[shading_mesh] = False
            for model_mesh in hires_meshes:
                mesh_name = model_mesh.split('|')[-1]
                if shading_name == mesh_name:
                    check_meshes[shading_mesh] = True

        valid_meshes = True
        for mesh_name, mesh_check in check_meshes.items():
            if mesh_check is False:
                mc.error('Mesh {} not found in both model and shading file ...'.format(mesh_name))
                valid_meshes = False
        if not valid_meshes:
            mc.error('Some shading meshes and model hires meshes are missed. Please contact TD!')
            return False

        # Create if necessary shaders attribute in model tag data node
        if not tag_data_node or not mc.objExists(tag_data_node):
            mc.error('Tag data does not exists in the current scene!'.format(tag_data_node))
            return False

        attr_exists = tp.Dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
        if attr_exists:
            tp.Dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')
        else:
            tp.Dcc.add_string_attribute(node=tag_data_node, attribute_name='shaders')
            attr_exists = tp.Dcc.attribute_exists(node=tag_data_node, attribute_name='shaders')
            if not attr_exists:
                mc.error('No Shaders attribute found on model tag data node: {}'.format(tag_data_node))
                return False

        tp.Dcc.unlock_attribute(node=tag_data_node, attribute_name='shaders')
        tp.Dcc.set_string_attribute_value(node=tag_data_node, attribute_name='shaders',
                                          attribute_value=shader_data)
        tp.Dcc.lock_attribute(node=tag_data_node, attribute_name='shaders')

        return True

    def _generate_input_data_structure(self):
        pass
