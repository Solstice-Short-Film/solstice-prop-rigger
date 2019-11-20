import maya.cmds as cmds


class TagDefinitions(object):
    SCENE_SELECTION_NAME = 'scene'
    TAG_TYPE_ATTRIBUTE_NAME = 'tag_type'
    TAG_DATA_ATTRIBUTE_NAME = 'tag_data'
    NODE_ATTRIBUTE_NAME = 'node'
    TAG_DATA_NODE_NAME = 'tag_data'
    TAG_DATA_SCENE_NAME = 'tag_data_scene'


def add_string_attribute(node, attribute_name, keyable=False):
    return cmds.addAttr(node, ln=attribute_name, dt='string', k=keyable)


def set_string_attribute_value(node, attribute_name, attribute_value):
    return cmds.setAttr('{}.{}'.format(node, attribute_name), str(attribute_value), type='string')


def add_message_attribute(node, attribute_name, keyable=False):
    return cmds.addAttr(node, ln=attribute_name, at='message', k=keyable)


def unkeyable_attribute(node, attribute_name):
    return cmds.setAttr('{}.{}'.format(node, attribute_name), keyable=False)


def hide_attribute(node, attribute_name):
    return cmds.setAttr('{}.{}'.format(node, attribute_name), channelBox=False)


def lock_attribute(node, attribute_name):
    return cmds.setAttr('{}.{}'.format(node, attribute_name), lock=True)


def unlock_attribute(node, attribute_name):
    return cmds.setAttr('{}.{}'.format(node, attribute_name), lock=False)


def attribute_exists(node, attribute_name):
    return cmds.attributeQuery(attribute_name, node=node, exists=True)


def connect_attribute(source_node, source_attribute, target_node, target_attribute, force=False):
    return cmds.connectAttr('{}.{}'.format(source_node, source_attribute),
                            '{}.{}'.format(target_node, target_attribute), force=force)


def select_object(node, replace_selection=False, **kwargs):
    cmds.select(node, replace=replace_selection, **kwargs)


def create_tag_node():
    current_selection = cmds.ls(sl=True)[0]
    tag_data_node = cmds.createNode('network', n='tag_data')
    add_string_attribute(node=tag_data_node, attribute_name=TagDefinitions.TAG_TYPE_ATTRIBUTE_NAME)
    set_string_attribute_value(node=tag_data_node, attribute_name=TagDefinitions.TAG_TYPE_ATTRIBUTE_NAME,
                               attribute_value='SOLSTICE_TAG')
    unkeyable_attribute(node=tag_data_node, attribute_name=TagDefinitions.TAG_TYPE_ATTRIBUTE_NAME)
    hide_attribute(node=tag_data_node, attribute_name=TagDefinitions.TAG_TYPE_ATTRIBUTE_NAME)
    lock_attribute(node=tag_data_node, attribute_name=TagDefinitions.TAG_TYPE_ATTRIBUTE_NAME)
    add_message_attribute(node=tag_data_node, attribute_name=TagDefinitions.NODE_ATTRIBUTE_NAME)
    print(current_selection)
    if not attribute_exists(node=current_selection, attribute_name=TagDefinitions.TAG_DATA_ATTRIBUTE_NAME):
        add_message_attribute(node=current_selection, attribute_name=TagDefinitions.TAG_DATA_ATTRIBUTE_NAME)
    unlock_attribute(node=current_selection, attribute_name=TagDefinitions.TAG_DATA_ATTRIBUTE_NAME)
    unlock_attribute(node=tag_data_node, attribute_name=TagDefinitions.NODE_ATTRIBUTE_NAME)
    connect_attribute(tag_data_node, TagDefinitions.NODE_ATTRIBUTE_NAME, current_selection,
                      TagDefinitions.TAG_DATA_ATTRIBUTE_NAME)
    lock_attribute(node=current_selection, attribute_name=TagDefinitions.TAG_DATA_ATTRIBUTE_NAME)
    lock_attribute(node=tag_data_node, attribute_name=TagDefinitions.NODE_ATTRIBUTE_NAME)
    select_object(tag_data_node)
