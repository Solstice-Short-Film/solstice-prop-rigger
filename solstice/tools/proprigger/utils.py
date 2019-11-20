import maya.cmds as mc


def lock_all_transforms(node, lock_visibility=None):
    lock_visibility = lock_visibility or False

    for trn in "trs":
        for a in "xyz":
            mc.setAttr("{}.{}{}".format(node, trn, a), lock=True)

    if lock_visibility:
        mc.setAttr("{}.v".format(node), lock=True)
