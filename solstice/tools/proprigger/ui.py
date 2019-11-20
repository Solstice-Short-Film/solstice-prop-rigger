from functools import partial

import maya.cmds as mc
from . import prop


def run_ui():
    window_name = "PropBaseRigUI"
    if mc.window(window_name, exists=True):
        mc.deleteUI(window_name, window=True)
    window = mc.window(window_name, title="PropBaseRig", widthHeight=(250, 90), sizeable=False)
    main_col = mc.columnLayout(adjustableColumn=True)
    base_lay = mc.rowColumnLayout(numberOfColumns=2, parent=main_col, adjustableColumn=True,
                                  columnWidth=[(1, 50), (2, 200)], columnAlign=[(1, "left")])
    mc.text("AssetName:", parent=base_lay)
    name_txf = mc.textField(placeholderText="S_PRP_01_shovel", parent=base_lay)
    mc.text("Model:", parent=base_lay)
    model_txf = mc.textField(placeholderText="S_PRP_01_shovel_MODEL", parent=base_lay)
    mc.text("Proxy:", parent=base_lay)
    proxy_txf = mc.textField(placeholderText="S_PRP_01_shovel_PROXY", parent=base_lay)
    mc.text("Builder:", parent=base_lay)
    builder_txf = mc.textField(placeholderText="S_PRP_01_shovel_BUILDER", parent=base_lay)
    mc.button(label='Execute', parent=main_col, command=partial(run_logic, name_txf, model_txf, proxy_txf, builder_txf))
    mc.showWindow(window)


def run_logic(name_txf, model_txf, proxy_txf, builder_txf, *args):
    # query data
    name = mc.textField(name_txf, q=True, text=True)
    model_grp = mc.textField(model_txf, q=True, text=True)
    proxy_grp = mc.textField(proxy_txf, q=True, text=True)
    builder_grp = mc.textField(builder_txf, q=True, text=True)

    # check
    if model_grp:
        assert mc.objExists(model_grp), "object does not exist"
    if proxy_grp:
        assert mc.objExists(model_grp), "object does not exist"
    if builder_grp:
        assert mc.objExists(model_grp), "object does not exist"

    prop_autorig = prop.PropRig(
        asset_name=name,
        import_scenes=False,
        model_grp=model_grp,
        proxy_grp=proxy_grp,
        builder_grp=builder_grp
    )
    prop_autorig.build()


run_ui()
